from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from .models import Recipe
from qfilter.mixins import QQueryViewMixin


class RecipeListView(QQueryViewMixin, ListView):
    """
    Recipe List View
    """
    model = Recipe
    template_name = 'food/recipe_list.html'
    ordering = ['name']