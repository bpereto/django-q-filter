"""
unit tests for django q filter
"""

# pylint: disable=invalid-name,line-too-long,anomalous-backslash-in-string

__all__ = (
    'QQueryMatchTestCase',
)

from unittest import TestCase

from django.db.models import Q

from ..models import Ingredient, IngredientType


class QQueryMatchTestCase(TestCase):
    """
    Test cases for the QFilter
    """

    def setUp(self):

        ing_type = IngredientType.objects.get(name='spice')
        self.obj, _ = Ingredient.objects.get_or_create(name='pepper', type=ing_type)

    def test_exact_qquery(self):
        """
        test simple qquery
        """

        # exact true
        m = self.obj.match(Q(name='pepper'))
        self.assertTrue(m)

        # exact false
        m = self.obj.match(Q(name='onion'))
        self.assertFalse(m)

        # exact negated
        m = self.obj.match(~Q(name='pepper'))
        self.assertFalse(m)

    def test_startswith_query(self):
        """
        test simple qquery
        """

        # startswith true
        m = self.obj.match(Q(name__startswith='p'))
        self.assertTrue(m)

        # startswith false
        m = self.obj.match(Q(name__startswith='x'))
        self.assertFalse(m)

        # startswith negated
        m = self.obj.match(~Q(name__startswith='p'))
        self.assertFalse(m)

    def test_endswith_query(self):
        """
        test simple qquery
        """

        # endswith true
        m = self.obj.match(Q(name__endswith='r'))
        self.assertTrue(m)

        # endswith false
        m = self.obj.match(Q(name__endswith='x'))
        self.assertFalse(m)

        # endswith negated
        m = self.obj.match(~Q(name__endswith='r'))
        self.assertFalse(m)

    def test_lt_query(self):
        """
        test simple qquery
        """

        # lt true
        m = self.obj.recipe_set.first().match(Q(cook_time__lt=60))
        self.assertTrue(m)

        # lt false
        m = self.obj.recipe_set.first().match(Q(cook_time__lt=30))
        self.assertFalse(m)

        # lt negated
        m = self.obj.recipe_set.first().match(~Q(cook_time__lt=60))
        self.assertFalse(m)

    def test_gt_query(self):
        """
        test simple qquery
        """

        # gt true
        m = self.obj.recipe_set.first().match(Q(cook_time__gt=10))
        self.assertTrue(m)

        # gt false
        m = self.obj.recipe_set.first().match(Q(cook_time__gt=60))
        self.assertFalse(m)

        # gt negated
        m = self.obj.recipe_set.first().match(~Q(cook_time__gt=5))
        self.assertFalse(m)

    def test_gte_query(self):
        """
        test simple qquery
        """

        # gte true
        m = self.obj.recipe_set.first().match(Q(cook_time__gte=45))
        self.assertTrue(m)

        # gt false
        m = self.obj.recipe_set.first().match(Q(cook_time__gte=60))
        self.assertFalse(m)

        # gt negated
        m = self.obj.recipe_set.first().match(~Q(cook_time__gte=5))
        self.assertFalse(m)

    def test_isnull_query(self):
        """
        test simple qquery
        """

        # isnull true
        m = self.obj.match(Q(type__isnull=False))
        self.assertTrue(m)

        # isnull false
        m = self.obj.match(Q(type__isnull=False))
        #self.assertFalse(m)

        # isnull negated
        m = self.obj.match(~Q(type__isnull=False))
        self.assertFalse(m)

    def test_related_qquery(self):
        # exact related
        m = self.obj.match(Q(type__name='spice'))
        self.assertTrue(m)

    def test_complex_qquery(self):

        m = self.obj.match(Q(Q(name__startswith='p') & Q(name__endswith='r')) & Q(name__endswith='r'))
        self.assertTrue(m)

        m = self.obj.match(Q(Q(name__startswith='p') & Q(name__endswith='r')) & Q(name__endswith='x'))
        self.assertFalse(m)

        m = self.obj.match(Q(Q(name__startswith='p') | Q(name__endswith='x')) & Q(name__endswith='r'))
        self.assertTrue(m)

