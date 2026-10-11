"""Report known missing PAM mappings before source validation hides them.

These are converter limitations, not claims about capabilities of VPS itself.
The source locations refer to the expanded deck, including nested includes.
"""
from core.fea.conversion_notes import unconverted
from core.fea.validation import FeaInputError
from utilities.source_location import source_location


def check_dyna_mapping(deck):
    blockers = []
    for record in deck.lines:
        text = record.text.strip()
        if not text.startswith('*'):
            continue
        keyword = text.split()[0].upper()
        reason = None
        if keyword.startswith(('*ICFD_', '*MESH_')):
            reason = 'fluid mesh/analysis mapping is not implemented'
        elif keyword.startswith(('*ELEMENT_BEAM', '*SECTION_BEAM')):
            reason = ('beam section/material mapping has not been verified against '
                      'the available PAM-CRASH 2020 documentation; BEAM topology '
                      'alone is insufficient. Missing verified 1D beam material '
                      '(e.g. elastic MATYP 201) and cross-section card definitions. '
                      'PAM-CRASH supports beams, but this converter does not yet '
                      'map their stiffness/section properties')
        elif (keyword.startswith(('*MAT_THERMAL_', '*CONTROL_THERMAL_',
                                  '*BOUNDARY_TEMPERATURE', '*BOUNDARY_CONVECTION',
                                  '*BOUNDARY_RADIATION', '*BOUNDARY_FLUX',
                                  '*INITIAL_TEMPERATURE', '*LOAD_HEAT_'))):
            reason = ('thermal material/analysis mapping has not been verified against '
                      'the available PAM-CRASH 2020 documentation')
        if reason:
            location = source_location(record.path, record.number, keyword)
            unconverted(f'Cannot convert {keyword} to PAM-CRASH: {reason}', location)
            blockers.append(keyword)
    if blockers:
        keywords = ', '.join(dict.fromkeys(blockers))
        raise FeaInputError(
            'PAM-CRASH conversion cannot preserve the source analysis; '
            f'no output was written. Unmapped keywords: {keywords}. '
            'See the warnings for source files, line numbers and reasons.')
