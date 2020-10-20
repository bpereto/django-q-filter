"""
Mixins for Inventory
"""

__all__ = (
    'QQueryViewMixin',
)

# pylint: disable=attribute-defined-outside-init

import logging

from django.contrib import messages
from django.db.models import Q  # pylint: disable=unused-import
from django.db.models import F

from .forms import (QueryFilterForm, QueryFilterWizardFormSet, QueryFilterWizardFormSetHelper)
from . import utils
from .utils import eval_qquery

LOGGER = logging.getLogger(__name__)


class QQueryViewMixin:
    """
    Mixin to enhance View with Q Query functionality

    - get lookup expressions from Q Query Statement
    - get field names from QuerySet and Q Query Statement
    - annotate Fields of Q Filter Statement to QuerySet as result
    """

    qfilter = None
    qfilter_options = {'merged': False}

    def _get_lookups_from_q(self, qquery):
        """
        recursive function to walk through Q Nodes and extract
        the lookup expression
        """
        for child in qquery.children:
            if isinstance(child, Q):
                for lookup in self._get_lookups_from_q(child):
                    yield lookup
            else:
                yield child

    def get_lookups_from_q(self, qquery):
        """
        walk through the Q Query nodes and extract the lookup expressions
        """
        return [lookup for lookup in self._get_lookups_from_q(qquery)]  # pylint: disable=unnecessary-comprehension

    def annotate_qfilter_value(self, qs, qquery, stringify=False):
        """
        annotate qfilter values to queryset

        q_field format:
        queryset.Q(<q_field>)

        string format:
        queryset.Q(<field_name>)

        :param qs:      Django Query Set
        :param qquery:   Django Q Query
        :param stringify: Use field name instead of q-filter notation
        """

        # pylint: disable=invalid-name

        lookups = self.get_lookups_from_q(qquery)
        q_fields = utils.extract_field_names_from_q(qs.query, lookups)
        filter_fields = self.get_filter_fields()

        qfilter_fields = []
        for field in q_fields:

            if stringify:
                # get __str__ representation of field
                # iteration needed to get django model field from q-filter notation
                # ex. group__name -> inventory.Group.name
                for ff in filter_fields:
                    if ff[0] == field:
                        annotate_field_name = utils.get_short_field_name(ff[2])
                        break
            else:
                annotate_field_name = 'Q({})'.format(field)

            annotate_field_value = {annotate_field_name: F(field)}
            qfilter_fields.append(annotate_field_name)
            LOGGER.debug(annotate_field_name)
            LOGGER.debug(annotate_field_value)
            qs = qs.annotate(**annotate_field_value)

        qs.qfilter_fields = list(set(qfilter_fields))
        return qs

    def get_filter_fields(self):
        """
        collect possible filter fields from given model
        also the related fields with depth 2 and for ansiblefacts depth 3
        - exclude field type "AutoField": auto generated ID field
        """
        filter_fields = []

        for field in self.model._meta.get_fields():  # pylint: disable=too-many-nested-blocks
            if field.is_relation:
                for field2 in field.related_model._meta.get_fields():  # traverse 1. relation
                    if not field2.is_relation and field2.get_internal_type() != 'AutoField':
                        filter_fields.append(('{}__{}'.format(field.name, field2.name), field2.get_internal_type(), field2),)  # pylint: disable=line-too-long
                    # traverse 2. relation
                    elif field2.is_relation and field2.related_model is not None and field2.related_model._meta.model_name.startswith('ansiblefacts'):  # pylint: disable=line-too-long
                        for field3 in field2.related_model._meta.get_fields():
                            if not field3.is_relation and field3.get_internal_type() != 'AutoField':
                                filter_fields.append(('{}__{}__{}'.format(field.name, field2.name, field3.name), field3.get_internal_type(), field3),)  # pylint: disable=line-too-long
            else:
                if field.get_internal_type() != 'AutoField':
                    filter_fields.append(('{}'.format(field.name), field.get_internal_type(), field),)

        return filter_fields


    def get_queryset(self, *args, **kwargs):
        """
        override get_queryset from parent class to enhance q query filtering

        to avoid inner joins and slow SQL, the QQuery QuerySet is stored in self.qfilter_qs
        and evaluated separate.
        """
        # pylint: disable=invalid-name
        qs = super().get_queryset(*args, **kwargs)

        #
        # apply Q Filter
        #
        try:
            if self.qfilter:
                Q_query = eval_qquery(self.qfilter)

                # check if there is a basic / non-customized select
                if getattr(qs.model.objects, 'minimal', None):
                    qquery_mgr = qs.model.objects.minimal()
                else:
                    qquery_mgr = qs.model.objects

                qquery_qs = qquery_mgr.filter(Q_query).distinct()

                # annotate q query filter fields and values
                self.qfilter_qs = self.annotate_qfilter_value(qquery_qs, Q_query, stringify=True)

                # merge-ing can be time consuming
                if self.qfilter_options['merged']:
                    LOGGER.debug('merge queryset')
                    self.qfilter_qs.merged = utils.merge('id', self.qfilter_qs.qfilter_fields, self.qfilter_qs.values())

        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception(exc)
            messages.error(self.request, 'Failed to apply Q Filter: {} Filter: {}'.format(exc, self.qfilter))
        return qs

    def get_qfilter_wizard(self, context):
        """
        get and initialize qfilter wizard formset for filtering
        """

        # check for already provided filter
        if self.request.POST.get('qfilter-wizard'):
            LOGGER.debug('use initial parameters: %s', self.request.POST)
            formset = QueryFilterWizardFormSet(self.request.POST)
        else:
            formset = QueryFilterWizardFormSet()

        # init qfilter wizard
        context['qquery_filter_formset'] = formset

        field_choices = [(v[0], utils.get_short_field_name(v[2]),) for v in self.get_filter_fields()]
        for form in context['qquery_filter_formset'].forms:
            form.fields['field'].choices = field_choices
            form.fields['combinator'].initial = 'AND'
        context['qquery_filter_formset_helper'] = QueryFilterWizardFormSetHelper()
        context['qquery_filter_formset_empty_form'] = context['qquery_filter_formset'].empty_form
        context['qquery_filter_formset_empty_form'].fields['field'].choices = field_choices

        return context

    def get_context_data(self, **kwargs):  # pylint: disable=arguments-differ
        """
        enrich context with qquery informations
        """
        context = super().get_context_data(**kwargs)    # pylint: disable=bad-super-call
        context['qfilter'] = self.qfilter
        context['qfilter_options'] = self.qfilter_options

        # init query filter
        context['qquery_filter_form'] = QueryFilterForm(initial={'qfilter': self.qfilter})
        context['qquery_filter_fields'] = self.get_filter_fields()

        # init query filter wizard
        self.get_qfilter_wizard(context)

        # override queryset with filter queryset
        if hasattr(self, 'qfilter_qs'):
            context[self.context_object_name] = self.qfilter_qs
            context['qfilter_qs'] = self.qfilter_qs

        return context

    def _compile_query_from_wizard(self):
        total_forms = int(self.request.POST.get('form-TOTAL_FORMS'))
        form_counter = 0
        qfilter = ''
        while form_counter < total_forms:
            field = self.request.POST.get('form-{}-field'.format(form_counter))
            operator = self.request.POST.get('form-{}-operator'.format(form_counter))
            value = self.request.POST.get('form-{}-value'.format(form_counter))
            inverse = self.request.POST.get('form-{}-inverse'.format(form_counter), '')
            combinator = self.request.POST.get('form-{}-combinator'.format(form_counter), '')

            # enable or disable inverse (not checkbox)
            if inverse == 'on':
                inverse = '~'

            # handle operators which requires non string input
            # FIXME: this is ugly.
            if operator == '__isnull=':
                value = 'False'
            elif operator in ('__gte=', '__lte='):
                value = '{}'.format(value)
            else:
                value = '"{}"'.format(value)

            query = '{}Q({}{}{})'.format(inverse, field, operator, value)

            # add combinator if there are more forms to combinate with
            if form_counter < total_forms - 1:
                query = query + ' ' + combinator + ' '

            qfilter += query
            form_counter += 1
        return qfilter

    def get(self, request, *args, **kwargs):
        """
        get qfilter from get parameters
        """
        if self.request.method == 'GET':
            self.qfilter = self.request.GET.get('qfilter', None)
            if self.request.GET.get('qfilter-merged', False):
                self.qfilter_options['merged'] = True

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        get qfilter wizard parameters from post
        """
        print(self.request.POST)
        if self.request.POST.get('qfilter-wizard'):
            self.qfilter = self._compile_query_from_wizard()
            if self.request.POST.get('qfilter-merged', False):
                self.qfilter_options['merged'] = True
        return super().get(request, *args, **kwargs)
