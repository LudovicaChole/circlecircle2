from core.fea.parser import Parser
from core.fea.model.lsdyna.database_cross_section_set import DatabaseCrossSectionSet
from core.fea.mesh_data import insert
from .card_fields import identifier, value


class SecFoParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        self.temp.append(line_raw.rstrip())

    def finish(self):
        if not self.temp:
            return
        header = self.temp[0]
        uid = identifier(header[8:16])
        if header[16:24].strip() != 'SECTION' or value(header[24:32],integer=True):
            raise ValueError('SECFO: only global SECTION node/element selections are supported')
        node_ids, element_ids, name = [], [], f'section_{uid}'
        for row in self.temp[1:]:
            if row.startswith('NAME'):
                name = row[4:].strip()
                continue
            tokens = row.split()
            if not tokens or tokens[0]=='END':
                continue
            kind,*items = tokens
            if kind not in ('NOD','ELE'):
                raise ValueError(f'SECFO: unsupported selection {kind}')
            store = self.dataframe.node if kind=='NOD' else {**self.dataframe.element_shell,**self.dataframe.element_solid}
            result = node_ids if kind=='NOD' else element_ids
            for token in items:
                if ':' in token:
                    first,last = map(int,token.split(':'))
                    result.extend(i for i in store if first<=i<=last)
                else:
                    result.append(int(token))
        if not node_ids or not element_ids:
            raise ValueError('SECFO SECTION requires node and element selections')
        insert(self.dataframe.storge['cross_section_set'], DatabaseCrossSectionSet(uid,name,tuple(sorted(set(node_ids))),tuple(sorted(set(element_ids)))))
        self.reset()
