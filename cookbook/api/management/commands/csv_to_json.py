import json
import os
from csv import DictReader

from django.core.management import BaseCommand

from cookbook.settings import BASE_DIR
from api.models import Recipe

api_dir = os.path.join(BASE_DIR, "api")
data_dir = os.path.join(api_dir, "data")


always_available_ingredients = [
    "сахар",
    "соль",
    "вода",
    "перец чёрный",
    "сода",
    "масло растительное",
    "чеснок",
    "чай чёрный"
]


class Command(BaseCommand):
    """Команда для перевода данных из csv-файла в json-файл для loaddata."""

    def handle(self, *args, **options):
        with open(os.path.join(data_dir, "recipes.csv"), "r") as csv_file:
            recipes_data = DictReader(csv_file, delimiter=";")
            recipes_full = [row for row in recipes_data]

        recipes_ingredients = set()
        recipes_categories = set()

        for recipe in recipes_full:
            for recipe_ingredient in recipe.get("ingredients").split(","):
                recipes_ingredients.add(recipe_ingredient.split(":")[0])
            for recipe_category in recipe.get("categories").split(","):
                recipes_categories.add(recipe_category)

        for main_category in "завтрак", "обед", "перекус", "ужин":
            recipes_categories.add(main_category)

        recipes_ingredients = {
            ingredient: item for item, ingredient in enumerate(recipes_ingredients, 1)
        }
        recipes_categories = {
            category: item for item, category in enumerate(recipes_categories, 1)
        }

        ingredients = [
            {
                "model": "api.ingredient",
                "id": item,
                "fields": {
                    "name": ingredient,
                    "always_available": True
                    if ingredient in always_available_ingredients
                    else False
                }
            }
            for ingredient, item in recipes_ingredients.items()
        ]
        categories = [
            {"model": "api.category", "id": item, "fields": {"name": category}}
            for category, item in recipes_categories.items()
        ]

        recipes_in_db = Recipe.objects.all().values_list("id", flat=True).order_by("-id")
        last_recipe_id = recipes_in_db[0] if recipes_in_db else 0
        recipes = list()
        for item, recipe in enumerate(recipes_full, last_recipe_id + 1):
            recipe_row = {
                "model": "api.recipe",
                "id": item,
                "fields": {
                    "name": recipe.get("name"),
                    "cooking_time": recipe.get("cooking_time"),
                    "description": recipe.get("description"),
                    "categories": [
                        recipes_categories.get(category_name)
                        for category_name in recipe.get("categories").split(",")
                    ]
                }
            }
            recipes.append(recipe_row)
            count_ingredients = [
                {
                    "model": "api.countingredients",
                    "fields": {
                        "recipe_id": item,
                        "ingredient_id": recipes_ingredients.get(ingredient.split(":")[0]),
                        "count": ingredient.split(":")[1],
                        "optional": ingredient.split(":")[2]
                    }
                }
                for ingredient in recipe.get("ingredients").split(",")
            ]
            recipes.extend(count_ingredients)

        with open(
                os.path.join(data_dir, "recipes.json"), "w", encoding="utf-8"
        ) as json_file:
            json.dump(
                ingredients + categories + recipes,
                json_file,
                indent=2,
                ensure_ascii=False,
            )
