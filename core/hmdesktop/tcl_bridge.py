"""Small, quoted Tcl bridge; imported only inside HyperMesh."""
import hw


def quote(value):
    value = str(value).replace('\\', '/')
    return '"' + ''.join('\\'+c if c in '\\"$[]' else c for c in value) + '"'


def run(command):
    try:
        return str(hw.evalTcl(command))
    except Exception as error:
        detail = str(hw.evalTcl('set ::errorInfo'))
        raise RuntimeError(f'HyperMesh command failed: {command}\n{detail}') from error


def ids(entity, selection='all', mark=1):
    run(f'*createmark {entity} {mark} {selection}')
    return marked(entity, mark)


def marked(entity, mark=1):
    return [int(i) for i in run(f'hm_getmark {entity} {mark}').split()]


def mark(entity, values, number=1):
    run(f'*createmark {entity} {number} ' + ' '.join(str(int(i)) for i in values))


def strings(options):
    run(f'*createstringarray {len(options)} ' + ' '.join(quote(s) for s in options))
    return len(options)


def value(entity, uid, name):
    return run(f'hm_getvalue {entity} id={int(uid)} dataname={name}')
