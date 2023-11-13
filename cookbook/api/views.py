from random import choice, randint
from typing import Dict, List

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import GenericAPIView, ListAPIView, QuerySet, RetrieveAPIView
from rest_framework.response import Response

from .models import Category, CountIngredients, Ingredient, Recipe
from .serializers import (CategorySerializer, IngredientAllSerializer,
                          IngredientShortSerializer, MenuDaySerializer,
                          RecipeFullSerializer, RecipeShortSerializer)


class RandomRecipeView(RetrieveAPIView):
    """Получение случайного рецепта."""

    serializer_class = RecipeFullSerializer

    def get_object(self) -> Recipe:
        count = Recipe.objects.count()
        random_id = randint(1, count)
        return Recipe.objects.get(id=random_id)


class RecipeView(RetrieveAPIView):
    """Получение рецепта по id."""

    serializer_class = RecipeFullSerializer

    def get_object(self) -> Recipe:
        recipe_id = self.kwargs.get("id")
        return Recipe.objects.get(id=recipe_id)


class MenuDayView(RetrieveAPIView):
    """Получение меню на день."""

    serializer_class = MenuDaySerializer

    def get_object(self) -> Dict[str, Recipe]:
        return {
            "breakfast": self.get_recipe("завтрак"),
            "lunch": self.get_recipe("обед"),
            "snack": self.get_recipe("перекус"),
            "dinner": self.get_recipe("ужин"),
        }

    @staticmethod
    def get_recipe(name: str) -> Recipe:
        return choice(Recipe.objects.filter(categories__name=name))


class CategoriesView(ListAPIView):
    """Получение всех категорий блюд."""

    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet:
        return Category.objects.all().order_by("name")


@extend_schema(parameters=[OpenApiParameter(name="categories", default="1,2,3")])
class RecipesCategoriesAsideView(ListAPIView):
    """Получение отдельных блюд из выбранных категорий."""

    serializer_class = RecipeShortSerializer

    def get_queryset(self) -> QuerySet:
        categories = self.request.query_params.get("categories").split(",")
        return Recipe.objects.filter(categories__id__in=categories).distinct()


@extend_schema(parameters=[OpenApiParameter(name="categories", default="1,2,3")])
class RecipesCategoriesSelectView(ListAPIView):
    """Получение блюд, совпадающих по всем категориям сразу."""

    serializer_class = RecipeShortSerializer

    def get_queryset(self) -> List[Recipe]:
        categories = [
            int(category)
            for category in self.request.query_params.get("categories").split(",")
        ]
        recipes = Recipe.objects.filter(categories__id__in=categories).distinct()
        return [
            recipe
            for recipe in recipes
            if set([category.id for category in recipe.categories.all()])
               >= set(categories)
        ]


@extend_schema(parameters=[OpenApiParameter(name="startswith", default="а",)])
class IngredientsView(RetrieveAPIView):
    """Получение всех ингредиентов по первой букве."""

    serializer_class = IngredientAllSerializer

    def get_object(self):
        ingredients_symbol = {symbol: list() for symbol in "абвгдежзийклмнопрстуфхцчшщэюя"}
        for ingredient in self.get_queryset():
            ingredients_symbol[ingredient.name[0]].append(ingredient)
        return ingredients_symbol

    def get_queryset(self):
        return Ingredient.objects.all().order_by("name")


@extend_schema(parameters=[OpenApiParameter(name="ingredients", default="1,2,3",)])
class RecipesIngredientsInView(ListAPIView):
    """Получение блюд с содержанием выбранных ингредиентов."""

    serializer_class = RecipeShortSerializer

    def get_queryset(self) -> List[Recipe]:
        need_ingredients = [
            int(ingredient)
            for ingredient in self.request.query_params.get("ingredients").split(",")
        ]
        count_ingredients = CountIngredients.objects.filter(
            ingredient_id__in=need_ingredients
        )

        recipes_ingredients = dict()
        for recipe_ingredient in count_ingredients:
            recipes_ingredients.setdefault(recipe_ingredient.recipe, list())
            recipes_ingredients[recipe_ingredient.recipe].append(
                recipe_ingredient.ingredient.id
            )

        return [
            recipe
            for recipe, ingredients in recipes_ingredients.items()
            if set(ingredients) >= set(need_ingredients)
        ]


@extend_schema(parameters=[OpenApiParameter(name="ingredients", default="1,2,3",)])
class RecipesIngredientsOnlyView(ListAPIView):
    """Получение блюд с содержанием только выбранных ингредиентов."""

    serializer_class = RecipeShortSerializer

    def get_queryset(self) -> List[Recipe]:
        need_ingredients = [
            int(ingredient)
            for ingredient in self.request.query_params.get("ingredients").split(",")
        ]
        recipes = Recipe.objects.filter(ingredients__id__in=need_ingredients).distinct()
        select_recipes = list()

        for recipe in recipes:
            ingredients = [
                ingredient.id for ingredient in recipe.ingredients.all()
                if (
                    not ingredient.count_ingredient.filter(recipe=recipe)
                    .first().optional
                    and not ingredient.always_available
                )
            ]
            if set(ingredients) == set(need_ingredients):
                select_recipes.append(recipe)
        return select_recipes
