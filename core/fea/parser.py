from core.fea.dataframe import dataframe
from abc import ABC, abstractmethod
from core.fea.validation import guarded

class Parser:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'parse' in cls.__dict__:
            cls.parse = guarded('Parse')(cls.parse)

    def __init__(self):
        """
        self.version is a function mapping, must be define, like this:
        self.version = {
            "12.0": f1,
            "13.0": f2,
        }

        f1, f2, ... is a user define function to parse line raw data
        """
        self.dataframe = dataframe
        self.line_number = 0
        self.temp = []
        self.version = {}

    def reset(self):
        self.line_number = 0
        self.temp = []

    @guarded("Parse")
    def parse(self, line_raw, version):
        """
        :param line_raw: raw data
        :return: Node Object
        """

        try:
            if version not in self.version:
                raise ValueError(f"Unsupported parser version {version}")
            self.version[version](line_raw)

        except Exception as e:

            raise e
