from core.fea.parser import Parser
from core.fea.model.lsdyna.element_shell import ElementShell
from core.fea.mesh_data import insert
from .card_fields import identifier, value


class ShellParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        eid, pid, n1, n2, n3 = [identifier(line_raw[i:i+8]) for i in range(8, 48, 8)]
        n4 = value(line_raw[48:56], integer=True) or n3
        element = ElementShell(uid=eid, pid=pid, n1=n1, n2=n2, n3=n3, n4=n4)
        # Columns 57-64 are reserved; H occupies columns 65-72.
        element.thickness = value(line_raw[64:72])
        if element.thickness < 0:
            raise ValueError('SHELL: negative H is not supported')
        insert(self.dataframe.element_shell, element)
