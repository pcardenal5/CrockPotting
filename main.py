import asyncio
import aiohttp

# Utils
from src.CrawlService import CrawlService
from src.DatabaseService import Database
from src.LogService import LogService

from tqdm import tqdm
import time
import json

async def main():
    logs = LogService()

    # Selenium setup
    mainUrl = 'https://www.crockpotting.es/indice/'

    # Settings to change the behaviour of the script
    with open('./AppConfig.json') as inputFile:
        config = json.load(inputFile)
        GET_URLS = config['GET_URLS']
        CRAWL_ALL = config['CRAWL_ALL']


    ###########################################
    #           Instantiate Classes           #
    ###########################################

    crawlService = CrawlService(mainUrl, logs)
    db = Database(dbPath = './db/AsyncTiny.json')


    ###########################################
    #              Prepare crawl              #
    ###########################################


    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            
        if (GET_URLS):
            logs.sendInfo('Extracting URLs.')
            task = asyncio.ensure_future(crawlService.getUrls(session))

            recipeList = await asyncio.gather(task)

            logs.sendInfo('Updating URL database.')
            db.update(recipeList[0])
        
        if (CRAWL_ALL):
            preCrawledURLs = db.database.table('urls').all()
            #TinyDb does not support "column" selection
            preCrawledURLs = [recipe['Link'] for recipe in preCrawledURLs]
            crawledURLs = []
            
            tasks = [asyncio.ensure_future(crawlService.getData(session, url)) for url in preCrawledURLs]


            recipesHTML = await asyncio.gather(*tasks)
            


            for recipe in tqdm(recipesHTML):
                try:
                    recipeEnriched = crawlService.processRecipePage(recipesHTML, recipe) 
                    if not recipeEnriched:
                        continue
                except Exception as e:
                    e = str(e).replace("\\n", ' ')
                    logs.sendWarning(f'Could not crawl given url: {e}.')
                    recipeEnriched = recipe    
                recipeEnriched['crawled'] = True
                crawledURLs.append(recipeEnriched)

                time.sleep(1)
                counter += 1
                if counter % 20 == 0:
                    db.update(crawledURLs)
                    logs.sendInfo('Updating recipes database.')
                    crawledURLs = []
            db.update(crawledURLs)

if __name__ == '__main__':
    asyncio.run(main())
