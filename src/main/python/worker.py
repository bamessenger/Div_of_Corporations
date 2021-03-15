from PyQt5.QtCore import QObject, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from src.main.python.fileparser import ParseFile
from src.main.python.filewriter import WriteFile
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from chromedriver_py import binary_path


class Worker(QObject):
    urlMain = 'https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch' \
              '.aspx'
    # driverPath = 'C:/Users/brand/OneDrive - InsureGood LLC/Documents - ' \
    #             'Cedar Insights/applications/WebScrape/Div_of_Corporations' \
    #
    # Create worker signals
    currentStatus = pyqtSignal(str)
    progressSearch = pyqtSignal(str)
    progressDialogue = pyqtSignal(str)
    progressScrapes = pyqtSignal(str)
    progressCompleted = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, scFile, mFile):
        super().__init__()
        self.options = Options()
        # Suppress browser pop-up
        self.options.add_argument('--headless')
        # Establish chromedriver path
        # self.chromedriver_path = driverPath
        self.driver = webdriver.Chrome(executable_path=binary_path,
                                       chrome_options=self.options)
        self.wait = WebDriverWait(self.driver, 5)
        self.masterFile = mFile
        self.searchData = scFile
        #self.searchFile = ParseFile(scFile)
        self.dataDict = WriteFile()
        self.entityDict = {}

    def run(self):
        self.currentStatus.emit('Starting')
        self.driver.get(self.urlMain)
        if type(self.searchData) is not list:
            # Grab search criteria from Excel file
            self.searchFile = ParseFile(self.searchData)
            self.searchList = self.searchFile.getExcelFile()
            self.searchListLen = len(self.searchList)
            self.progressSearch.emit(str(self.searchListLen))
            self.currentStatus.emit('Reading')
        else:
            self.searchList = self.searchData
            self.searchListLen = len(self.searchList)
            self.progressSearch.emit(str(self.searchListLen))
            self.currentStatus.emit('Reading')
        for i in range(self.searchListLen):
            # Find website objects
            self.currentStatus.emit('Searching')
            entityNameSearch = self.wait.until(
                ec.presence_of_element_located(
                    (By.ID, 'ctl00_ContentPlaceHolder1_frmEntityName')))
            entityNameSearch.clear()
            # Pull search items in excel list and populate search box with
            # wildcard search characters
            entityNameSearch.send_keys('*' + self.searchList[i] + '*')
            # Find search button and click it
            entityNameSearchBtn = self.wait.until(
                ec.presence_of_element_located(
                    (By.ID, 'ctl00_ContentPlaceHolder1_btnSubmit')))
            entityNameSearchBtn.click()
            results = self.wait.until(ec.presence_of_element_located(
                (By.ID, 'ctl00_ContentPlaceHolder1_divCountsMsg')))
            # format string to show a percentage w/2 decimal places
            self.progressCompleted.emit(str(
                '{:.2f}%'.format((i/self.searchListLen)*100)))
            if results.text != 'No Records Found.':
                self.currentStatus.emit('Scraping')
                self.progressDialogue.emit(
                    self.searchList[i] + '...........' + 'Results '
                                                'Found')
                self.driver.implicitly_wait(5)
                # Find the Table of results
                table = self.driver.find_element_by_id('tblResults')
                # Find all the rows of data
                rows = table.find_elements_by_tag_name('td')
                # Loop through all the rows, first starting at line 3, going
                # the length of the total rows, and skipping every other
                # 'td' (only want Entity Name, ignore File Number, for
                # hyperlink)
                for row in range(3, len(rows), 2):
                    # Re-introduce table/rows vars to combat stale element
                    # error
                    table = self.driver.find_element_by_id('tblResults')
                    rows = table.find_elements_by_tag_name('td')
                    self.driver.implicitly_wait(10)
                    entityText = rows[row].text
                    # Click on hyperlink text to get to Entity details
                    # Identify if and duplicate links exist and
                    dups = len(
                        self.driver.find_elements_by_link_text(entityText))
                    if dups > 1:
                        for i in range(dups):
                            self.driver.find_elements_by_link_text(
                                entityText)[i].click()
                            self.getInfo()
                    else:
                        self.driver.find_element_by_link_text(
                            entityText).click()
                        self.getInfo()
            # if condition not met, continue with for loop
            else:
                self.progressDialogue.emit(
                    self.searchList[i] + '...........' + 'No Results Found')
                continue
        # when scraping complete, send captured data to filewriter to
        # write back into master data file
        self.currentStatus.emit('Writing')
        self.dataDict.setNewMastDict(self.entityDict, self.masterFile)
        self.currentStatus.emit('Completed')
        self.driver.quit()
        self.progressCompleted.emit(str('100%'))
        self.finished.emit()

    def getInfo(self):
        self.driver.implicitly_wait(5)
        # Gather File Number, Entity Name, and Incorporation Date
        fileNumber = self.wait.until(ec.presence_of_element_located(
            (By.ID, 'ctl00_ContentPlaceHolder1_lblFileNumber')))
        entityName = self.wait.until(ec.presence_of_element_located(
            (By.ID, 'ctl00_ContentPlaceHolder1_lblEntityName')))
        incDate = self.wait.until(ec.presence_of_element_located(
            (By.ID, 'ctl00_ContentPlaceHolder1_lblIncDate')))
        # Input data into dictionary where fileNumber is key
        self.entityDict[fileNumber.text] = entityName.text, incDate.text
        self.progressScrapes.emit(str(len(self.entityDict)))
        # Have browser go back to Search page
        self.driver.back()
