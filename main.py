# Selenium, to get and crawl the URLs
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import selenium.common.exceptions

# Utils
from src.CrawlService import CrawlService
from src.Database import Database
from src.LogService import LogService

import time
import json

logs = LogService()

# Selenium setup
mainUrl = 'https://www.crockpotting.es/indice/'
driverpath = './geckodriver.exe'
s = Service(driverpath)
driver = webdriver.Firefox(service=s)
logs.sendInfo('Selenium has been set up')

# Settings to change the behaviour of the script
with open('./AppConfig.json') as inputFile:
    config = json.load(inputFile)
    GET_URLS = config['GET_URLS']
    CRAWL_ALL = config['CRAWL_ALL']


###########################################
#           Instantiate Classes           #
###########################################

crawlService = CrawlService(mainUrl, logs)
db = Database(dbPath = './db/tiny.json')


###########################################
#              Prepare crawl              #
###########################################

if (GET_URLS):
    logs.sendInfo('Extracting URLs')
    recipeList = crawlService.getUrls(driver)
    logs.sendInfo('Updating database')
    db.update(recipeList)


###########################################
#              Execute crawl              #
###########################################

if (CRAWL_ALL):
    preCrawledURLs = db.database.table('urls').all()
    crawledURLs = []
    counter = 0
    for recipe in preCrawledURLs:
        try:
            recipeEnriched = crawlService.getData(driver, recipe) 
            if not recipeEnriched:
                continue
            logs.sendInfo('Crawl complete.')
        except selenium.common.exceptions.NoSuchElementException as e:
            logs.sendWarning(f'Could not crawl given url: {e}')
            recipeEnriched = recipe    
        recipeEnriched['crawled'] = True
        crawledURLs.append(recipeEnriched)

        time.sleep(1)
        counter += 1
        if counter % 20 == 0:
            db.update(crawledURLs)
            logs.sendInfo('Updating database.')
            crawledURLs = []
    db.update(crawledURLs)
driver.close()