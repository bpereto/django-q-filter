"""
Q Query Forms
"""

__all__ = (
    'QueryFilterForm',
    'QueryFilterWizardFormSet',
    'QueryWizardForm',
    'QueryFilterWizardFormSetHelper'
)

from qfilter import vars
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row
from django import forms
from django.core.validators import RegexValidator


class QueryFilterForm(forms.Form):
    """
    form to build a Q-query
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_tag = False

    qfilter = forms.CharField(required=False,
                              empty_value=None,
                              label="Django Q Query",
                              validators=[RegexValidator(vars.QQUERY_REGEX)],  # pylint: disable=line-too-long
                              widget=forms.TextInput(attrs={'pattern': vars.QQUERY_REGEX, 'class':'w-100'})
                              )


class QueryWizardForm(forms.Form):
    """
    Wizardry query form for django q queries
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = QueryFilterWizardFormSetHelper()

    OPERATOR_CHOICES = [
        ('=', 'equal'),
        ('__icontains=', 'contains'),
        ('__isnull=', 'exists'),
        ('__gte=', 'gte'),
        ('__lte=', 'lte'),
        ('__regex=', 'regex')
    ]

    COMBINATOR_CHOICES = [
        ('&', 'AND'),
        ('|', 'OR')
    ]

    field = forms.ChoiceField()
    operator = forms.ChoiceField(choices=OPERATOR_CHOICES)
    value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control-sm'}), required=False)
    inverse = forms.BooleanField(required=False, label='not')
    combinator = forms.ChoiceField(choices=COMBINATOR_CHOICES, label='')


class QueryFilterWizardFormSetHelper(FormHelper):
    """
    django crispy helper for the q filter wizard
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = Layout(
            Div(
                Row(
                    Column('field', css_class='form-group col-md-5 mb-0'),
                    Column('operator', css_class='form-group col-md-2 mb-0'),
                    Column('value', css_class='form-group col-md-3 mb-2'),
                    Column('inverse',
                           css_class='form-group col-md-1 mt-1 align-self-center'
                           ),
                    Column(Div(css_class='delete-row d-flex h-100 float-right'),
                           css_class='form-group col-md-1 pr-0'
                           ),
                    css_class='form-row border rounded mt-2'
                ),
                Row(
                    'combinator', css_class='form-row mt-2'
                ),
                css_class='form-container'
            )
        )
        self.form_method = 'POST'
        self.form_tag = False


QueryFilterWizardFormSet = forms.formset_factory(
    QueryWizardForm, extra=1
)
