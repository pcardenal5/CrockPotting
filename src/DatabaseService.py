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

    def upsert(self, recipeList, collection : str) -> None:
        recipeColletion = self.database.table(collection)

        recipeList = [recipe for recipe in recipeList if recipe != {}]

        for recipe in recipeList:
            recipeColletion.upsert(recipe, Query().Link == recipe['Link'])