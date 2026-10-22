"""Replace Python's dormant bootstrap wheel, as well as the installed pip.

Run only inside the derived Thunderbird image. No package index is contacted.
"""
import hashlib
from pathlib import Path
import re
import shutil
import sysconfig
import zipfile

PIP_SHA256 = 'fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70'
wheel = Path('/tmp/pip-26.2.2-py3-none-any.whl')
if hashlib.sha256(wheel.read_bytes()).hexdigest() != PIP_SHA256:
    raise RuntimeError('Unexpected pip wheel')
with zipfile.ZipFile(wheel) as archive:
    if archive.testzip() is not None:
        raise RuntimeError('Invalid pip archive')
root = Path(sysconfig.get_path('stdlib')) / 'ensurepip'
bundled = root / '_bundled'
if root.is_symlink() or bundled.is_symlink() or not bundled.is_dir():
    raise RuntimeError('Unexpected ensurepip layout')
source = root / '__init__.py'
original = source.read_text()
updated, count = re.subn(r'(?m)^_PIP_VERSION = [\'"][^\'\"]+[\'\"]$', '_PIP_VERSION = "26.2.2"', original)
if count != 1:
    raise RuntimeError('Unexpected ensurepip version definition')
old_wheels = list(bundled.glob('pip-*.whl'))
if len(old_wheels) != 1 or old_wheels[0].is_symlink():
    raise RuntimeError('Unexpected bundled pip inventory')
shutil.copyfile(wheel, bundled / wheel.name)
source.write_text(updated)
if old_wheels[0].name != wheel.name:
    old_wheels[0].unlink()
print('ensurepip 26.2.2 bootstrap wheel installed')
