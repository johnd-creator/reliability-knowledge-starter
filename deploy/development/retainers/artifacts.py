"""Numeric-only emitted-map checks in private synthetic copies; no source output."""
import base64,json,re
from pathlib import Path

def inspect(root):
    root=Path(root)
    if not root.is_absolute() or root.resolve().as_posix().startswith('/tmp/nadi-fix05-private/') is False or root.is_symlink():raise ValueError('Private artifact required')
    server=root/'runs/frontend/reliability-cockpit/web/.next-primary-dev/server'
    files=[server/'vendor-chunks/next.js',*server.glob('app/**/page.js')]
    rows=[]
    for file in files:
        if file.is_symlink() or not file.resolve().as_posix().startswith(root.resolve().as_posix()+'/'):raise ValueError('Private artifact escape')
        if not file.exists():continue
        if file.stat().st_size>32*1048576:raise ValueError('Artifact budget')
        body=file.read_text();maps=embedded=0
        for match in re.finditer(r'sourceMappingURL=data:application/json[^,]*,([A-Za-z0-9+/=]+)',body):
            maps+=1
            try:data=json.loads(base64.b64decode(match.group(1)))
            except (ValueError,UnicodeDecodeError):continue
            if data.get('sourcesContent'):
                embedded+=1
        rows.append(dict(kind='vendor-next' if 'vendor-chunks' in str(file) else 'application-page',bytes=file.stat().st_size,eval_text_occurrences=body.count('eval('),map_comments=maps,maps_with_embedded_source=embedded))
    return rows
if __name__=='__main__':
    import sys
    print(json.dumps(inspect(sys.argv[1]),indent=2))
