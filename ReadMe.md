# CrockPotting

## Setting up

This project has been done using Python 3.10.11 and `pipenv` as an environment manager. In order to get everything running one must install pipenv
```bash
    pip3 install pipenv
```
and then create the virtual environment. To do that, the following command must be executed on the same folder as the `Pipfile` and `Pipfile.lock` files:
```bash
    pipenv sync
```

Before running anythin, change the global settings using the `AppConfig.json` file:

- `GET_URLS` : Boolean, indicates whether or not to get all the URLS in the index page. Set to `true` on the first execution.
- `CRAWL_ALL` :  Boolean, indicates whether or not to extract the recipes from the crawled URLs.
- `BATCH_SIZE` : Ineteger, sets the size for the `aiohttp` Client Session.
- `OUTPUT_PATH` : String, path to the folder where you want to store the recipes in Markdown format.

## Execution

Finally, to crawl the recipes run
```bash
    pipenv run python main.py
```

Then, if you want to save the recipes as Markdown files (I have used [Obsidian](https://obsidian.md/) to index and displaying them), run
```bash
    pipenv run python ToMarkdown.py
```

## Goals

The aim of this project is to extract all the existing recepies of a given website, https://crockpotting.es. This will be done using `asyncio` and `aiohttp` to get the html text, `bs4` to parse and extarct the data, and `tinyDb` to store the information.

## Database

I will be extracting and storing the following information from every recipe link:

- Name
- Url
- Time
- Ingredients
- Steps
- Recommendations

TinyDb uses JSON files to store the data. Using the previous list, each element of the database will have the following structure:

```json
{
    "Name": "recipeName",
    "Link": "recipeLink",
    "CookingTime": "CookingTime",
    "PreparationTime": "PreparationTime",
    "Ingredients": {
        "ingredientGroupName1" : [
            {"name" : "ingredientName", "amount": 0, "unit": "ingredientUnits", "notes": "ingredientNotes"}
            {"name" : "ingredientName", "amount": 0, "unit": "ingredientUnits", "notes": "ingredientNotes"}
        ],
        "ingredientGroupName2" : [
            {"name" : "ingredientName", "amount": 0, "unit": "ingredientUnits", "notes": "ingredientNotes"}
            {"name" : "ingredientName", "amount": 0, "unit": "ingredientUnits", "notes": "ingredientNotes"}
        ]
    },
    "Steps" : {
        "stepGroup1": ["Step1", "Step2"],
        "stepGroup2": ["Step1", "Step2"]
    },
    "Recommendations": "Recommendations"
}
```