from bs4 import BeautifulSoup
import aiohttp


# Logging
from src.LogService import LogService

# Utils
import time

class CrawlService():

    def __init__(self, mainUrl: str, logs: LogService) -> None:
        self.mainUrl = mainUrl
        self.logs = logs

    async def getUrls(self, session: aiohttp.ClientSession) -> list:
        '''
            Exports all URLs and recipe names
        '''

        self.logs.sendInfo('Loading main page')
        async with session.get(self.mainUrl) as response:
            recipeIndex = await response.text()
        soup = BeautifulSoup(recipeIndex, 'html.parser')

        recipeColumns = soup.find_all("div", class_ =  'azindex')


        recipes = []
        for recipe in recipeColumns[0].find_all_next('li'):
            # Some elements may not have a link
            try:
                recipeElement = recipe.find('a')
                recipeName = recipeElement.text
                
                try:
                    recipeLink = recipeElement['href']
                    
                    
                    if (not recipeLink.endswith('#azindex-1')):
                        recipes.append({'Name' : recipeName, 'Link' : recipeLink, 'crawled' : False})

                except:
                    self.logs.sendWarning(f'No link found for {recipeName}')
                    
            except:
                pass

        return recipes

    async def getData(self, session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
        '''
        Asynchronously gets the text from a given page
        '''
        try:
            async with session.get(url) as response:
                recipeHTML = await response.text()
                # Create recipe dict from scratch, no need for order
                return self.processRecipePage(BeautifulSoup(recipeHTML, 'html.parser'), recipe = {'Link': url})
        except aiohttp.client_exceptions.InvalidURL:
            return {}

    def processRecipePage(self, soup: BeautifulSoup, recipe : dict) -> dict:
        '''
            Extracts the ingredients, productions and recommendations from a bs4 soup
        '''
        # First, check if recipe has ingredients. If it doesn't, exit early
        # Variable used later. I will only consider a recipe is crawled if it has ingredients
        ingredientGroups = soup.find_all("div", class_ = 'wprm-recipe-ingredient-group')
        if not ingredientGroups:
            return {}
        recipe['crawled'] = True

        #########################################
        #              Recipe Name              #
        #########################################
        try:
            recipe['Name'] = soup.find(class_ = 'entry-title').text
        except:
            # It it has no name, return empty
            return {}


        #########################################
        #     Cooking and elaboration times     #
        #########################################

        try:

            try:
                cookingTimeDays = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-days wprm-recipe-cook_time wprm-recipe-cook_time-days').text.replace('\n',' ')
            except:
                cookingTimeDays = ''

            try:
                cookingTimeHours = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-hours wprm-recipe-cook_time wprm-recipe-cook_time-hours').text.replace('\n',' ')
            except:
                cookingTimeHours = ''

            try:
                cookingTimeMinutes = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-minutes wprm-recipe-cook_time wprm-recipe-cook_time-minutes').text.replace('\n',' ')
            except:
                cookingTimeMinutes = ''

            recipe['CookingTime'] = f'{cookingTimeDays} {cookingTimeHours} {cookingTimeMinutes}'.strip()

        except:
            recipe['CookingTime'] = ''


        try:
            try:
                preparationTimeDays = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-days wprm-recipe-prep_time wprm-recipe-prep_time-days').text.replace('\n',' ')
            except:
                preparationTimeDays = ''

            try:
                preparationTimeHours = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-hours wprm-recipe-prep_time wprm-recipe-prep_time-hours').text.replace('\n',' ')
            except:
                preparationTimeHours = ''

            try:
                preparationTimeMinutes = soup.find("span", class_ = 'wprm-recipe-details wprm-recipe-details-minutes wprm-recipe-prep_time wprm-recipe-prep_time-minutes').text.replace('\n',' ')
            except:
                preparationTimeMinutes = ''

            recipe['PreparationTime'] = f'{preparationTimeDays} {preparationTimeHours} {preparationTimeMinutes}'.strip()

        except:
            recipe['PreparationTime'] = ''

        #########################################
        #              Ingredients              #
        #########################################

        Ingredients = {}
        # First one must loop over all the different groups
        for ingredientGroup in ingredientGroups:

            try:
                # If there is more than one group, here we get its title
                title = ingredientGroup.find('h4').text
                title = title.split(' ')[-1].title()
            except:
                title = 'Ingredientes'

            # Then we can get all the different ingredients
            # Each one will be one element of a list[dict]
            ingredientList = []
            for ingredient in ingredientGroup.find_all_next('li',recursive=False):
                ingredientDict = {}
                try:
                    ingredientDict['name'] = ingredient.find(class_ = 'wprm-recipe-ingredient-name').text
                except:
                    pass


                # Sometimes there is no amount
                try:
                    ingredientDict['amount'] = ingredient.find(class_ = 'wprm-recipe-ingredient-amount').text
                except:
                    pass

                # Sometimes there are no units (1 clove of garlic)
                try:
                    ingredientDict['unit'] = ingredient.find(class_ = 'wprm-recipe-ingredient-unit').text
                except:
                    pass

                # Sometimes there are notes
                try:
                    ingredientDict['notes'] = ingredient.find(class_ = 'wprm-recipe-ingredient-notes wprm-recipe-ingredient-notes-normal').text
                except:
                    pass

                # The find all next also detects li elements we don't really want
                if ingredientDict == {}:
                    break


                ingredientList.append(ingredientDict)

            Ingredients[title] = ingredientList

        # Finally, one can add the ingredients to the recipe
        recipe['Ingredients'] = Ingredients

        #########################################
        #                 Steps                 #
        #########################################

        # The process to get the steps is quite similar to the ingredients. In this case, we will not need to use
        # dicts to store the data as the steps will be simply strings.
        Steps = {}
        for stepGroup in soup.find_all(class_ = 'wprm-recipe-instruction-group'):

            try:
                # If there is more than one group, here we get its title
                title = stepGroup.find('h4').text
                title = title.split(' ')[-1].title()
            except:
                title = 'Elaboración'

            stepList = []
            for step in stepGroup.find_all_next('li', recursive=False):
                try:
                    step = step.find(class_ = 'wprm-recipe-instruction-text').text
                    stepList.append(step)
                except:
                    pass

            Steps[title] = stepList

        recipe['Steps'] = Steps


        #########################################
        #            Recommendations            #
        #########################################

        # Finally, the recipe recommendations

        try:
            recipe['Recommendations'] = soup.find(class_ = 'wprm-recipe-notes').text.replace('\n',' ')
        except:
            pass

        return recipe