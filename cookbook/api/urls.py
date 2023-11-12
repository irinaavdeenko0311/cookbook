from django.urls import path

from .views import (CategoriesView, IngredientsView, MenuDayView,
                    RandomRecipeView, RecipesCategoriesAsideView,
                    RecipesCategoriesSelectView, RecipesIngredientsInView,
                    RecipesIngredientsOnlyView, RecipeView)

app_name = "api"

urlpatterns = [
    path("recipes/<int:id>", RecipeView.as_view(), name="recipes_full"),
    path("random_recipe", RandomRecipeView.as_view(), name="random_recipe"),
    path("menu_day", MenuDayView.as_view(), name="menu_day"),
    path("categories", CategoriesView.as_view(), name="categories"),
    path("recipes/categories/aside", RecipesCategoriesAsideView.as_view(), name="recipes_categories_aside"),
    path("recipes/categories/select", RecipesCategoriesSelectView.as_view(), name="recipes_categories_select"),
    path("recipes/ingredients/in", RecipesIngredientsInView.as_view(), name="recipes_ingredients_in"),
    path("recipes/ingredients/only", RecipesIngredientsOnlyView.as_view(), name="recipes_ingredients_only"),
    path("ingredients", IngredientsView.as_view(), name="ingredients_startswith"),
]
