"""Build a portable Windows folder. Run with the project's Python environment.

python pack.py            Build (install PyInstaller if needed).
python pack.py --check    Check inputs and show the build plan without installing/building.

PyInstaller onedir reference: https://pyinstaller.org/en/stable/usage.html
"""
import argparse
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PACKAGES = ('core', 'gui', 'utilities', 'net_services')
ISSUER_MODULES = ('gui.license', 'utilities.license_issuer')


def modules(root=ROOT):
    result = []
    for package in PACKAGES:
        for path in sorted((root / package).rglob('*.py')):
            relative = path.relative_to(root)
            if any(part in ('test', 'tests', '__pycache__') for part in relative.parts):
                continue
            parts = list(relative.with_suffix('').parts)
            if parts[-1] == '__init__':
                parts.pop()
            name = '.'.join(parts)
            if name not in ISSUER_MODULES:
                result.append(name)
    return sorted(set(result))


def data_files(root=ROOT):
    result = [(root / 'config/public_key.pem', 'config')]
    for folder in ('help_documentation', 'core'):
        for path in sorted((root / folder).rglob('*')):
            if path.suffix.lower() not in ('.json', '.md', '.txt') or not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in ('test', 'tests', '__pycache__') for part in relative.parts):
                continue
            result.append((path, relative.parent.as_posix()))
    return result


def build_command(build_id, root=ROOT):
    command = [sys.executable, '-m', 'PyInstaller', '--onedir', '--windowed',
               '--name', 'CircleCircle2', '--contents-directory', '_internal',
               '--noupx', '--paths', str(root),
               '--distpath', str(root / 'dist' / build_id),
               '--workpath', str(root / 'build' / build_id / 'work'),
               '--specpath', str(root / 'build' / build_id)]
    for name in ('test', 'gui.tests', *ISSUER_MODULES):
        command += ['--exclude-module', name]
    for name in modules(root):
        command += ['--hidden-import', name]
    for path, destination in data_files(root):
        command += ['--add-data', f'{path}:{destination}']
    return command + [str(root / 'main.py')]


def check_inputs(root=ROOT):
    if root == ROOT:
        from utilities.licensing import ensure_public_key
        ensure_public_key()
    if sys.platform != 'win32':
        raise RuntimeError('Build the Windows application on Windows.')
    missing = [name for name in ('PySide6', 'cryptography', 'numpy', 'torch')
               if importlib.util.find_spec(name) is None]
    if missing:
        raise RuntimeError('Run pack.py with the CircleCircle2 Python environment. Missing packages: '
                           + ', '.join(missing))
    for path in [root / 'main.py', *(item[0] for item in data_files(root))]:
        if not path.is_file():
            raise FileNotFoundError(f'Required application resource is missing: {path}')


def initialize_distribution(folder, root=ROOT):
    # Never copy the developer's profile, licenses, logs, or signing private key.
    config = folder / 'config'
    config.mkdir(parents=True, exist_ok=True)
    from shutil import copyfile
    copyfile(root / 'config' / 'public_key.pem', config / 'public_key.pem')
    if (root / 'Material_Library').is_dir():
        from shutil import copytree
        copytree(root / 'Material_Library', folder / 'Material_Library', dirs_exist_ok=True)
    defaults = ['.inp', '.geo', '.k', '.key', '.pc', '.inc', '.jpg', '.png', '.gif', '.mp4', '.avi']
    (config / 'clear_fea_result.json').write_text(
        json.dumps({'keep_extensions': defaults}, indent=2) + '\n', encoding='utf-8')
    (folder / 'START_HERE.txt').write_text(
        'Run CircleCircle2.exe. Keep the entire folder together when copying it.\n'
        'No Python installation or installer is required on the destination computer.\n'
        'On first launch, use File > Set Work Directory and Setting > License.\n'
        'New log entries go to app.log in the current work directory.\n'
        'For material mapping, keep Material_Library/ABAQUS, Material_Library/Ls_Dyna and Material_Library/PamCrash beside the executable.\n'
        'HyperMesh integration requires a separately installed compatible HyperMesh.\n', encoding='utf-8')


def check_distribution(folder):
    """Reject accidentally copied issuer files or PEM private keys before delivery."""
    forbidden = {'license.py', 'license.pyc', 'license_issuer.py',
                 'license_issuer.pyc', 'private_key.pem'}
    for path in folder.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(folder)
        if path.name.lower() in forbidden or 'license_issuer' in relative.parts:
            raise RuntimeError(f'Issuer-only file found in distribution: {relative}')
        if path.suffix.lower() == '.pem' and b'PRIVATE KEY-----' in path.read_bytes():
            raise RuntimeError(f'Private key found in distribution: {relative}')
    if not (folder / 'config' / 'public_key.pem').is_file():
        raise RuntimeError('The distribution is missing the license verification public key.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate inputs without building or installing.')
    args = parser.parse_args(argv)
    check_inputs()
    build_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    command = build_command(build_id)
    if args.check:
        print(f'Inputs OK: {len(modules())} modules; {len(data_files())} resource files.')
        print('Layout: dist/<build time>/CircleCircle2/CircleCircle2.exe + _internal/ + config/')
        print('Build tool installed:', importlib.util.find_spec('PyInstaller') is not None)
        print('Issuer modules excluded: ' + ', '.join(ISSUER_MODULES))
        print('Only the public key is included; the signing private key stays in the source project.')
        print('No build or installation was performed.')
        return 0
    if importlib.util.find_spec('PyInstaller') is None:
        print('Installing the PyInstaller build tool into the current Python environment...')
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyInstaller>=6,<7'], check=True)
    (ROOT / 'build' / build_id).mkdir(parents=True, exist_ok=False)
    print('Building the portable application. This can take several minutes with PyTorch.')
    subprocess.run(command, cwd=ROOT, check=True)
    folder = ROOT / 'dist' / build_id / 'CircleCircle2'
    if not (folder / 'CircleCircle2.exe').is_file():
        raise RuntimeError('The build did not produce CircleCircle2.exe.')
    initialize_distribution(folder)
    check_distribution(folder)
    print(f'Build complete. Copy this entire folder:\n{folder}')
    return 0


if __name__ == '__main__':
    try:
        result = main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        result = 1
    if len(sys.argv) == 1 and sys.stdin is not None and sys.stdin.isatty():
        input('Press Enter to close...')
    raise SystemExit(result)
