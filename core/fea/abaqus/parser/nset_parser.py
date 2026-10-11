from .elset_parser import ElsetParser


class NsetParser(ElsetParser):
    def parse(self, options, rows, sets):
        super().parse(options, rows, sets, key='NSET')
