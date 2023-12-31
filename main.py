
# Selenium, to get and crawl the URLs
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import selenium.common.exceptions

# Utils
from src.prepareCrawl import PrepareCrawl
from src.database import Database
import time
import sys

# Logging
import logging
logging.basicConfig(
    encoding='utf-8', 
    level=logging.INFO, 
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    handlers=[logging.FileHandler("log.txt", mode = 'a'), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger()

# Selenium setup
mainUrl = 'https://www.crockpotting.es/indice/'
driverpath = './geckodriver.exe'
s = Service(driverpath)
driver = webdriver.Firefox(service=s)
logger.info('Selenium has been set up')

# Settings to change the behaviour of the script
getUrls = True
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
    counter = 0
    for recipe in preCrawledURLs:
        try:
            recipeEnriched = pC.getData(driver, recipe)    
            recipeEnriched['crawled'] = True
            crawledURLs.append(recipeEnriched)
            logger.info('Crawl complete.')
        except selenium.common.exceptions.NoSuchElementException as e:
            logger.warning('Could not crawl given url.')
            logger.warning(f'{e}')
        time.sleep(5)
        counter += 1
        if counter % 20 == 0:
            db.update(crawledURLs)
            logger.info('Updating database.')
            crawledURLs = []
    db.update(crawledURLs)
driver.close()