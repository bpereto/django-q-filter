"""
Mixins for matching
"""

__all__ = (
    'QQueryMatchMixin',
)

# pylint: disable=attribute-defined-outside-init,line-too-long,protected-access
import functools
import logging

from django.contrib import messages
from django.core.exceptions import FieldError
from django.db.models import Q  # pylint: disable=unused-import
from django.db.models import F

from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql import Query

LOGGER = logging.getLogger(__name__)


class QQueryMatchConditionals:

    def _check_condition(self, lookup, condition, value, negated=False):
        LOGGER.debug('lookup: %s', lookup)
        LOGGER.debug('condition: %s', condition)
        LOGGER.debug('value: %s', value)

        if len(lookup) == 0:
            lookup = 'exact'
        else:
            # FIXME: lookup is a list?
            lookup = lookup[0]
        try:
            func = getattr(self, f'check_{lookup}')
            if negated:
                return not func(condition, value)
            return func(condition, value)
        except:
            raise Exception(f'check condition {lookup} not implemented.')

    @staticmethod
    def check_exact(condition, value):
        return value == condition

    @staticmethod
    def check_startswith(condition, value):
        return value.startswith(condition)

    @staticmethod
    def check_endswith(condition, value):
        return value.endswith(condition)

    @staticmethod
    def check_lt(condition, value):
        return value < condition

    @staticmethod
    def check_lte(condition, value):
        return value <= condition

    @staticmethod
    def check_gt(condition, value):
        return condition < value

    @staticmethod
    def check_gte(condition, value):
        return condition <= value

    @staticmethod
    def check_isnull(condition, value):
        LOGGER.debug(value)
        LOGGER.debug(condition)
        if value is None and condition is True:
            return True
        elif value is not None and condition is False:
            return True
        return False

class QQueryMatchMixin(QQueryMatchConditionals):
    """
    Mixin to enhance django model object to match against a
    django Q query pythonic and not via SQL.

    built for situations where no database is available or the object
    is not part of a QuerySet
    """

    def _sanity_check(self, qquery):
        if not isinstance(qquery, Q):
            raise Exception('given query is not a Q Query')
        return True

    def recursive_getattr(self, obj, attr, *args):
        def _getattr(obj, attr):
            return getattr(obj, attr, *args)
        return functools.reduce(_getattr, [obj] + attr.split('.'))

    def resolve_value(self, field_parts):
        LOGGER.debug(field_parts)

        path = '.'.join(field_parts)
        LOGGER.debug('path: %s', path)

        value = self.recursive_getattr(self, path)
        LOGGER.debug('value: %s', value)

        return value

    def solve_qquery(self, qquery, depth=0):

        LOGGER.debug(f'{qquery}: depth={depth}')

        matrix = []
        for i, child in enumerate(qquery.children, start=0):
            LOGGER.debug('qquery child: %s', child)
            if isinstance(child, Q):
                LOGGER.debug('child is Q!')
                r = self.solve_qquery(child, depth=depth+1)
            else:
                LOGGER.debug('child is tuple!')
                lookup, condition = child
                solved_lookups, field_parts, is_expression = self.match_query.solve_lookup_type(lookup)
                LOGGER.debug('solved_lookups: %s', solved_lookups)
                LOGGER.debug('field_parts: %s', field_parts)
                LOGGER.debug('is_expression: %s', is_expression)

                value = self.resolve_value(field_parts)
                r = self._check_condition(lookup=solved_lookups, condition=condition, value=value)

            if qquery.negated:
                r = not r

            LOGGER.debug('result: %s', r)
            matrix.append(r)

        LOGGER.debug(f'{qquery}: matrix: {matrix}')
        connector_test_str = f' {qquery.connector.lower()} '.join([str(r) for r in matrix])
        LOGGER.debug('connector_test_str: %s', connector_test_str)
        return eval(connector_test_str)

    def match(self, q):
        self._sanity_check(q)

        self.match_query = Query(model=self._meta.model)
        LOGGER.debug(self.match_query)

        LOGGER.debug('Start match: %s', q)
        match = self.solve_qquery(q)
        LOGGER.debug('Match: %s', match)
        return match

