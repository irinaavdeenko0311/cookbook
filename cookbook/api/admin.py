from csv import DictReader
from io import TextIOWrapper
from typing import List

from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from .models import Category, CountIngredients, Ingredient, Recipe


class CSVForm(forms.Form):
    """Форма для загрузки файла CSV."""

    csv_file = forms.FileField()


class BaseAdmin(admin.ModelAdmin):
    """Базовое представление модели административной панели."""

    change_list_template = "csv_changelist.html"

    def path_model_name(self) -> str:
        """Название модели для формирования динамического пути."""

        pass

    def changelist_view(self, request, extra_context=None):
        """
        Добавление в контекст переменной с названием модели.

        Необходимо для формирования динамической ссылки.
        """

        extra_context = extra_context or dict()
        extra_context["name"] = self.path_model_name()
        return super(BaseAdmin, self).changelist_view(request, extra_context)

    def get_urls(self) -> List[str]:
        """Добавление нового роута."""

        urls = super().get_urls()
        urls.pop(-1)
        new_urls = [path("import-csv/", self.import_data_from_csv)]
        return urls + new_urls

    def upload_data_to_db(self, csv_file: TextIOWrapper) -> bool:
        """Функция для добавления данных из файла в БД."""

        pass

    def import_data_from_csv(self, request: HttpRequest) -> HttpResponse:
        """Функция для загрузки данных из файла."""

        if request.method == "GET":
            form = CSVForm()
            return render(
                request=request, template_name="csv_form.html", context={"form": form}
            )

        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(
                form.files["csv_file"].file, encoding=request.encoding
            )

            result = self.upload_data_to_db(csv_file)

            if result:
                message = "Data from the csv-file successfully uploaded to db."
                level = 20
            else:
                message = "Data from the csv-file not uploaded to db."
                level = 40
            self.message_user(request, message, level)
            return redirect("..")


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    """Модель административной панели, описывающая ингредиент блюда."""

    list_display = "id", "name", "always_available"
    list_display_links = "id", "name"

    def path_model_name(self) -> str:
        return "ingredient"

    def upload_data_to_db(self, csv_file: TextIOWrapper) -> bool:
        current_ingredients = Ingredient.objects.all().values_list("name", flat=True)
        reader = DictReader(csv_file)
        ingredients = [
            Ingredient(**row)
            for row in reader
            if row["name"] not in current_ingredients
        ]
        return len(Ingredient.objects.bulk_create(ingredients)) > 0


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    """Модель административной панели, описывающая категорию блюда."""

    list_display = "id", "name"
    list_display_links = "id", "name"

    def path_model_name(self) -> str:
        return "category"

    def upload_data_to_db(self, csv_file: TextIOWrapper) -> bool:
        current_categories = Category.objects.all().values_list("name", flat=True)
        reader = DictReader(csv_file)
        categories = [
            Category(**row) for row in reader if row["name"] not in current_categories
        ]
        return len(Category.objects.bulk_create(categories)) > 0


class CountIngredientsInline(admin.TabularInline):
    model = CountIngredients


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    """Модель административной панели, описывающая рецепт приготовления блюда."""

    list_display = "id", "name"
    list_display_links = "id", "name"
    inlines = [CountIngredientsInline]

    def path_model_name(self) -> str:
        return "recipe"

    def upload_data_to_db(self, csv_file: TextIOWrapper) -> bool:
        always_available_ingredients = [
            "сахар",
            "соль",
            "вода",
            "перец чёрный",
            "сода",
            "масло растительное",
            "чеснок",
            "чай чёрный",
        ]

        reader = DictReader(csv_file, delimiter=";")
        recipes_full = [row for row in reader]

        current_categories = {
            category.name: category.id for category in Category.objects.all()
        }
        current_ingredients = {
            ingredient.name: ingredient.id for ingredient in Ingredient.objects.all()
        }

        recipes_ingredients = set()
        recipes_categories = set()

        for recipe in recipes_full:
            for recipe_ingredient in recipe.get("ingredients").split(","):
                ingredient = recipe_ingredient.split(":")[0]
                if ingredient not in current_ingredients:
                    recipes_ingredients.add(ingredient)
            for recipe_category in recipe.get("categories").split(","):
                if recipe_category not in current_categories:
                    recipes_categories.add(recipe_category)

        ingredients = [
            Ingredient(
                name=ingredient,
                always_available=True
                if ingredient in always_available_ingredients
                else False,
            )
            for ingredient in recipes_ingredients
        ]

        categories_obj = Category.objects.bulk_create(
            [Category(name=category) for category in recipes_categories]
        )
        categories_id = {
            category_obj.name: category_obj.id for category_obj in categories_obj
        }
        current_categories.update(**categories_id)
        ingredients_obj = Ingredient.objects.bulk_create(ingredients)
        ingredients_id = {
            ingredient_obj.name: ingredient_obj.id for ingredient_obj in ingredients_obj
        }
        current_ingredients.update(**ingredients_id)

        recipes = [
            {
                "recipe_obj": Recipe.objects.create(
                    name=recipe.get("name"),
                    cooking_time=recipe.get("cooking_time"),
                    description=recipe.get("description"),
                ),
                "recipe_data": recipe,
            }
            for recipe in recipes_full
        ]
        for recipe in recipes:
            for category in recipe["recipe_data"]["categories"].split(","):
                recipe["recipe_obj"].categories.add(current_categories[category])
                recipe["recipe_obj"].save()

            for ingredient in recipe["recipe_data"]["ingredients"].split(","):
                ingredient_info = ingredient.split(":")
                CountIngredients.objects.create(
                    recipe_id=recipe["recipe_obj"].id,
                    ingredient_id=current_ingredients[ingredient_info[0]],
                    count=ingredient_info[1],
                    optional=ingredient_info[2],
                )

        return len(recipes) > 0
