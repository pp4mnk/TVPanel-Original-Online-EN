#!/bin/sh
set -eu
cd "$(dirname "$0")"
for dep in python3 yad mpv; do
 command -v "$dep" >/dev/null || { echo "Missing dependency: $dep. Install it using the package manager."; exit 1; }
done
if ! command -v gtkdialog3 >/dev/null && ! command -v gtkdialog >/dev/null; then
 echo 'gtkdialog or gtkdialog3 is missing'; exit 1
fi
[ "$(id -u)" = 0 ] || { echo 'Run this installer as root in EasyOS.'; exit 1; }
mkdir -p /usr/local/lib/tvpanel-online /usr/local/bin /usr/share/applications
cp tvpanel-online.py defaults.json /usr/local/lib/tvpanel-online/
python3 - <<'PY'
import json, pathlib, shutil
root=pathlib.Path('/usr/local/lib/tvpanel-online')
data=json.loads((root/'defaults.json').read_text())
# Preserve the installed original logos in a stable directory.
icons=root/'icons'; icons.mkdir(exist_ok=True)
for c in data:
 p=pathlib.Path(c['icon'])
 if p.is_file():
  target=icons/p.name; shutil.copy2(p,target); c['icon']=str(target)
(root/'defaults.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
wrapper='#!/bin/sh\nexec python3 /usr/local/lib/tvpanel-online/tvpanel-online.py "$@"\n'
launcher=pathlib.Path('/usr/local/bin/tvpanel-online'); launcher.write_text(wrapper); launcher.chmod(0o755)
base=pathlib.Path('/root/noob'); base.mkdir(exist_ok=True)
targets=list(base.rglob('noob128_front_end'))
if not targets: targets=[base/'noob128_front_end']
for target in targets:
 if target.is_symlink():
  target=target.resolve()
 backup=target.with_name(target.name+'.before-online')
 if target.exists() and not backup.exists(): shutil.copy2(target,backup)
 target.write_text(wrapper); target.chmod(0o755)
 print('Panel updated:',target)
pathlib.Path('/usr/share/applications/tvpanel-online.desktop').write_text('[Desktop Entry]\nType=Application\nName=TVPanel\nComment=TV panel with an Internet channel catalogue\nExec=/usr/local/bin/tvpanel-online\nIcon=video-display\nTerminal=false\nCategories=AudioVideo;Video;\n')
PY
if command -v fixmenus >/dev/null; then fixmenus; fi
if command -v update-desktop-database >/dev/null; then update-desktop-database /usr/share/applications || true; fi
echo 'Done. Open your original TVPanel shortcut or run tvpanel-online.'
