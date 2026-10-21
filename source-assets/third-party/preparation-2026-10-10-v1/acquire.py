"""Acquire only chosen public, free official asset downloads. No login/payment flow.

The original files are never overwritten. Extraction rejects paths outside its root,
duplicate paths, symlinks, and unexpectedly large uncompressed archives.
"""
from pathlib import Path, PurePosixPath
import hashlib
import html
import http.cookiejar
import json
import re
import stat
import sys
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'acquisition-manifest.json'
UA = 'Mozilla/5.0 (asset acquisition; local prototype preparation)'
OP = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
records = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else []

def req(url, data=None, referer=None):
    headers = {'User-Agent': UA}
    if referer:
        headers['Referer'] = referer
    if data is not None:
        headers['X-Requested-With'] = 'XMLHttpRequest'
        data = urllib.parse.urlencode(data).encode()
    return OP.open(urllib.request.Request(url, data=data, headers=headers), timeout=90)

def page(url):
    with req(url) as response:
        return response.read().decode('utf-8', 'replace')

def persist():
    MANIFEST.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def save_page(folder, text, filename='official-page.html'):
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / filename
    if not target.exists():
        # These are anonymous public pages. Remove volatile anti-CSRF nonce.
        text = re.sub(r'(<meta name="csrf_token" value=")[^"]+', r'\1REDACTED_ANONYMOUS_NONCE', text)
        target.write_text(text, encoding='utf-8')

def download(url, path):
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite {path}')
    partial = path.with_suffix(path.suffix + '.partial')
    if partial.exists():
        raise FileExistsError(f'Existing unfinished download {partial}')
    count = 0
    digest = hashlib.sha256()
    with req(url) as response, partial.open('xb') as out:
        ctype = response.headers.get('Content-Type', '')
        if 'text/html' in ctype:
            raise ValueError('Download returned HTML instead of an asset; no bypass attempted')
        while chunk := response.read(1024 * 1024):
            count += len(chunk)
            if count > 250 * 1024 * 1024:
                raise ValueError('Per-file download limit exceeded')
            digest.update(chunk)
            out.write(chunk)
    partial.replace(path)
    return count, digest.hexdigest()

def extract_safe(archive, target):
    root = target.resolve()
    target.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as z:
        seen = set()
        if sum(i.file_size for i in z.infolist()) > 700 * 1024 * 1024:
            raise ValueError('Archive uncompressed limit exceeded')
        for item in z.infolist():
            name = item.filename.replace('\\', '/')
            parts = PurePosixPath(name).parts
            if name.startswith('/') or any(p in ('..', '') or ':' in p for p in parts):
                raise ValueError(f'Unsafe archive path: {name}')
            resolved = (target / name).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError(f'Path outside extraction directory: {name}')
            key = str(resolved).casefold()
            if key in seen:
                raise ValueError(f'Duplicate archive path: {name}')
            seen.add(key)
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f'Symlink rejected: {name}')
        z.extractall(target)

def audit_zip(rec, archive, extracted):
    entries = []
    with zipfile.ZipFile(archive) as z:
        for i in z.infolist():
            if not i.is_dir():
                entries.append({'path': i.filename, 'bytes': i.file_size})
    (archive.parent / 'archive-file-list.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    files = [p for p in extracted.rglob('*') if p.is_file()]
    counts = {}
    for p in files:
        ext = p.suffix.lower() or '(none)'
        counts[ext] = counts.get(ext, 0) + 1
    licenses = [str(p.relative_to(extracted)) for p in files if re.search(r'licen[cs]e|copying', p.name, re.I)]
    rec.update({'zip_entries':len(entries), 'uncompressed_bytes':sum(i['bytes'] for i in entries), 'formats':counts, 'license_entries':licenses,'status':'downloaded_extracted_license_pending_import_not_verified'})
    print(json.dumps({'id':rec['id'],'bytes':rec['bytes'],'formats':counts,'licenses':licenses,'extract_path':str(extracted)},ensure_ascii=False),flush=True)

def acquire_kenney(slug):
    identifier = 'kenney-' + slug
    if any(r['id']==identifier and r.get('status','').startswith('downloaded') for r in records):
        print('Already acquired',identifier,flush=True)
        return
    source = 'https://kenney.nl/assets/' + slug
    body = page(source)
    links = re.findall(r"href=['\"]([^'\"]+\.zip)['\"]",body)
    if len(links)!=1:
        raise ValueError(f'Expected one official ZIP link: {identifier}: {len(links)}')
    url=html.unescape(links[0])
    folder=ROOT/identifier
    save_page(folder/'evidence',body)
    archive=folder/Path(urllib.parse.urlparse(url).path).name
    print('Downloading',identifier,flush=True)
    size,digest=download(url,archive)
    extracted=folder/'extracted'
    extract_safe(archive,extracted)
    rec={'id':identifier,'source_page':source,'download_url':url,'archive_path':str(archive),'extract_path':str(extracted),'bytes':size,'sha256':digest,'license':'CC0','date':'2026-10-10','cost_paid':0,'login_used':False}
    audit_zip(rec,archive,extracted)
    records.append(rec)
    persist()

def acquire_itch(creator,slug,filename,identifier):
    if any(r['id']==identifier and r.get('status','').startswith('downloaded') for r in records):
        print('Already acquired',identifier,flush=True)
        return
    source=f'https://{creator}.itch.io/{slug}'
    body=page(source)
    folder=ROOT/identifier
    save_page(folder/'evidence',body)
    purchase=page(source+'/purchase')
    csrf=re.search(r'<meta name="csrf_token" value="([^"]+)"',purchase).group(1)
    # Exact public "No thanks, just take me to downloads" endpoint from itch checkout JS.
    with req(source+'/download_url',{'csrf_token':csrf},source+'/purchase') as response:
        result=json.load(response)
    download_page=page(result['url'])
    uploads=re.findall(r'data-upload_id="(\d+)".*?<strong[^>]*class="name"[^>]*>(.*?)</strong>',download_page,re.S)
    matches=[uid for uid,name in uploads if html.unescape(name)==filename]
    if len(matches)!=1:
        raise ValueError(f'Chosen free file not listed on anonymous download page: {filename}; visible names {[n for _,n in uploads]}')
    uid=matches[0]
    csrf=re.search(r'<meta name="csrf_token" value="([^"]+)"',download_page).group(1)
    endpoint=source+'/file/'+uid+'?source=game_download'
    with req(endpoint,{'csrf_token':csrf},result['url']) as response:
        result=json.load(response)
    if not result.get('url'):
        raise ValueError('No direct download URL; login/payment/quarantine not bypassed')
    archive=folder/filename
    print('Downloading',identifier,flush=True)
    size,digest=download(result['url'],archive)
    extracted=folder/'extracted'
    extract_safe(archive,extracted)
    rec={'id':identifier,'source_page':source,'download_endpoint':endpoint,'itch_upload_id':uid,'download_cdn_host':urllib.parse.urlparse(result['url']).hostname,'ephemeral_signed_download_url':'not retained; regenerate through public anonymous download page','selected_file':filename,'archive_path':str(archive),'extract_path':str(extracted),'bytes':size,'sha256':digest,'license':'CC0 (official asset page; package license to be checked)','date':'2026-10-10','cost_paid':0,'login_used':False}
    audit_zip(rec,archive,extracted)
    records.append(rec)
    persist()

if __name__=='__main__':
    task=sys.argv[1]
    if task=='kenney':
        for slug in ['modular-dungeon-kit','mini-dungeon','animated-characters-protagonists','rpg-audio']:
            acquire_kenney(slug)
    elif task=='animation':
        acquire_itch('quaternius','universal-animation-library-2','Universal Animation Library 2[Standard].zip','quaternius-universal-animation-library-2-standard')
    elif task=='music':
        acquire_itch('tallbeard','music-loop-bundle','music-loop-bundle-2026-q3.zip','abstraction-music-loop-bundle-2026-q3')
    else:
        raise ValueError(task)
