"""Native quality reports and bounded repair; unresolved failures are errors."""
from .tcl_bridge import mark, marked, run, quote


def check_mesh_quality(elements, directory, anchor_nodes=()):
    report = directory / 'quality.txt'
    mark('elems', elements)
    run(f'*getqualitysummary 1 {quote(report)} 2 0')
    failed = marked('elems', 2)
    if failed:
        criteria = directory / 'quality.criteria'
        run(f'*writecurrentqualitycriteria {quote(criteria)}')
        mark('elems', elements)
        mark('nodes', anchor_nodes, 1)
        # Keep feature/free edges and weld geometry fixed, but allow interior
        # nodes to redistribute within their existing surfaces.
        run(f'*qismoothfixfailed 1 1 {quote(criteria)} 30 0 0 0 -1 0 5')
        mark('elems', elements)
        run(f'*getqualitysummary 1 {quote(report)} 2 1')
        failed = marked('elems', 2)
    from .job_reports import format_quality
    native_report = report.read_text(encoding='utf-8', errors='replace')
    report.write_text(format_quality(native_report), encoding='utf-8')
    if failed:
        raise ValueError(f'{len(failed)} elements still fail quality after repair; see {report}')
    return str(report)
