import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.main.python.fileparser import ParseFile

# Global variable - change will update all URL instances
urlMain = 'https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch.aspx'


class SiteNavigation:
    def __init__(self):
        # Establish chromedriver path
        self.options = Options()
        self.options.add_argument('--headless')
        self.chromedriver_path = 'C:/Users/brand/OneDrive - InsureGood ' \
                                 'LLC/Documents - Cedar ' \
                                 'Insights/applications/WebScrape' \
                                 '/Div_of_Corporations/chromedriver.exe'
        self.driver = webdriver.Chrome(
            executable_path=self.chromedriver_path, chrome_options=self.options)
        self.excelFile = ParseFile()

    def getUrl(self):
        self.driver.get(urlMain)
        print("Title: ", self.driver.title)

    def searchSite(self):
        # Find website objects
        self.entityNameSearch = self.driver.find_element_by_id(
            'ctl00_ContentPlaceHolder1_frmEntityName')
        self.entityNameSearchBtn = self.driver.find_element_by_id(
            'ctl00_ContentPlaceHolder1_btnSubmit')
        # Grab search criteria from Excel file, if query returns results, click
        # on result(s) and save 'File Number' and 'Incorporation Date'
        self.entityNameSearch.send_keys('*merge*')
        time.sleep(2)
        self.entityNameSearchBtn.click()

    def readTable(self):
        self.table = self.driver.find_element_by_xpath("//*[@id='tblResults']")
        self.rows = self.table.find_elements_by_tag_name('td')
        for row in range(3,len(self.rows),2):
            self.rows[row].click()
            self.driver.implicitly_wait(10)
            self.fileNumber = self.driver.find_element_by_xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_lblFileNumber"]')
            self.entityName = self.driver.find_element_by_id(
                'ctl00_ContentPlaceHolder1_lblEntityName')
            self.incDate = self.driver.find_element_by_id(
                'ctl00_ContentPlaceHolder1_lblIncDate')
            print(self.fileNumber.text, self.entityName.text, self.incDate.text)
            self.driver.back()
            time.sleep(1)
