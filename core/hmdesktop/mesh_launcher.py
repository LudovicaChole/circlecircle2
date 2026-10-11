"""Run each mesh job in a private directory using a hidden, bounded process."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from .mesh_settings import MeshSettings


def find_hwx():
    configured = os.environ.get('CIRCLECIRCLE_HWX_EXE')
    candidates = [Path(configured)] if configured else [
        Path(os.environ.get('ProgramFiles', 'C:/Program Files'))/'Altair/2026/hwdesktop/hwx/bin/win64/runhwx.exe',
        Path('D:/Program Files/Altair/2026/hwdesktop/hwx/bin/win64/runhwx.exe')]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError('HyperMesh 2026 runhwx.exe not found. Set CIRCLECIRCLE_HWX_EXE to its full path.')


def mesh_file(source, catalog, settings=None):
    source = Path(source).resolve(strict=True)
    settings = settings or MeshSettings()
    exe = find_hwx()
    job = Path(tempfile.mkdtemp(prefix=source.stem+'_hwx_', dir=source.parent))
    config = dict(source=str(source), catalog=str(Path(catalog).resolve()), job=str(job),
                  settings=settings.to_dict(), output=str(job/(source.stem+'_meshed.hm')))
    config_path = job/'job.json'
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    root = Path(__file__).resolve().parents[2]
    script = job/'run_mesh.py'
    script.write_text(
        'import sys, os, json, traceback\nfrom pathlib import Path\n'
        'job = Path('+repr(str(job))+')\n'
        '(job/"worker.tmp").write_text(str(os.getpid()))\n'
        '(job/"worker.tmp").replace(job/"worker.pid")\n'
        'sys.path.insert(0, '+repr(str(root))+')\n'
        'try:\n'
        '    from core.hmdesktop.mesh_pipeline import run_job\n'
        '    run_job('+repr(str(config_path))+')\n'
        'except Exception as error:\n'
        '    result = dict(success=False, error=str(error), traceback=traceback.format_exc())\n'
        '    (job/"bootstrap.tmp").write_text(json.dumps(result), encoding="utf-8")\n'
        '    (job/"bootstrap.tmp").replace(job/"result.json")\n'
        '    import hw\n    hw.evalTcl("*quit 1")\n', encoding='utf-8')
    command = [str(exe), '-client', 'HyperWorksDesktop', '-plugin', 'HyperworksGeneral',
               '-profile', 'HyperworksGeneral', '-l', 'en', '-startwith', 'HyperMesh', '-b', '-f', str(script)]
    from utilities.logger import logger
    logger.info(f'hwx_mesh started: {source}; logs: {job}')
    with (job/'process.log').open('w', encoding='utf-8') as stream:
        process = subprocess.Popen(command, cwd=job, stdout=stream, stderr=subprocess.STDOUT,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        # runhwx is a launcher and can exit 0 before its hwx child finishes.
        # The unique per-job report, not launcher exit 0, proves completion.
        result_path = job/'result.json'
        started = time.monotonic()
        deadline = started+settings.timeout_seconds
        worker = None
        from .process_guard import WorkerProcess
        try:
            while not result_path.is_file() and time.monotonic() < deadline:
                if worker is None and (job/'worker.pid').is_file():
                    worker = WorkerProcess(int((job/'worker.pid').read_text()))
                code = process.poll()
                if code not in (None, 0) or (worker and worker.exited()):
                    break
                if worker is None and time.monotonic()-started > 120:
                    break
                time.sleep(0.5)
            if not result_path.is_file() and worker:
                worker.terminate()
            if result_path.is_file() and worker:
                exit_deadline = time.monotonic()+30
                while not worker.exited() and time.monotonic() < exit_deadline:
                    time.sleep(0.2)
                if not worker.exited():
                    raise RuntimeError(f'HyperMesh wrote a report but did not exit; intermediate files retained: {job}')
        finally:
            if worker:
                worker.close()
        code = process.poll() or 0
    if not result_path.is_file():
        raise RuntimeError(f'HyperMesh failed or timed out ({code}) without a completion report; inspect {job}/process.log')
    result = json.loads(result_path.read_text(encoding='utf-8'))
    result['log'] = str(job/'hwx_mesh.log')
    from .job_reports import clean_job
    if code or not result.get('success'):
        with (job/'hwx_mesh.log').open('a', encoding='utf-8') as stream:
            stream.write('\nJOB FAILED: '+result.get('error', 'HyperMesh process failed')+'\n')
            stream.write('failed_debug.hm is diagnostic only; it is not an accepted mesh.\n')
            stream.write(result.get('traceback', '')+'\n')
            process_log = job/'process.log'
            if process_log.exists():
                stream.write('\nNative process output:\n'+process_log.read_text(encoding='utf-8', errors='replace'))
        clean_job(job, 'failed_debug.hm')
        raise RuntimeError(f'{result.get("error", "HyperMesh process failed")}; logs: {job}')
    if not Path(result['output']).is_file():
        raise RuntimeError(f'HyperMesh did not write its output model; logs: {job}')
    clean_job(job, Path(result['output']).name)
    return result
