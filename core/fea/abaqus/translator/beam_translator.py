"""Verified uniform LS-DYNA beam/truss cross-sections to Abaqus."""
import math
from core.fea.translator import Translator
from core.fea.conversion_notes import unconverted
from utilities.source_location import diagnostic


def profile(section):
    d = section.dimensions
    if section.nsm or section.scoor or section.naupd:
        raise ValueError('SECTION_BEAM NSM/SCOOR/NAUPD requires an additional mapping')
    if section.elform == 3 and not section.shape:
        if any(d[1:]):
            raise ValueError('Truss initial stress/dynamic relaxation is not mapped')
        return 'TRUSS', (d[0],)
    if section.elform == 2 and section.shape == 'SECTION_01':
        width, flange, height, web = d[:4]
        if any(d[4:]) or min(width, flange, height, web) <= 0 or 2*flange >= height or web >= width:
            raise ValueError('Invalid symmetric I-section dimensions')
        # R13 Fig 39-1; Abaqus I profile: l, h, b1, b2, t1, t2, t3.
        return 'I', (height/2, height, width, width, flange, flange, web)
    if section.elform == 1 and not section.shape:
        a, b, c, e, s, t, *_ = d
        if a != b or c != e or s or t:
            raise ValueError('Tapered or offset SECTION_BEAM is not mapped')
        if section.cst == 0:
            return 'RECT', (a, c)
        if section.cst == 1:
            if not 0 <= c < a:
                raise ValueError('Beam requires 0 <= inner diameter < outer diameter')
            return ('CIRC', (a / 2,)) if c == 0 else ('THICK PIPE', (a / 2, (a - c) / 2))
    raise ValueError(f'SECTION_BEAM ELFORM={section.elform}, CST={section.cst}, '
                     f'shape={section.shape or "numeric"}: no verified Abaqus section mapping')


class BeamTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        lines = df.output_storge.setdefault('*BEAM_MODEL', [])
        for element in df.storge['element_beam'].values():
            try:
                part = df.part[element.pid]
                section = df.section_beam[part.secid]
                shape, dimensions = profile(section)
                if shape == 'THICK PIPE':
                    from .analysis_data import is_explicit
                    if is_explicit(df):
                        raise ValueError('Thick-walled pipe section requires Abaqus/Standard')
                if any(value <= 0 for value in dimensions):
                    raise ValueError('Beam section dimensions/area must be positive')
                if element.rt1 or element.rt2 or element.rr1 or element.rr2:
                    raise ValueError('Beam end releases require an additional Abaqus mapping')
                p1, p2 = df.node[element.n1], df.node[element.n2]
                tangent = tuple(b - a for a, b in zip(p1.xyz, p2.xyz))
                length = math.sqrt(sum(v*v for v in tangent))
                if not length:
                    raise ValueError('Zero-length structural beam')
                group = f'dyna_beam_{element.uid}'
                material = df.material[part.mid].name
                if shape == 'TRUSS':
                    lines += [f'*ELEMENT, TYPE=T3D2, ELSET={group}\n',
                              f'{element.uid}, {element.n1}, {element.n2}\n',
                              f'*SOLID SECTION, ELSET={group}, MATERIAL={material}\n',
                              f'{dimensions[0]:.12g}\n']
                    continue
                vector = element.vector
                if vector is None and element.n3:
                    vector = tuple(b - a for a, b in zip(p1.xyz, df.node[element.n3].xyz))
                if vector is None and shape in ('CIRC', 'PIPE', 'THICK PIPE'):
                    axis = min(range(3), key=lambda i: abs(tangent[i]))
                    vector = tuple(float(i == axis) for i in range(3))
                if vector is None:
                    raise ValueError('Noncircular beam requires an orientation node/vector')
                projection = sum(a*b for a, b in zip(vector, tangent)) / length**2
                perpendicular = tuple(a - projection*b for a, b in zip(vector, tangent))
                norm = math.sqrt(sum(v*v for v in perpendicular))
                if norm <= 1e-12 * max(math.sqrt(sum(v*v for v in vector)), 1e-30):
                    raise ValueError('Beam orientation vector is parallel to the beam axis')
                lines += [f'*ELEMENT, TYPE=B31, ELSET={group}\n',
                          f'{element.uid}, {element.n1}, {element.n2}\n',
                          f'*BEAM SECTION, ELSET={group}, MATERIAL={material}, SECTION={shape}\n',
                          ', '.join(f'{v:.12g}' for v in dimensions) + '\n',
                          ', '.join(f'{v/norm:.12g}' for v in perpendicular) + '\n']
                # Geometry and material are mapped; source integration settings are not identical.
                if not getattr(section, '_abaqus_noted', False):
                    unconverted(f'SECTION_BEAM {section.uid}: source ELFORM/QR/SHRF integration '
                                'settings replaced by Abaqus B31 section defaults', section)
                    section._abaqus_noted = True
            except (ValueError, KeyError) as error:
                raise ValueError(diagnostic(f'Cannot convert beam {element.uid}: {error}', element)) from error
