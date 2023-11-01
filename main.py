
# Selenium, to get and crawl the URLs
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

# Utils
from src.prepareCrawl import PrepareCrawl
from src.database import Database

# Logging
import logging
logging.basicConfig(encoding='utf-8', level=logging.INFO)


# Other utils
import time

# Selenium setup
mainUrl = 'https://www.crockpotting.es/indice/'
driverpath = './geckodriver.exe'
s = Service(driverpath)
driver = webdriver.Firefox(service=s)
logging.info('Selenium has been set up')

getUrls = False
updateDatabase = False
crawllAll = False

###########################################
#           Instantiate Classes           #
###########################################

pC = PrepareCrawl(driver, mainUrl)
db = Database(dbPath = './db/tiny.json')


###########################################
#              Prepare crawl              #
###########################################

if (getUrls):
    logging.info('Extracting URLs')
    recipeList = pC.getUrls()

if (updateDatabase):
    logging.info('Updating database')
    db.update(recipeList)

urlTable = db.database.table('urls')
crawledURLs = urlTable.all()
test = crawledURLs[10]
test = pC.getData(test)    
print(test)

if (crawllAll):
    for recipe in crawledURLs:
        recipeEnriched = pC.getData(recipe)    
        time.sleep(5)
