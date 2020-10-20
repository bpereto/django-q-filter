from django.contrib import admin

# Register your models here.
from .models import Ingredient, IngredientType, Recipe, Cookbook

admin.site.register(Ingredient)
admin.site.register(IngredientType)
admin.site.register(Recipe)
admin.site.register(Cookbook)