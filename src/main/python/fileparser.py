from openpyxl import Workbook, load_workbook


class ParseFile:
    def __init__(self):
        self.filepath = 'C:/Users/brand/OneDrive - InsureGood ' \
                                 'LLC/Documents - Cedar ' \
                                 'Insights/applications/WebScrape' \
                                 '/Div_of_Corporations/SPAC List.xlsx'
        self.wb = Workbook()
        self.search_list = []
    def fileParser(self):
        # load workbook
        self.wb = load_workbook(self.filepath)
        # select workbook
        self.sheet = self.wb.active
        # get max row count
        self.max_row = self.sheet.max_row
        # iterate through all rows in first column, skipping first row
        for r in range(2, self.max_row):
            self.cell = self.sheet.cell(row=r, column=1)
            self.search_list = [self.cell.value]
    def getExcelFile(self):
        return self.search_list



pf = ParseFile()
pf.fileParser()