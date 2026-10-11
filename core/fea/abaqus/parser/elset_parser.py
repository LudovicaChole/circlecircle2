class ElsetParser:
    def parse(self, options, rows, sets, key='ELSET'):
        if set(options) - {key, 'GENERATE', 'UNSORTED'}:
            raise ValueError(f'{key}: unsupported parameters')
        name = options[key].upper()
        ids = sets.setdefault(name, [])
        for row in rows:
            tokens = [v.strip().upper() for v in row.split(',') if v.strip()]
            if 'GENERATE' in options:
                if len(tokens) not in (2, 3):
                    raise ValueError(f'{key} GENERATE expects first, last, increment')
                start, end = map(int, tokens[:2])
                step = int(tokens[2]) if len(tokens) == 3 else 1
                if step <= 0 or end < start or (end-start) % step:
                    raise ValueError(f'{key}: invalid generated range')
                ids.extend(range(start, end+1, step))
            else:
                ids.extend(int(v) if v.isdecimal() else v for v in tokens)


def resolve(sets, name, active=()):
    if name in active:
        raise ValueError(f'Cyclic set reference {name}')
    if name not in sets:
        raise ValueError(f'Undefined set {name}')
    result = set()
    for item in sets[name]:
        if isinstance(item, int):
            result.add(item)
        else:
            result.update(resolve(sets, item, (*active, name)))
    return sorted(result)
