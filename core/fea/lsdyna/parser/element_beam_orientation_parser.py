from .element_beam_parser import ElementBeamParser


class ElementBeamOrientationParser(ElementBeamParser):
    def __init__(self):
        super().__init__(orientation=True)
