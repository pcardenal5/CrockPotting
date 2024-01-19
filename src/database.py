import os

# Database
from tinydb import TinyDB, Query

class Database():
    
    def __init__(self, dbPath : str) -> None:
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
    
    def update(self, recipeList) -> None:
        urlTable = self.database.table('urls')

        # Insert only new recepies
        crawledURLs = [element['recipeId'] for element in urlTable.all() if element['crawled']]
        
        newRecipes = [recipe for recipe in recipeList if recipe['recipeId'] not in crawledURLs]
        
        if newRecipes != []:
            try:
                urlTable.insert_multiple(recipeList)
            except ValueError:
                urlTable.update_multiple(
                    [(recipe, Query().recipeId == recipe['recipeId']) for recipe in recipeList]
                )