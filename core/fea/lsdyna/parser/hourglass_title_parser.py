from core.fea.lsdyna.parser.hourglass_parser import HourglassParser


class HourglassTitleParser(HourglassParser):
    def _12p0(self, line_raw):
        if self.line_number == 0:
            self.temp = [line_raw.strip()]
            self.line_number = 1
        else:
            record = super()._12p0(line_raw)
            record.name = self.temp[0]
            self.reset()
