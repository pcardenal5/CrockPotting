
# Selenium, to get and crawl the URLs
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import selenium.common.exceptions

# Utils
from src.prepareCrawl import PrepareCrawl
from src.database import Database

# Logging
import logging
logging.basicConfig(
    encoding='utf-8', 
    level=logging.INFO, 
    filename = 'log.txt',
    filemode='a',
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S')
logger = logging.getLogger()

# Other utils
import time

# Selenium setup
mainUrl = 'https://www.crockpotting.es/indice/'
driverpath = './geckodriver.exe'
s = Service(driverpath)
driver = webdriver.Firefox(service=s)
logger.info('Selenium has been set up')

# Settings to change the behaviour of the script
getUrls = False
crawllAll = True


###########################################
#           Instantiate Classes           #
###########################################

pC = PrepareCrawl(mainUrl)
db = Database(dbPath = './db/tiny.json')


###########################################
#              Prepare crawl              #
###########################################

if (getUrls):
    logger.info('Extracting URLs')
    recipeList = pC.getUrls(driver)
    logger.info('Updating database')
    db.update(recipeList)


###########################################
#              Execute crawl              #
###########################################

if (crawllAll):
    preCrawledURLs = db.database.table('urls').all()
    crawledURLs = []
    for recipe in preCrawledURLs:
        try:
            recipeEnriched = pC.getData(driver, recipe)    
            crawledURLs.append(recipeEnriched)
            logger.info('Crawl complete.')
        except selenium.common.exceptions.NoSuchElementException as e:
            logger.warning('Could not crawl given url.')
            logger.warning(f'{e}')
        time.sleep(5)
    db.update(crawledURLs)

driver.close()