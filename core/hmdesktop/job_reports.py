"""Readable reports and cleanup restricted to one newly created job directory."""
import logging
from pathlib import Path
import re
import shutil


class MeshLogFormatter(logging.Formatter):
    def format(self, record):
        text = super().format(record)
        return text + '\n'


def format_quality(raw):
    lines = ['MESH QUALITY REPORT', '='*100,
             'Units: mm    |    -- means not evaluated / not applicable', '',
             f'{"#":>3}  {"Criterion":<20} {"Limit":>10} {"Failed %":>10} {"Worst":>10} {"Q.I.":>10}  Worst element IDs',
             '-'*100]
    for line in raw.splitlines():
        match = re.match(r'^\s*(\d+)\s+(.+?)\s{2,}(.*)$', line)
        if match:
            number, name, tail = match.groups()
            values = tail.split()
            # Q.I. can exceed its native column width on a failed mesh.
            # Tokenize values instead of truncating their significant digits.
            fields = (values[:1]+['', '']+values[1:2] if name == '% of trias'
                      else (values[:4]+['']*4)[:4])
            lines.append(f'{number:>3}  {name:<20} '+ ' '.join(f'{v or "--":>10}' for v in fields)
                         + '  ' + (' '.join(values[4:]) or '--'))
        elif '=' in line:
            lines.append(line.strip())
    lines += ['', '='*100, 'Quality values above are reported by HyperMesh; no values are inferred.', '']
    return '\n'.join(lines)


def clean_job(directory, model_name):
    root = Path(directory).resolve(strict=True)
    keep = {'hwx_mesh.log', 'quality.txt', model_name}
    if not (root/'quality.txt').exists():
        (root/'quality.txt').write_text('Mesh quality was not evaluated. See hwx_mesh.log.\n', encoding='utf-8')
    for item in root.iterdir():
        if item.name in keep:
            continue
        resolved = item.resolve()
        if root not in resolved.parents or item.is_symlink():
            raise ValueError(f'Refusing cleanup outside job directory: {item}')
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
