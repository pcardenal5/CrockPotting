# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver

# Database
from tinydb import TinyDB, Query

# Logging
import logging

# Utils
import time

class prepareCrawl():
    
    def __init__(self, driver: FirefoxWebDriver, dbPath: str, mainUrl) -> None:
        self.driver = driver
        self.dbPath = dbPath
        self.mainUrl = mainUrl
        
    def getUrls(self) -> dict:
        '''
            Exports all URLs and recipe names
        '''
        
        driver = self.driver        
        
        # Get all URLs on main page
        logging.info('Loading main page')
        driver.get(self.mainUrl)

        # Remove cookies
        # They don't always appear, though 
        time.sleep(5)
        try:
            cookies = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/button[2]')
            cookies.click()
            logging.info('Cookies warning removed')
        except:
            pass

        # There are two lists with recepies, so one must loop over both to get all links
        recipeLists = driver.find_elements(By.CLASS_NAME, 'azindex')

        recipeId = 0
        recipeDict = {}

        for recipeList in recipeLists:
            recipeList = recipeList.find_element(By.TAG_NAME, 'ul')
            recipes = recipeList.find_elements(By.TAG_NAME, 'li')
            for recipe in recipes:
                # Not all recepie links are creted equal
                try:
                    recipeElement = recipe.find_element(By.TAG_NAME, 'a')
                    recipeName = recipeElement.text
                    
                    try:
                        recipeLink = recipeElement.get_attribute('href')
                    except:
                        recipeLink = ''
                        logging.warning(f'No href found for {recipeName}')
                    
                    
                    if (not recipeLink.endswith('/#azindex-1')):
                        recipeDict[recipeId] = {'recipeName' : recipeName, 'recipeLink' : recipeLink}
                        recipeId += 1
                        
                except:
                    pass
                    
        return recipeDict

            