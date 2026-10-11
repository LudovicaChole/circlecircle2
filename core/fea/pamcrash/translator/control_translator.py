"""Map solver-independent control intent to PAM, with explicit partial audits.

Layouts follow the supplied PAM 2020 TCTRL pages and OCTRL/header examples.
Algorithm-specific controls remain in the source archive, never guessed.
"""
from decimal import Decimal
from functools import reduce
from math import gcd
from core.fea.translator import Translator
from core.fea.conversion_notes import unconverted


def number(value):
    return format(value, '.12g')


def common_interval(values):
    """A common output grid preserves every requested constant output time."""
    values = [Decimal(str(value)) for value in values]
    places = max(0, -min(value.as_tuple().exponent for value in values))
    scale = 10 ** places
    result = Decimal(reduce(gcd, (int(value * scale) for value in values))) / scale
    if result <= 0 or min(values) / result > 10000:
        raise ValueError('PAM OCTRL: source output intervals have no practical common time grid')
    return float(result)


class HeaderTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        if df.solver != 'lsdyna':
            return
        implicit = bool(df.storge.get('implicit_eigenvalue'))
        lines = [f'INPUTVERSION {version}\n', 'SOLVER  CRASH\n',
                 'ANALYSIS  ' + ('IMPLICIT' if implicit else 'EXPLICIT') + '\n']
        if implicit:
            unconverted('PAM ANALYSIS IMPLICIT identifies the analysis only; implicit solver controls are not mapped')
        for title in df.title.values():
            lines.append('TITLE / ' + str(title.context).replace('\n', ' ').replace('\r', ' ') + '\n')
        df.output_storge['PAM_HEADER'] = lines


class ControlTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        if df.solver != 'lsdyna':
            return
        consumed = {}

        def mark(store, fields):
            consumed.setdefault(store, set()).update(fields)

        tctrl = []
        for obj in df.control_timestep.values():
            if obj.dtinit > 0:
                tctrl.append(f' INITIAL {number(obj.dtinit)}\n')
            if obj.tssfac > 0:
                tctrl.append(f' SCALE CONSTANT {number(obj.tssfac)}\n')
            mark('control_timestep', ('dtinit', 'tssfac'))
            if obj.dt2ms < 0 and obj.ms1st == 1 and not any(
                    (obj.lctm, obj.dt2msf, obj.dt2mslc, obj.imscl, obj.rmscl, obj.ihdo)):
                tctrl.append(f' INIT_MASS_SCALE {number(abs(obj.dt2ms))}\n')
                mark('control_timestep', ('dt2ms', 'ms1st'))
                unconverted('Initial-only mass scaling criterion mapped to PAM INIT_MASS_SCALE; solver element timestep/mass algorithms differ', obj)
            # LCTM/DT2MS are mass-scaling controls, not user-imposed PREFER.
            # A zero physical curve is inactive and needs no mass scaling.
            if obj.lctm and obj.lctm in df.define_curve:
                curve = df.define_curve[obj.lctm]
                physical_y = [(float(y) + curve.offo) * (curve.sfo or 1.0) for y in curve.o1]
                if physical_y and all(y == 0 for y in physical_y) and obj.dt2ms == 0:
                    mark('control_timestep', ('lctm',))
        if tctrl:
            df.output_storge['TCTRL'] = ['TCTRL /\n', *tctrl, 'END_TCTRL\n']

        octrl = []
        history = []
        for store, records in df.storge.items():
            if not store.startswith('database_') or not isinstance(records, dict):
                continue
            if store.startswith('database_binary_') or store in ('database_extent_binary', 'database_format'):
                continue
            for obj in records.values():
                if getattr(obj, 'dt', 0) > 0 and not getattr(obj, 'lcur', 0):
                    history.append(obj.dt)
                    mark(store, ('dt',))
        if history:
            interval = common_interval(history)
            octrl.append(f' TIME_HISTORY INTERVAL {number(interval)}\n')
            if len(set(history)) > 1:
                unconverted(f'PAM has one history schedule: using common interval {number(interval)}; output may be denser than source')
        for obj in df.database_binary_d3plot.values():
            if obj.dt > 0 and not obj.lcdt:
                octrl.append(f' CONTOUR_PLOT INTERVAL {number(obj.dt)}\n')
                mark('database_binary_d3plot', ('dt',))
        if df.database_glstat or df.database_matsum or df.database_sleout or df.control_energy:
            octrl.append(' GLBTHP ALL\n')
            unconverted('PAM GLBTHP ALL covers global energy/history intent; LS file separation and individual energy accounting switches are not equivalent')
        if df.database_elout:
            octrl += [' SHLTHP ALL\n', ' SOLTHP ALL\n', ' BEATHP ALL\n']
            unconverted('PAM element histories use ALL variables; LS ELOUT selection/variable layouts are retained in the source archive')
        if df.database_nodout:
            octrl.append(' NODPLOT FACM\n')
        if df.database_extent_binary:
            flags = next(iter(df.database_extent_binary.values()))
            shell, solid = [], []
            for flag, qualifier in (('sigflg', 'SIGM'), ('strflg', 'STRA')):
                if getattr(flags, flag) == 1:
                    shell.append(qualifier)
                    if not df.element_solid:
                        mark('database_extent_binary', (flag,))
            if flags.epsflg == 1:
                shell.append('EPME')
                solid.append('EPLE')
                mark('database_extent_binary', ('epsflg',))
            if shell:
                octrl.append(' SHLPLOT ' + ' '.join(shell) + '\n')
            if solid:
                octrl.append(' SOLPLOT ' + ' '.join(solid) + '\n')
        for store in ('database_binary_d3dump', 'database_binary_runrsf'):
            for obj in df.storge.get(store, {}).values():
                if getattr(obj, 'dt', 0) > 0 and not getattr(obj, 'lcur', 0):
                    octrl.append(f' RSTOUTPUT INTERVAL {number(obj.dt)}\n')
                    mark(store, ('dt',))
                    unconverted('PAM restart output frequency mapped; restart file format/content differ', obj)
                    break
            if any('RSTOUTPUT' in line for line in octrl):
                break
        if octrl:
            df.output_storge['OCTRL'] = ['OCTRL /\n', *octrl, 'END_OCTRL\n']

        mark('control_termination', ('endtim',))
        mark('control_solution', ('soln',))
        handled = {'database_history_node', 'database_cross_section_plane_id',
                   'database_cross_section_set', 'control_hourglass'}
        audit = []
        for store, records in df.storge.items():
            if not store.startswith(('control_', 'database_')) or not isinstance(records, dict) or store in handled:
                continue
            for obj in records.values():
                used = consumed.get(store, set())
                pending = {key: value for key, value in vars(obj).items()
                           if key not in used | {'uid', 'name', 'source_context', 'has_optional_card'}
                           and isinstance(value, (int, float)) and value != 0}
                audit.append({'source': store.upper(), 'mapped_fields': sorted(used),
                              'unmapped_fields': pending})
                if pending or not used:
                    unconverted(f'{store.upper()}: PAM mapping is partial; unconverted fields '
                                + (', '.join(f'{k.upper()}={v}' for k, v in pending.items()) or '(solver-specific card/default semantics)'), obj)
        df.storge['pam_control_audit'] = {index: row for index, row in enumerate(audit, 1)}
