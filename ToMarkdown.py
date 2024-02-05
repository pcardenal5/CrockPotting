import os
import json
from tqdm import tqdm
import re

from src.DatabaseService import Database

def tryGet(inputDict, key, onFail: str = ''):
    try:
        return inputDict[key]
    except KeyError:
        return onFail

# Load app configuration
with open('./AppConfig.json') as inputFile:
    config = json.load(inputFile)

# Set output directory
OUTPUT_PATH = config['OUTPUT_PATH']
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

db = Database()
recipeDb = db.database.table('urls').all()


# Loop through all the recipes 
for i in tqdm(range(len(recipeDb))):
    recipe = recipeDb[i]
    # I will first build the text to write into the file and only then I will write it 
    recipeMarkdown = ''
    
    # Set recipe headers    
    recipeMarkdown += f'''# {recipe["Name"]}
---
## Información básica
- Enlace a la receta original: {recipe["Link"]}
- Tiempo total de elaboración y cocinado: {recipe["Time"]}
---
## Ingredientes
'''
    recipeIngredients = dict(recipe["Ingredients"])
    ingredientsText = ''
    for ingredientName in recipeIngredients.keys():
        ingredientGroup = recipeIngredients[ingredientName]
        
        if ingredientName != 'Ingredientes':
            ingredientsText += f'### {ingredientName}\n'
        # ingredientGroup is an array of ingredients
        for ingredient in ingredientGroup:
            # I use tryGet because the ingredients don't always have the same keys
            iName = tryGet(ingredient, 'name')
            iAmount = tryGet(ingredient, 'amount')
            iUnit = tryGet(ingredient, 'unit')
            iNotes = tryGet(ingredient, 'notes')
            ingredientsText += f'- {iAmount} {iUnit} {iName} ({iNotes})\n'
        #There may be a fancier way to do this with reges, but couldn't get it to work
        ingredientsText = ingredientsText.replace('  ', ' ').replace('  ', ' ').replace('()','')

    # Add ingredient list
    recipeMarkdown += ingredientsText

    # Add Steps 
    recipeMarkdown += '## Elaboración\n'
    recipeSteps = dict(recipe["Steps"])
    stepsText = ''
    for stepName in recipeSteps.keys():
        stepGroup = recipeSteps[stepName]
        
        if stepName != 'Elaboración':
            recipeMarkdown += f'### {stepName}\n'
        # stepGroup is an array of Steps. Loop ober them and add to string
        c = 1
        for step in stepGroup:
            stepsText += f'{c}. {step}\n'
            c+=1
        stepsText = stepsText.replace('  ', ' ').replace('  ', ' ').replace('()','')
    recipeMarkdown += stepsText

    # Remove special characters from the name and save the file
    rName = re.sub(r'\||\?|¿', '', recipe['Name'])
    recipePath = os.path.join(OUTPUT_PATH, rName)
    with open(recipePath +'.md', 'w', encoding = 'utf-8') as outputFile:
        outputFile.write(recipeMarkdown)