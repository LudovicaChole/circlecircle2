from core.fea.dataframe import dataframe
from abc import ABC, abstractmethod
from core.fea.validation import guarded


class Translator(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'translate' in cls.__dict__:
            cls.translate = guarded('Translate')(cls.translate)

    def __init__(self):
        self.dataframe = dataframe

    @abstractmethod
    def translate(self, version):
        pass
