from django.core.validators import MinValueValidator
from django.db import models


class Ingredient(models.Model):
    """Модель, описывающая ингредиент блюда."""

    name = models.CharField(max_length=30, null=False)
    always_available = models.BooleanField(
        db_comment="Ингредиент, который всегда есть дома (н-р, соль, перец и т.п.).",
        default=0,
    )

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    """Модель, описывающая категорию блюда."""

    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """Модель, описывающая рецепт приготовления блюда."""

    name = models.CharField(max_length=30)
    cooking_time = models.PositiveIntegerField(
        db_comment="Время приготовления в минутах.", validators=[MinValueValidator(1)]
    )
    description = models.TextField(db_comment="Рецепт приготовления.")
    ingredients = models.ManyToManyField(Ingredient, through="CountIngredients")
    categories = models.ManyToManyField(Category)
    image = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class CountIngredients(models.Model):
    """Модель, описывающая количество ингредиента в конкретном рецепте."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="count_ingredient"
    )
    count = models.CharField(max_length=20)
    optional = models.BooleanField(
        db_comment="Ингредиент, необязательный в рецепте (н-р, для подачи)", default=0
    )

    def __str__(self):
        return f"{self.recipe.name}-{self.ingredient.name}"
