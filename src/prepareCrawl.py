# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
import selenium.common.exceptions

# Logging
import logging
logging.basicConfig(encoding='utf-8', level=logging.INFO)

# Utils
import time

class PrepareCrawl():
    
    def __init__(self, driver: FirefoxWebDriver, mainUrl: str) -> None:
        self.driver = driver
        self.mainUrl = mainUrl
        
    def getUrls(self) -> list:
        '''
            Exports all URLs and recipe names
        '''
        
        driver = self.driver        
        
        logging.info('Loading main page')
        driver.get(self.mainUrl)
        time.sleep(5)

        try:
            acceptCookiesButton = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/button[2]')
            acceptCookiesButton.click()
            logging.info('Cookies warning removed')
        except:
            pass

        recipeColumns = driver.find_elements(By.CLASS_NAME, 'azindex')


        recipes = []
        for recipeColumn in recipeColumns:
            recipeList = recipeColumn.find_element(By.TAG_NAME, 'ul')
            
            for recipe in recipeList.find_elements(By.TAG_NAME, 'li'):
                # Some elements may not have a link
                try:
                    recipeElement = recipe.find_element(By.TAG_NAME, 'a')
                    recipeName = recipeElement.text
                    
                    try:
                        recipeLink = recipeElement.get_attribute('href')
                        
                        recipeId = abs(hash(recipeLink))
                        
                        if (not recipeLink.endswith('/#azindex-1')):
                            recipes.append({'recipeId' : recipeId, 'Name' : recipeName, 'Link' : recipeLink})

                    except:
                        logging.warning(f'No link found for {recipeName}')
                        
                except:
                    pass
      
        return recipes

    def getData(self, recipe: dict) -> dict:
        '''
            Given an element of the database, extracts the ingredients, productions and recommendations.
        '''
        url = recipe['Link']
        driver = self.driver
        driver.get(url)
        logging.info('Main link extracted')
        time.sleep(10)
        
        
        try:
            acceptCookiesButton = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/button[2]')
            acceptCookiesButton.click()
            logging.info('Cookies warning removed')
        except:
            pass
        
        #########################################
        #                Portions               #
        #########################################

        height = 1500
        driver.execute_script(f"window.scrollTo(0, {height})")
        servingsLink = driver.find_element(By.CLASS_NAME, 'wprm-recipe-servings-link')
        recipe['Portions'] = servingsLink.find_element(By.TAG_NAME, 'span').text

        logging.info('Recipe portions extracted')
        
        #########################################
        #              Cooking time             #
        #########################################
        
        cookingTime = driver.find_element(By.CLASS_NAME, 'wprm-recipe-time')
        cookingTimeHours =   cookingTime.find_element(By.XPATH, '//*[@class="wprm-recipe-details wprm-recipe-details-hours wprm-recipe-total_time wprm-recipe-total_time-hours"]').text.replace('\n',' ')
        cookingTimeMinutes = cookingTime.find_element(By.XPATH, '//*[@class="wprm-recipe-details wprm-recipe-details-minutes wprm-recipe-total_time wprm-recipe-total_time-minutes"]').text.replace('\n',' ')
        
        recipe['Time'] = f'{cookingTimeHours} {cookingTimeMinutes}'
        logging.info('Cooking time extracted')
        
        #########################################
        #              Ingredients              #
        #########################################
        
        Ingredients = []
        # First one must loop over all the different groups
        for ingredientGroup in driver.find_elements(By.CLASS_NAME, 'wprm-recipe-ingredient-group'):
            ingredientGroupDict ={}
            try:
                # If there is more than one group, here we get its title
                title = ingredientGroup.find_element(By.TAG_NAME, 'h4').text
                title = title.split(' ')[-1].title()
            except:
                title = 'Ingredientes'
                        
            # Then we can get all the different ingredients
            # Each one will be one element of a list[dict]
            ingredientList = []
            for ingredient in ingredientGroup.find_elements(By.TAG_NAME, 'li'):
                ingredientDict = {}
                
                ingredientDict['name'] = ingredient.find_element(By.CLASS_NAME, 'wprm-recipe-ingredient-name').text

                # Sometimes there is no amount 
                try:
                    ingredientDict['amount'] = ingredient.find_element(By.CLASS_NAME, 'wprm-recipe-ingredient-amount').text
                except selenium.common.exceptions.NoSuchElementException:
                    ingredientDict['amount'] = ''
                
                # Sometimes there are no units (1 clove of garlic)
                try:
                    ingredientDict['unit'] = ingredient.find_element(By.CLASS_NAME, 'wprm-recipe-ingredient-unit').text
                except selenium.common.exceptions.NoSuchElementException:
                    ingredientDict['unit'] = ''

                # Sometimes there are notes
                try:
                    ingredientDict['notes'] = ingredient.find_element(By.CSS_SELECTOR, '.wprm-recipe-ingredient-notes.wprm-recipe-ingredient-notes-normal').text
                except selenium.common.exceptions.NoSuchElementException:
                    ingredientDict['notes'] = ''
                
                
                
                ingredientList.append(ingredientDict)
            
            ingredientGroupDict[title] = ingredientList
            
            Ingredients.append(ingredientGroupDict)
            
        # Finally, one can add the ingredients to the recipe
        recipe['Ingredients'] = Ingredients
        logging.info('Ingredients extracted')
        
        #########################################
        #                 Steps                 #
        #########################################
        
        # The process to get the steps is quite similar to the ingredients. In this case, we will not need to use 
        # dicts to store the data as the steps will be simply strings.
        for stepGroup in driver.find_elements(By.CLASS_NAME, 'wprm-recipe-instruction-group'):
            # Each stepList 
            stepGroupDict ={}
            try:
                # If there is more than one group, here we get its title
                title = stepGroup.find_element(By.TAG_NAME, 'h4').text
                title = title.split(' ')[-1].title()
            except:
                title = 'Elaboración'
            
        
        return recipe