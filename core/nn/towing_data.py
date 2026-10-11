"""Independent mesh-only training reader. IDs are always scoped to a file."""
from dataclasses import dataclass
from pathlib import Path
import re
import hashlib
import os
import tempfile
import numpy as np
from core.fea.dataframe import DataFrame
from core.fea.include_reader import load_deck


@dataclass
class PartCloud:
    source: str
    pid: int
    points: np.ndarray
    mesh: object
    target: bool | None = None

    @property
    def key(self):
        return f'{self.source}::{self.pid}'


def read_k(path, deck=None):
    from core.fea.lsdyna.parser.node_parser import NodeParser
    from core.fea.lsdyna.parser.element_shell_parser import ElementShellParser
    from core.fea.lsdyna.parser.element_solid_parser import ElementSolidParser
    from core.fea.lsdyna.parser.parameter_parser import ParameterParser
    from core.fea.mesh_data import rebuild_indices
    df = DataFrame()
    deck = deck if deck is not None else load_deck(path, 'lsdyna')
    parsers = {'*PARAMETER': ParameterParser(), '*NODE': NodeParser(),
               '*ELEMENT_SHELL': ElementShellParser(), '*ELEMENT_SOLID': ElementSolidParser()}
    for parser in parsers.values():
        parser.dataframe = df
    # Nodes precede elements logically even when the source orders blocks otherwise.
    for accepted in ({'*PARAMETER'}, {'*NODE'}, {'*ELEMENT_SHELL', '*ELEMENT_SOLID'}):
        parser = None
        for record in deck.lines:
            text = record.text.strip()
            if text.startswith('*'):
                if parser is not None and parser.line_number:
                    raise ValueError(f'{record.location}: incomplete mesh record')
                key = text.split()[0].upper()
                if key.startswith(('*NODE_', '*ELEMENT_SHELL_', '*ELEMENT_SOLID_')):
                    raise ValueError(f'{record.location}: training reader does not support {key}')
                parser = parsers.get(key) if key in accepted else None
            elif text and not text.startswith('$') and parser is not None:
                parser.parse(record.text, '16.0')
        if parser is not None and parser.line_number:
            raise ValueError(f'{path}: incomplete mesh record')
    rebuild_indices(df)
    if not df.storge_part_element:
        raise ValueError(f'{path}: no shell or solid mesh parts')
    return df


def filename_targets(path):
    """A numeric filename identifies positive PARTs within that file only."""
    stem = Path(path).stem
    if stem.lower() == 'background':
        return set()
    if not re.fullmatch(r'[0-9]+(?:_[0-9]+)*', stem):
        raise ValueError(f'{path}: use target PART IDs as filenames, such as 1008.k or '
                         '1008_1009.k; use background.k for background-only files.')
    ids = {int(value) for value in stem.split('_')}
    if 0 in ids:
        raise ValueError(f'{path}: filename PART IDs must be positive.')
    return ids


def folder_parts(folder, cancelled=lambda: False, filename_labels=False, progress=lambda text: None):
    paths = sorted(p for p in Path(folder).rglob('*') if p.is_file() and p.suffix.lower() in ('.k', '.key'))
    if not paths:
        raise ValueError('The training folder has no .k or .key files.')
    result = []
    for index, path in enumerate(paths, 1):
        if cancelled():
            raise InterruptedError('Reading training folder cancelled.')
        targets = filename_targets(path) if filename_labels else None
        progress(f'Reading {index}/{len(paths)}: {path.name}')
        # Hash expanded content so edits in INCLUDE files also invalidate the cache.
        deck = load_deck(path, 'lsdyna')
        digest = hashlib.sha256(b'towing-cloud-v1')
        for record in deck.lines:
            digest.update(record.text.encode('utf-8'))
            digest.update(b'\n')
        from utilities.app_paths import config_directory
        cache = config_directory() / 'nn_cloud_cache' / (digest.hexdigest() + '.npz')
        clouds = None
        try:
            with np.load(cache, allow_pickle=False) as saved:
                clouds = {int(pid): saved[str(pid)].copy() for pid in saved['pids']}
        except (OSError, ValueError, KeyError, EOFError):
            pass
        if clouds is None:
            df = read_k(path, deck)
            clouds = {pid: np.array([df.node[n].xyz for n in sorted(ids)], dtype=np.float64)
                      for pid, ids in df.storge_part_node_id.items()}
            try:
                cache.parent.mkdir(parents=True, exist_ok=True)
                fd, temp = tempfile.mkstemp(dir=cache.parent, suffix='.npz')
                os.close(fd)
                try:
                    np.savez(temp, pids=np.array(sorted(clouds)), **{str(pid): xyz for pid, xyz in clouds.items()})
                    os.replace(temp, cache)
                finally:
                    if os.path.exists(temp):
                        os.unlink(temp)
            except OSError:
                pass  # Read-only installations can still train without a cache.
        if targets is not None:
            missing = targets-clouds.keys()
            if missing:
                raise ValueError(f'{path}: filename targets {sorted(missing)} have no usable mesh.')
            small = [pid for pid in targets if len(clouds[pid]) < 12]
            if small:
                raise ValueError(f'{path}: target PARTs {small} have fewer than 12 nodes.')
        for pid, points in sorted(clouds.items()):
            if len(points) < 12:
                continue
            # Training only needs points; do not retain 1000 complete assembly meshes.
            result.append(PartCloud(str(path.resolve()), pid, points, None,
                                    pid in targets if targets is not None else None))
    if not result:
        raise ValueError('No parts have enough points for training.')
    return result


def normalize(points, count=512, rng=None):
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('Point cloud must contain finite XYZ coordinates.')
    if len(points) < 12:
        raise ValueError('Point cloud needs at least 12 nodes.')
    center = points.mean(axis=0)
    points = points - center
    scale = np.linalg.norm(points, axis=1).max()
    if scale <= 1e-12:
        raise ValueError('Point cloud has zero extent.')
    points /= scale
    # PCA removes rigid orientation before the learned classifier. No shape labels
    # are inferred by PCA; classification still comes only from trained weights.
    _, _, frame = np.linalg.svd(points, full_matrices=False)
    if np.linalg.det(frame) < 0:
        frame[-1] *= -1
    points = points @ frame.T
    if rng is None:
        indices = np.linspace(0, len(points)-1, count).astype(int)
    else:
        indices = rng.choice(len(points), count, replace=len(points) < count)
    return points[indices].astype(np.float32)
