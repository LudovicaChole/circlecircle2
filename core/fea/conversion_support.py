"""Availability rules shared by the application and conversion entry point."""


class TranslationUnderDevelopment(ValueError):
    pass


def development_warning(source, target, version):
    normalize = lambda value: str(value).strip().lower().replace('-', '').replace(' ', '')
    source, target = normalize(source), normalize(target)
    version = str(version)
    pending = (target == 'lsdyna' and version not in ('12.0', '13.0')) or (
        source == 'lsdyna' and ((target == 'abaqus' and version != '6.14') or
                               (target == 'pamcrash' and version != '2020')))
    if pending:
        return f'{source} → {target} {version}: This feature is under development. Conversion was not started.'
    return None
