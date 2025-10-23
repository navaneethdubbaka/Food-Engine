import os
import sqlite3
import time
import argparse
from datetime import datetime
from urllib.parse import quote_plus

import requests
import imghdr


DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'restaurant.db')
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')


def ensure_directories():

    os.makedirs(IMAGES_DIR, exist_ok=True)


def slugify(value):

    value = value.strip().lower()
    safe_chars = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    out = []
    for ch in value:
        if ch in safe_chars:
            out.append(ch)
        elif ch.isspace() or ch in ['/', '\\', ',', '.', '&', '+', '#', '(', ')', '[', ']', '{', '}', ':', ';', '\'', '"']:
            out.append('-')
        else:
            out.append('-')
    slug = '-'.join(part for part in ''.join(out).split('-') if part)
    return slug or datetime.now().strftime('%Y%m%d%H%M%S')


def _http_get(url, timeout):

    headers = {
        'User-Agent': 'FoodEngine-ImageFetcher/1.0 (+https://local.app)'
    }
    response = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers)
    response.raise_for_status()
    return response


def _clean_query(raw: str) -> str:

    # Reduce noisy tokens and parentheses content to increase hit-rate
    q = raw or ''
    q = q.replace('(', ' ').replace(')', ' ')
    q = ' '.join(part for part in q.split() if part.lower() not in {'non-veg', 'veg', 'special', 'bone', 'boneless'})
    q = q.strip()
    return q or raw


def _fetch_from_wikipedia(query: str, width: int, height: int, timeout: int):

    # Use Wikipedia API to get a page thumbnail; no API key required
    cleaned = _clean_query(query)
    api = (
        'https://en.wikipedia.org/w/api.php?'
        'action=query&format=json&prop=pageimages&piprop=thumbnail&'
        f'pithumbsize={max(width, height)}&redirects=1&'
        f'generator=search&gsrsearch={quote_plus(cleaned)}&gsrlimit=1'
    )
    try:
        resp = _http_get(api, timeout)
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            raise ValueError('No pages')
        page = next(iter(pages.values()))
        thumb = page.get('thumbnail', {})
        src = thumb.get('source')
        if not src:
            raise ValueError('No thumbnail in page')
        img_resp = _http_get(src, timeout)
        ct = (img_resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        if not ct.startswith('image/'):
            raise ValueError(f'Wikipedia returned non-image {ct}')
        return img_resp.content, ct
    except Exception as e:
        raise e


def fetch_image_for_query(query, width=640, height=480, timeout=15, retries=3, provider_order=None):

    if provider_order is None:
        provider_order = ['wikipedia', 'unsplash', 'loremflickr']

    last_error = None
    encoded_query = quote_plus(query)

    # Providers
    providers = []
    if 'wikipedia' in provider_order:
        providers.append(lambda: ('wikipedia', None))
    if 'unsplash' in provider_order:
        providers.append(lambda: f"https://source.unsplash.com/{width}x{height}/?{encoded_query}")
    if 'loremflickr' in provider_order:
        # LoremFlickr supports comma-separated tags
        alt_query = encoded_query.replace('+', ',')
        providers.append(lambda: f"https://loremflickr.com/{width}/{height}/{alt_query}")

    for make_url in providers:
        backoff = 0.75
        for attempt in range(1, retries + 1):
            try:
                url_or_provider = make_url()
                if isinstance(url_or_provider, tuple) and url_or_provider[0] == 'wikipedia':
                    # Wikipedia provider uses JSON API
                    return _fetch_from_wikipedia(query, width, height, timeout)
                else:
                    url = url_or_provider
                    resp = _http_get(url, timeout)
                    content_type = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
                    # Ensure we actually got an image
                    if not content_type.startswith('image/'):
                        raise requests.HTTPError(f"Non-image content-type: {content_type}", response=resp)
                    return resp.content, content_type
            except requests.HTTPError as e:
                status = getattr(e.response, 'status_code', None)
                last_error = e
                transient = status in (429, 500, 502, 503, 504)
                if transient and attempt < retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                # Non-transient or out of retries -> try next provider
                break
            except requests.RequestException as e:
                last_error = e
                if attempt < retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                break

    # Fallback to local placeholder if available
    placeholder_path = os.path.join(IMAGES_DIR, 'placeholder.jpg')
    if os.path.exists(placeholder_path):
        with open(placeholder_path, 'rb') as f:
            data = f.read()
            return data, 'image/jpeg'

    # Final fallback: small generated image from placehold.co to avoid failure
    try:
        fallback = _http_get(f"https://placehold.co/{width}x{height}.jpg?text=Food", timeout)
        return fallback.content, 'image/jpeg'
    except Exception:
        if last_error:
            raise last_error
        raise RuntimeError('All providers failed and no placeholder available')


def update_menu_image(conn, item_id, filename):

    cursor = conn.cursor()
    cursor.execute('UPDATE menu SET image=? WHERE id=?', (filename, item_id))
    conn.commit()


def get_menu_items(conn):

    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, image FROM menu ORDER BY category, name')
    return cursor.fetchall()


def download_images(overwrite=False, delay=0.5, only_missing=True):

    ensure_directories()

    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"Database not found at {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        items = get_menu_items(conn)
        total = len(items)
        print(f"Found {total} menu items")

        downloaded = 0
        skipped = 0
        errors = 0

        for item_id, name, category, image in items:
            image_path_on_disk = os.path.join(IMAGES_DIR, image) if image else None
            has_db_image = bool(image)
            file_missing = has_db_image and not os.path.exists(image_path_on_disk)

            needs_download = (
                overwrite or
                (only_missing and (not has_db_image or file_missing)) or
                (not only_missing)
            )
            if not needs_download:
                skipped += 1
                reason = "has image in DB and file exists" if has_db_image and not file_missing else "already processed"
                print(f"[SKIP] {name} -> {reason}")
                continue

            query = f"{name} {category} food"
            base_filename = slugify(name)
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_')}{base_filename}.jpg"
            file_path = os.path.join(IMAGES_DIR, filename)

            try:
                content, content_type = fetch_image_for_query(query)

                # Validate image bytes via imghdr and size
                detected = imghdr.what(None, h=content)
                min_bytes = 2048  # Avoid saving tiny/invalid responses
                if not detected and content_type.startswith('image/'):
                    # Map some content types to imghdr names
                    if content_type.endswith('jpeg'):
                        detected = 'jpeg'
                    elif content_type.endswith('png'):
                        detected = 'png'
                    elif content_type.endswith('gif'):
                        detected = 'gif'

                if not detected or len(content) < min_bytes:
                    raise ValueError(f"Invalid image (type={detected}, size={len(content)} bytes)")

                # Enforce supported formats (jpeg/png/gif). Avoid webp as app disallows it.
                if detected not in ('jpeg', 'png', 'gif'):
                    raise ValueError(f"Unsupported image format: {detected}")

                # Adjust extension based on detected type
                ext = 'jpg' if detected == 'jpeg' else detected
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_')}{base_filename}.{ext}"
                file_path = os.path.join(IMAGES_DIR, filename)

                with open(file_path, 'wb') as f:
                    f.write(content)

                update_menu_image(conn, item_id, filename)
                downloaded += 1
                print(f"[OK] {name} -> {filename} ({detected}, {len(content)} bytes)")
            except Exception as e:
                errors += 1
                print(f"[ERR] {name}: {e}")

            if delay > 0:
                time.sleep(delay)

        print("")
        print(f"Completed. Downloaded: {downloaded}, Skipped: {skipped}, Errors: {errors}")
    finally:
        conn.close()


def main():

    parser = argparse.ArgumentParser(description='Download images for menu items and update database')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing images')
    parser.add_argument('--no-only-missing', action='store_true', help='Process all items, not only those missing images')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between downloads (seconds)')
    args = parser.parse_args()

    only_missing = not args.no_only_missing
    download_images(overwrite=args.overwrite, delay=args.delay, only_missing=only_missing)


if __name__ == '__main__':

    main()


