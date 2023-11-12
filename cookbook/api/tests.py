from django.shortcuts import reverse
from django.test import Client, TestCase

from .models import Category, CountIngredients, Ingredient, Recipe

categories = [
    Category(id=1, name="завтрак"),
    Category(id=2, name="обед"),
    Category(id=3, name="перекус"),
    Category(id=4, name="ужин"),
    Category(id=5, name="суп"),
    Category(id=6, name="горячее блюдо"),
    Category(id=7, name="вегетарианское"),
    Category(id=8, name="мясное"),
    Category(id=9, name="напиток"),
    Category(id=10, name="салат"),
    Category(id=11, name="праздничное"),
    Category(id=12, name="сладкое"),
]
ingredients = [
    Ingredient(id=1, name="курица", always_available=False),
    Ingredient(id=2, name="вода", always_available=True),
    Ingredient(id=3, name="картофель", always_available=False),
    Ingredient(id=4, name="перец чёрный", always_available=True),
    Ingredient(id=5, name="яблоко", always_available=False),
    Ingredient(id=6, name="апельсин", always_available=False),
    Ingredient(id=7, name="соль", always_available=True),
    Ingredient(id=8, name="молоко", always_available=False),
    Ingredient(id=9, name="огурец", always_available=False),
    Ingredient(id=10, name="томат", always_available=False),
    Ingredient(id=11, name="сахар", always_available=True),
    Ingredient(id=12, name="форель", always_available=False),
    Ingredient(id=13, name="сыр", always_available=False),
]
recipes = [
    Recipe(id=1, name="рецепт1", cooking_time=30, description="апиворарв"),
    Recipe(id=2, name="рецепт2", cooking_time=30, description="укпукпукп"),
    Recipe(id=3, name="рецепт3", cooking_time=30, description="апивораыаыарв"),
    Recipe(id=4, name="рецепт4", cooking_time=30, description="ваываыва"),
    Recipe(id=5, name="рецепт5", cooking_time=30, description="аыаываыа"),
    Recipe(id=6, name="рецепт6", cooking_time=30, description="вываыаыа"),
    Recipe(id=7, name="рецепт7", cooking_time=30, description="фаыаывава"),
]
recipes_categories = {
    1: [1, 2],
    2: [1, 3, 4],
    3: [1],
    4: [1, 2, 5],
    5: [7, 8, 9],
    6: [3, 10],
    7: [5, 7],
}
count_ingredients = [
    CountIngredients(
        id=1, recipe_id=1, ingredient_id=5, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=2, recipe_id=1, ingredient_id=1, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=3, recipe_id=2, ingredient_id=13, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=4, recipe_id=2, ingredient_id=5, count="500 гр.", optional=True
    ),
    CountIngredients(
        id=5, recipe_id=3, ingredient_id=8, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=6, recipe_id=3, ingredient_id=9, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=7, recipe_id=4, ingredient_id=5, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=8, recipe_id=4, ingredient_id=12, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=9, recipe_id=5, ingredient_id=10, count="500 гр.", optional=True
    ),
    CountIngredients(
        id=10, recipe_id=5, ingredient_id=7, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=11, recipe_id=6, ingredient_id=11, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=12, recipe_id=6, ingredient_id=6, count="500 гр.", optional=True
    ),
    CountIngredients(
        id=13, recipe_id=7, ingredient_id=4, count="500 гр.", optional=False
    ),
    CountIngredients(
        id=14, recipe_id=7, ingredient_id=5, count="500 гр.", optional=False
    ),
]


class TestCookbook(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        Category.objects.bulk_create(categories)
        Ingredient.objects.bulk_create(ingredients)
        recipes_obj = Recipe.objects.bulk_create(recipes)
        for recipe_obj in recipes_obj:
            recipe_obj.categories.set(recipes_categories[recipe_obj.id])
        CountIngredients.objects.bulk_create(count_ingredients)

    def test_random_recipe(self):
        response = self.client.get(reverse("api:random_recipe"))
        self.assertEqual(response.status_code, 200)
        for value in "name", "cooking_time", "description", "ingredients":
            with self.subTest(value):
                self.assertIn(value, response.data)

    def test_recipes_full(self):
        response = self.client.get(reverse("api:recipes_full", kwargs={"id": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("name"), "рецепт1")

    def test_menu_day(self):
        response = self.client.get(reverse("api:menu_day"))
        self.assertEqual(response.status_code, 200)
        for eating in "breakfast", "lunch", "snack", "dinner":
            with self.subTest(eating):
                self.assertIn(eating, response.data)
                self.assertIsNotNone(response.data.get(eating))

    def test_categories(self):
        response = self.client.get(reverse("api:categories"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 12)

    def test_recipes_categories_aside(self):
        response = self.client.get(
            reverse("api:recipes_categories_aside"), {"categories": "1,7"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_recipes_categories_select(self):
        response = self.client.get(
            reverse("api:recipes_categories_select"), {"categories": "1,2"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_recipes_ingredients_in(self):
        response = self.client.get(
            reverse("api:recipes_ingredients_in"), {"ingredients": "5"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_recipes_ingredients_only(self):
        response = self.client.get(
            reverse("api:recipes_ingredients_only"), {"ingredients": "5"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_ingredients_startswith(self):
        response = self.client.get(
            reverse("api:ingredients_startswith"), {"startswith": "к"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
