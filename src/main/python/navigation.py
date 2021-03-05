from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from src.main.python.fileparser import ParseFile
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Global variables
urlMain = 'https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch.aspx'
driverPath = 'C:/Users/brand/OneDrive - InsureGood LLC/Documents - ' \
             'Cedar Insights/applications/WebScrape/Div_of_Corporations' \
             '/chromedriver.exe'


class SiteNavigation:
    def __init__(self):
        self.options = Options()
        # Suppress browser pop-up
        self.options.add_argument('--headless')
        # Establish chromedriver path
        self.chromedriver_path = driverPath
        self.driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        # ,chrome_options=self.options)
        self.wait = WebDriverWait(self.driver, 5)
        self.file = ParseFile()
        self.entityDict = {}

    def getUrl(self):
        self.driver.get(urlMain)

    def searchSite(self):
        # Grab search criteria from Excel file
        try:
            excelList = self.file.getExcelFile()
            excelListLen = len(excelList)
            for i in range(excelListLen):
                # Find website objects
                entityNameSearch = self.wait.until(
                    ec.presence_of_element_located(
                        (By.ID, 'ctl00_ContentPlaceHolder1_frmEntityName')))
                entityNameSearch.clear()
                # Pull search items in excel list and populate search box with
                # wildcard search characters
                entityNameSearch.send_keys('*' + excelList[i] + '*')
                entityNameSearchBtn = self.wait.until(
                    ec.presence_of_element_located(
                        (By.ID, 'ctl00_ContentPlaceHolder1_btnSubmit')))
                entityNameSearchBtn.click()
                results = self.wait.until(ec.presence_of_element_located(
                    (By.ID, 'ctl00_ContentPlaceHolder1_divCountsMsg')))
                print(results.text)
                if results.text != 'No Records Found.':
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
                        dups = len(self.driver.find_elements_by_link_text(
                                entityText))
                        if dups > 1:
                            for i in range(dups):
                                self.driver.find_elements_by_link_text(
                                    entityText)[i].click()
                                self.getInfo()
                        else:
                            self.driver.find_element_by_link_text(
                                entityText).click()
                            self.getInfo()
                # if condition not met? continue with for loop
                else:
                    continue
            else:
                self.file.writeExcel(self.entityDict)
        except IOError as e:
            if e.errno == 13:
                print(e.strerror)
                print("Please close file if open")

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
        self.entityDict[
            fileNumber.text] = entityName.text, incDate.text
        print(self.entityDict)
        # Have browser go back to Search page
        self.driver.back()