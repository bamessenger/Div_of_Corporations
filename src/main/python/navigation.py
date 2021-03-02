import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from src.main.python.fileparser import ParseFile
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Global variable - change will update all URL instances
urlMain = 'https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch.aspx'


class SiteNavigation:
    def __init__(self):
        # Establish chromedriver path
        self.options = Options()
        # Surpress browser pop-up
        self.options.add_argument('--headless')
        self.chromedriver_path = 'C:/Users/brand/OneDrive - InsureGood ' \
                                 'LLC/Documents - Cedar ' \
                                 'Insights/applications/WebScrape' \
                                 '/Div_of_Corporations/chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=self.chromedriver_path,
            chrome_options=self.options)
        self.wait = WebDriverWait(self.driver, 10)
        self.excelFile = ParseFile()

    def getUrl(self):
        self.driver.get(urlMain)
        # print("Title: ", self.driver.title)

    def searchSite(self):
        # Find website objects
        self.entityNameSearch = self.wait.until(ec.presence_of_element_located(
            (By.ID, 'ctl00_ContentPlaceHolder1_frmEntityName')))
        self.entityNameSearchBtn = self.wait.until(
            ec.presence_of_element_located(
                (By.ID, 'ctl00_ContentPlaceHolder1_btnSubmit')))
        # Grab search criteria from Excel file, if query returns results, click
        # on result(s) and save 'File Number' and 'Incorporation Date'
        self.entityNameSearch.send_keys('*merge*')
        self.driver.implicitly_wait(10)
        self.entityNameSearchBtn.click()

    def readTable(self):
        # Start by finding the Table of results
        self.table = self.driver.find_element_by_id('tblResults')
        # Find all the rows of data
        self.rows = self.table.find_elements_by_tag_name('td')
        # Loop through all the rows, first starting at line 3, going the length
        # of the total rows, and skipping every other 'td' (only want Entity
        # Name, ignore File Number, for hyperlink)
        for row in range(3, len(self.rows), 2):
            # Re-introduce table/rows vars to combat stale element errors
            self.table = self.driver.find_element_by_id('tblResults')
            self.rows = self.table.find_elements_by_tag_name('td')
            self.driver.implicitly_wait(10)
            self.entityText = self.rows[row].text
            # Click on hyperlink text to get to Entity details
            self.driver.find_element_by_link_text(self.entityText).click()
            self.driver.implicitly_wait(10)
            # Gather File Number, Entity Name, and Incorporation Date
            self.fileNumber = self.wait.until(ec.presence_of_element_located(
                (By.ID, 'ctl00_ContentPlaceHolder1_lblFileNumber')))
            self.entityName = self.wait.until(ec.presence_of_element_located(
                (By.ID, 'ctl00_ContentPlaceHolder1_lblEntityName')))
            self.incDate = self.wait.until(ec.presence_of_element_located(
                (By.ID, 'ctl00_ContentPlaceHolder1_lblIncDate')))
            print(self.fileNumber.text, self.entityName.text, self.incDate.text)
            # Have browser go back to Search page
            self.driver.back()

