# CrockPotting

## Setting up

This project has been done using Python 3.10.11 and `pipenv` as an environment manager. In order to get everything running one must install pipenv
```
    pip3 install pipenv
``` 
and then create the virtual environment. The following command must be executed on the same folder as the `Pipfile` and `Pipfile.lock` files:
```
    pipenv sync
```
Finally, once everything has been downloaded and installed one can simply execute
```
    pipenv shell
    python main.py
```
## Goals

The aim of this project is to extract all the existing recepies of a given website, https://crockpotting.es. This will be done using `selenium` to crawl and extract the data, and `tinyDb` to store the information.

## Database

I will be extracting and storing the following information from every recipe link:

- Name
- Url
- Servings
- Time
- Ingredients
- Steps
- Recommendations

TinyDb uses JSON files to store the data. Using the previous list, each element of the database will have the following structure:

```json
{
    "recipeId": 0,
    "Name": "recipeName",
    "Link": "recipeLink",
    "Servings" : 0,
    "Time": "recipeTime",
    "Ingredients": {
        "ingredientGroupName1" : [
            {"Name" : "ingredientName", "Amount": 0, "Units": "ingredientUnits"}
            {"Name" : "ingredientName", "Amount": 0, "Units": "ingredientUnits"}
        ],
        "ingredientGroupName2" : [
            {"Name" : "ingredientName", "Amount": 0, "Units": "ingredientUnits"}
            {"Name" : "ingredientName", "Amount": 0, "Units": "ingredientUnits"}
        ]
    },
    "Steps" : {
        "stepGroup1": ["Step1", "Step2"],
        "stepGroup2": ["Step1", "Step2"]
    },
    "Recommendations": "Recommendations"
}
```