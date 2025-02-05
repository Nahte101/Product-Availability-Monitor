from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import smtplib
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time

from Emailer import Emailer



#TODO PRICING MONITORING
#For pricing store the price IF THERES NO DISCOUNT and keep that safe
#maybe title -> array of prices in a dictionary for history sake


stockKeywords = ["in", "out", "stock"]
productMonitorTypes = ["stock","price"]

nintendoEShopXPaths = {
    'price':'//*[@id="root"]/div/div/article/section/section/section[1]/section[2]/div/div/div/div[1]/div[1]/div/div[1]',
    'img':'//*[@id="root"]/div/div/article/section/section/section[1]/section[1]/section/section/div/div/div/div[3]/div/div/img',
    'name':'//*[@id="root"]/div/div/article/section/div[2]/h1'
}
def timer(secs):
    while secs:
        mins, secs = divmod(secs,60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        time.sleep(1)
        secs -= 1

#Stock monitor & price monitor types for now
class ProductMonitor:

    def __init__(self, savedProductListFile: str):
        #Web scraper settings and stuff
        self.webDriveOptions = webdriver.ChromeOptions()
        self.webDriveOptions.add_argument('--headless')

        self.chromeService = ChromeService('chromedrive')

        #SavedUrlTagPairList should be CSV one pair per line + the type of monitor that product
        self.savedProductListFile = savedProductListFile
        self.stockMonitorProducts = dict()
        self.priceMonitorProducts = dict()
        
        self.stockStates = dict()
        self.priceStates = dict()
        
        self.fileToProductDict(self.savedProductListFile)

        self.emailSystem = Emailer()
        
    def fileToProductDict(self, filename: str):
        productDict = dict()
        file = open(filename, 'r')
        for line in file:
            parts = line.split(',')
            productDict[parts[0]] = parts[1]
            #Stripping out newline characters
            parts[2] = parts[2].replace('\n', '')
            if parts[2] == "stock":
                self.stockMonitorProducts[parts[0]] = parts[1]
            elif parts[2] == "price":
                self.priceMonitorProducts[parts[0]] = parts[1]

    def monitorStockProducts(self):
        
        self.browser = webdriver.Chrome(options=self.webDriveOptions, service=self.chromeService)

        for productPage in self.stockMonitorProducts:
            xmlPath = self.stockMonitorProducts[productPage]
            self.browser.get(productPage)
            element = self.browser.find_element(By.XPATH,xmlPath)
            #i means in stock and o means out of stock just to make them on char incase when saving to a file
            if self.getStockState(element):
                stockState = 'i' 
            else:
                stockState = 'o'
            self.storeStockState(productPage, stockState)
        print("PRODUCTS = " + str(self.stockMonitorProducts))
        print("PRODUCT STATE = " + str(self.stockStates))
        self.browser.close()

    def getStockState(self, element):
        elementText = element.text.lower()
        print("ELEMENT TEXT = " + elementText)
        #Had some problems with this because find() returns a index and -1 if not found
        if elementText.find(stockKeywords[2]) != -1 and elementText.find(stockKeywords[0]) != -1:
            print("STOCK STATE TRUE")
            return True
        else:
            print("STOCK STATE FALSE")
            return False
        
    def storeStockState(self, url :str, state :str):
        #Check if url already exists in dict and if it does check what the state is and only update it if it's different (also send an email if its different for both out of stock and in stock)
        if url in self.stockStates.keys():
            if self.stockStates[url] == state:
                pass#State is the same do not update
            else:
                #Update State and send an email as an update
                self.stockStates[url] = state
                #Send out an email depending on the state
                if state == 'o':
                    self.emailSystem.sendStockEmail("N64 SWITCH ONLINE CONTROLLER", "OUT OF STOCK")
                else:
                    self.emailSystem.sendStockEmail("N64 SWITCH ONLINE CONTROLLER", "IN STOCK")
        else:#Add the url & state to the dict as it doesn't exist
            self.stockStates[url] = state
            
    #TODO Save product states to file just incase function #File format should be 'url,monitorType,status' per line    
        
productMonitor = ProductMonitor("products.txt")
while 1:
    productMonitor.monitorStockProducts()
    timer(300)

"""
url = 'https://store.nintendo.com.au/au/nintendo-64-controller.html'
url = 'https://store.nintendo.com.au/au/super-nintendo-entertainment-system-controller.html'

browser.get(url)

stock_txt = browser.find_element(By.XPATH, '//*[@id="maincontent"]/div[2]/div/div[1]/div[2]/div[1]/div[1]/span').text

print("TEXT IN TAG = " + stock_txt)
"""
