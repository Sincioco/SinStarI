"""Refresh changed local asset versions without rebuilding or replacing authored HTML."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import html
import re

ROOT = Path(__file__).resolve().parents[1]

def main():
    hashes = {}
    def replace(match):
        value = html.unescape(match.group(2))
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path.startswith('asset/'):
            return match.group(0)
        file = ROOT / unquote(url.path)
        if not file.is_file():
            return match.group(0)
        if file not in hashes:
            hashes[file] = hashlib.sha256(file.read_bytes()).hexdigest()[:10]
        return match.group(1) + '="' + html.escape(url.path + '?v=' + hashes[file], quote=True) + '"'
    for page in ROOT.glob('*.html'):
        source = page.read_text(encoding='utf-8')
        updated = re.sub(r'(src|href|poster|data-src)="([^"]*\?v=[^"]*)"', replace, source)
        if source != updated:
            page.write_text(updated, encoding='utf-8')
    print(f'Refreshed versions for {len(hashes)} local assets; authored HTML preserved.')

if __name__ == '__main__':
    main()
