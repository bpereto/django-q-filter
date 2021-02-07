from django.contrib import admin
import reversion
from reversion.admin import VersionAdmin

# Register your models here.
from .models import Ingredient, IngredientType, Recipe, Cookbook

admin.site.register(Ingredient, VersionAdmin)
admin.site.register(IngredientType, VersionAdmin)
admin.site.register(Recipe, VersionAdmin)
admin.site.register(Cookbook, VersionAdmin)