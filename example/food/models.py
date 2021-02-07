from django.db import models
from qfilter.mixins import QQueryMatchMixin

import reversion


@reversion.register()
class IngredientType(models.Model):
    """
    type of ingredient
    fruit, vegetable, pasta etc.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

@reversion.register()
class Ingredient(models.Model, QQueryMatchMixin):
    """
    ingredient
    """
    name = models.CharField(max_length=100)
    type = models.ForeignKey(IngredientType, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@reversion.register(follow=['ingredients'])
class Recipe(models.Model, QQueryMatchMixin):
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

@reversion.register()
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