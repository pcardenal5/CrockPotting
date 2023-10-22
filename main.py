# Database to store data
from tinydb import TinyDB, Query

# Selenium, to get and crawl the URLs
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Get crawleable urls
from src.prepareCrawl import prepareCrawl

# Other utils
import time




# Selenium setup
mainUrl = 'https://www.crockpotting.es/indice/'
driverpath = 'D:/R/Utils/Webdriver/Firefox/geckodriver.exe'
s = Service(driverpath)
driver = webdriver.Firefox(service=s)
print('Selenium has been set up')

###########################################
#              Prepare crawl              #
###########################################

pC = prepareCrawl(driver = driver, dbPath = './db/tiny.json', mainUrl = mainUrl)

recipeDict = pC.getUrls()
print(recipeDict)

TinyDB('./db/tiny.json').insert(recipeDict)


driver.close()