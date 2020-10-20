from django.db import models


class IngredientType(models.Model):
    """
    type of ingredient
    fruit, vegetable, pasta etc.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    ingredient
    """
    name = models.CharField(max_length=100)
    type = models.ForeignKey(IngredientType, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    recipe with ingredients
    """
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ingredients = models.ManyToManyField(Ingredient)
    cook_time = models.IntegerField()

    def __str__(self):
        return self.name


class Cookbook(models.Model):
    """
    cookbook which has recipes.
    """
    name = models.CharField(max_length=100)
    recipes = models.ManyToManyField(Recipe)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name