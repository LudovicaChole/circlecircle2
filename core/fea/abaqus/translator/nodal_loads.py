from .analysis_data import curve_points, node_ids
from utilities.source_location import diagnostic


def nodal_loads(df):
    amplitudes, loads = [], []
    for uid, record in df.storge['load_node'].items():
        try:
            dof = {1: 1, 2: 2, 3: 3, 5: 4, 6: 5, 7: 6}.get(record.dof)
            if dof is None or record.cid:
                raise ValueError('Follower/local-coordinate nodal loads are not mapped')
            selected = node_ids(df, df.set_node_list[record.target].ids if record.is_set else [record.target])
            if not selected:
                raise ValueError('Nodal load selection is empty')
            points = curve_points(df.define_curve[record.lcid])
            name = f'dyna_load_{uid}'
            amplitudes += [f'*AMPLITUDE, NAME={name}, TIME=TOTAL TIME\n']
            amplitudes += [f'{x:.12g}, {y:.12g}\n' for x, y in points]
            loads += [f'*CLOAD, AMPLITUDE={name}\n']
            loads += [f'{nid}, {dof}, {record.sf:.12g}\n' for nid in sorted(selected)]
        except (ValueError, KeyError) as error:
            raise ValueError(diagnostic(f'Cannot convert nodal load: {error}', record)) from error
    return amplitudes, loads
