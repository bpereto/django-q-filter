import itertools
import logging

from django.core.exceptions import ValidationError
from django.db.models import Q  # pylint: disable=unused-import
from django.db.models.constants import LOOKUP_SEP

from .forms import QueryFilterForm

LOGGER = logging.getLogger(__name__)

# pylint: disable=unused-argument, invalid-name, broad-except, unused-variable


def sanitize_qquery(query):
    """
    use form to validate qfilter before eval
    QueryFilterForm uses the Regex in settings to validate the filter query
    """
    qfilter_form = QueryFilterForm(data={'qfilter': query})
    if not qfilter_form.is_valid():
        raise ValidationError(qfilter_form.errors, code='invalid')
    return qfilter_form.cleaned_data['qfilter']

def eval_qquery(query):
    """
    Evaluate QQuery String to Q-Object after sanitize
    """
    safe_dict = {'Q': Q}

    sanitized_query = sanitize_qquery(query)
    query = eval(sanitized_query, {"__builtins__": None}, safe_dict)  # pylint: disable=eval-used,line-too-long
    LOGGER.debug('Q Query: %s', query.__repr__())
    return query

def extract_field_names_from_q(query, lookups):
    """
    get field names from q query
    this extracts the lookups (iexact, startswith..) from the Q query expression
    """
    fields = []
    for lookup in lookups:
        LOGGER.debug(lookup)
        ex_lookups, field_parts, is_expression = query.solve_lookup_type(lookup[0])

        if not is_expression:
            field = LOOKUP_SEP.join(field_parts)
            fields.append(field)

        # expressions resp. annotations are handled differently in django
        else:
            lookup_splitted = lookup[0].split(LOOKUP_SEP)
            LOGGER.debug(lookup_splitted)
            for i in ex_lookups:
                if i in lookup_splitted:
                    lookup_splitted.remove(i)
            fields.append(LOOKUP_SEP.join(lookup_splitted))

    LOGGER.debug('lookup fields: %s', fields)
    return fields


def get_short_field_name(model_field):
    """
    get field name composed of model object name and model field name
    """
    return '{}.{}'.format(model_field.model._meta.object_name, model_field.name)

def merge(shared_key, merge_fields, *iterables):
    """
    merge dictionaries based on a given shared_key.
    used for normalization of the joined values in a queryset based on key
    the given merge_fields are converted in lists.

    :param shared_key:  ex. id
    :param merge_fields: ex. Platform.name
    :param iterables:   queryset values
    :return: dictionary
    """
    result = {}
    for dictionary in itertools.chain.from_iterable(iterables):
        d_key = dictionary[shared_key]
        if d_key not in result.keys():
            result[d_key] = {}
        dictionary.pop(shared_key, None)
        for key, value in dictionary.items():
            if key in merge_fields:
                if key not in result[d_key].keys():
                    result[d_key][key] = []
                if value:
                    result[d_key][key].extend([value])
                    result[d_key][key] = list(set(result[d_key][key]))
            else:
                result[d_key][key] = value
    LOGGER.debug(result)
    return result
