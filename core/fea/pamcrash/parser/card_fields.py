"""PAM fixed-column numeric fields (including PYVAR references)."""
from core.fea.dataframe import dataframe
from core.fea.lsdyna.parser.card_fields import number
from core.fea.validation import required_id


def value(raw, integer=False, default=0):
    raw = raw.strip()
    if raw.startswith('<') and raw.endswith('>'):
        raw = '&' + raw[1:-1].strip()
    return number(raw, dataframe, integer=integer, default=default)


def identifier(raw):
    result = value(raw, integer=True)
    return required_id(str(result), 'Identifier', dataframe)
