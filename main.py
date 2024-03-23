import asyncio
import aiohttp

# Utils
from src.CrawlService import CrawlService
from src.DatabaseService import Database
from src.LogService import LogService

from tqdm import tqdm
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
        BATCH_SIZE = config['BATCH_SIZE']


    ###########################################
    #           Instantiate Classes           #
    ###########################################

    crawlService = CrawlService(mainUrl, logs)
    db = Database(dbPath = './db/AsyncTiny.json')




    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit = BATCH_SIZE, force_close=True)) as session:

    ###########################################
    #              Prepare crawl              #
    ###########################################

        if (GET_URLS):
            logs.sendInfo('Extracting URLs.')
            task = asyncio.ensure_future(crawlService.getUrls(session))

            recipeList = await asyncio.gather(task)

            logs.sendInfo('Updating URL database.')
            db.upsert(recipeList[0])

        if (CRAWL_ALL):
            preCrawledURLs = db.database.table('urls').all()
            #TinyDb does not support "column" selection
            preCrawledURLs = [recipe['Link'] for recipe in preCrawledURLs]

            # Create small batches
            progressBar = tqdm(total = len(preCrawledURLs))
            crawledUrls = 0
            while crawledUrls < len(preCrawledURLs):
                try:
                    urlsToCrawl = preCrawledURLs[crawledUrls:crawledUrls + BATCH_SIZE]
                    preCrawledURLs = preCrawledURLs[crawledUrls + BATCH_SIZE:]
                except IndexError:
                    urlsToCrawl = preCrawledURLs

                tasks = [asyncio.ensure_future(crawlService.getData(session, url)) for url in urlsToCrawl]


                recipesList = await asyncio.gather(*tasks)

                logs.sendInfo('Updating database')
                db.upsert(recipesList)
                progressBar.update(len(recipesList))
            progressBar.close()
if __name__ == '__main__':
    asyncio.run(main())
