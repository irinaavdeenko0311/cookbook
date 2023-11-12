from rest_framework.serializers import ModelSerializer, Serializer

from .models import Category, CountIngredients, Ingredient, Recipe


class IngredientNameSerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели Ingredient. Только название."""

    class Meta:
        model = Ingredient
        fields = ("name",)


class IngredientShortSerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели Ingredient. Id и название."""

    class Meta:
        model = Ingredient
        fields = "id", "name"


class CountIngredientsSerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели CountIngredients."""

    ingredient = IngredientNameSerializer()

    class Meta:
        model = CountIngredients
        fields = "count", "ingredient"


class RecipeShortSerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели Recipe. Краткая информация о рецепте."""

    class Meta:
        model = Recipe
        fields = "id", "name"


class RecipeFullSerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели Recipe. Полная информация о рецепте."""

    ingredients = CountIngredientsSerializer(source="countingredients_set", many=True)

    class Meta:
        model = Recipe
        fields = "name", "cooking_time", "description", "ingredients", "image"


class CategorySerializer(ModelSerializer):
    """Сериализатор для преобразования данных модели Category."""

    class Meta:
        model = Category
        fields = "id", "name"


class MenuDaySerializer(Serializer):
    """Сериализатор для представления меню на день."""

    breakfast = RecipeFullSerializer()
    lunch = RecipeFullSerializer()
    snack = RecipeFullSerializer()
    dinner = RecipeFullSerializer()
