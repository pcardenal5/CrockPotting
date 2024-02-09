import os

# Database
from tinydb import TinyDB, Query

class Database():
    
    def __init__(self, dbPath : str = './db/tiny.json') -> None:
        self.dbPath = dbPath
        
        # Check if path to database file exists
        if not os.path.exists('./db/'):
            os.makedirs('./db/')
        if not os.path.exists(self.dbPath):
            with open(self.dbPath, 'w') as databaseFile:
                databaseFile.write('')
        
        
    @property
    def database(self) -> TinyDB:                
        return TinyDB(self.dbPath)
    
    def update(self, recipeList, database: str = 'urls') -> None:
        urlTable = self.database.table(database)

        # Insert only new recepies
        crawledURLs = [element['Link'] for element in urlTable.all() if element['crawled']]
        recipeList = [recipe for recipe in recipeList if recipe != {}]
        
        newRecipes = [recipe for recipe in recipeList if recipe['Link'] not in crawledURLs and recipe != {}]
        
        if newRecipes != []:
            try:
                urlTable.insert_multiple(recipeList)
            except ValueError:
                urlTable.update_multiple(
                    [(recipe, Query().Link == recipe['Link']) for recipe in recipeList]
                )

    def getUncrawled(self) -> dict:
        return self.database.table('urls').search(Query()['crawled'] == False)