"""Prevent CFD decks from becoming empty structural Abaqus jobs."""
from core.fea.conversion_notes import unconverted
from core.fea.validation import FeaInputError
from utilities.source_location import source_location


def check_dyna_fluid_mapping(deck):
    keywords = []
    for record in deck.lines:
        text = record.text.strip()
        if text.upper().startswith(('*ICFD_', '*MESH_')):
            keyword = text.split()[0].upper()
            keywords.append(keyword)
            unconverted(f'Cannot convert {keyword}: the current Abaqus exporter has no CFD '
                        'flow-equation, fluid-material or fluid-boundary mapping',
                        source_location(record.path, record.number, keyword))
    if keywords:
        raise FeaInputError('Abaqus CFD conversion is not implemented; no output was written. '
                            'Unmapped keywords: ' + ', '.join(dict.fromkeys(keywords)))
