from .section_beam_parser import SectionBeamParser


class SectionBeamTitleParser(SectionBeamParser):
    def __init__(self):
        super().__init__(title=True)
