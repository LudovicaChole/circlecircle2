"""Width-checked short LS-DYNA cards; never spill into adjacent fields."""
from core.fea.pamcrash.translator.selection import field


def card(values, width=10):
    return ''.join(field(v, width) for v in values) + '\n'
