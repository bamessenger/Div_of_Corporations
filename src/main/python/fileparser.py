from openpyxl import Workbook, load_workbook


class ParseFile:
    def __init__(self):
        self.filepath = 'C:/Users/brand/OneDrive - InsureGood ' \
                                 'LLC/Documents - Cedar ' \
                                 'Insights/applications/WebScrape' \
                                 '/Div_of_Corporations/SPAC List.xlsx'
        self.wb = Workbook()
    def fileparser(self):
        # load workbook
        self.wb = load_workbook(self.filepath)
        # select workbook
        self.sheet = self.wb.active
        # get max row count
        self.max_row = self.sheet.max_row

        for r in range(2,self.max_row):
            self.cell = self.sheet.cell(row=r, column=1)
            print(self.cell.value)

pf = ParseFile()
pf.fileparser()