"""Read isotropic nodal MASS cards; reject unsupported inertia/offset data."""
import math
import re
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import value


class MassParser(Parser):
    def parse(self, line_raw, version):
        if version not in ('2020', '2023'):
            raise ValueError(f'Unsupported PAM MASS version {version}')
        if line_raw.strip():
            self.temp.append(line_raw.rstrip('\n\r'))

    def finish(self):
        if len(self.temp) != 4:
            raise ValueError('PAM MASS: expected node header, NAME, masses and inertias')
        header, title, masses, inertias = self.temp
        nid = value(header[8:16], integer=True)
        frame = value(header[16:24], integer=True)
        offsets = [value(header[start:start+16]) for start in (32, 48, 64)]
        if not title.startswith('NAME ') or nid not in self.dataframe.node:
            raise ValueError('PAM MASS: missing NAME or node')
        if frame or any(offsets):
            raise ValueError('PAM MASS: frame/offset conversion is not implemented')
        if '&' in inertias:
            raise ValueError('PAM MASS: product inertia conversion is not implemented')
        xyz = [value(masses[start:start+16]) for start in (8, 24, 40)]
        inertia = [value(inertias[start:start+16]) for start in (8, 24, 40)]
        if not all(math.isfinite(v) for v in (*xyz, *inertia, *offsets)):
            raise ValueError('PAM MASS: nonfinite data')
        if xyz[0] < 0 or not all(v == xyz[0] for v in xyz) or any(inertia):
            raise ValueError('PAM MASS: only isotropic mass without rotary inertia is supported')
        store = self.dataframe.storge.setdefault('element_mass', {})
        match = re.fullmatch(r'NAME source_mass_(\d+)', title)
        uid = int(match.group(1)) if match else max(store, default=0)+1
        if uid in store:
            raise ValueError(f'PAM MASS: duplicate source mass ID {uid}')
        store[uid] = SimpleNamespace(uid=uid, nid=nid, mass=xyz[0], pid=0)
        self.temp = []
