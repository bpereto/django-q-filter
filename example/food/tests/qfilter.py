"""
unit tests for django q filter
"""

# pylint: disable=invalid-name,line-too-long,anomalous-backslash-in-string

__all__ = (
    'QFilterTestCase',
)

from unittest import TestCase

from qfilter.forms import QueryFilterForm


class QFilterTestCase(TestCase):
    """
    Test cases for the QFilter
    """

    def test_correct_qfilter(self):
        """
        Test correct qfilters
        """

        QFILTER = [

            # normal CharField, with different spaces
            'Q(name="curry")',
            'Q(name="thai curry")',
            'Q(name="thai curry ")',
            'Q(name=" thai curry ")',
            'Q(name="9999")',
            'Q(name="äöüÄÖÜéàè")',
            'Q(name="000-123-456-789")',
            'Q(name="_hello_")',
            #'Q(name="+*ç%&/()=?`")',

            # normal BooleanField
            'Q(active=True)',
            'Q(active=False)',

            # normal IntegerField
            'Q(hours=6)',

            # normal DateTimeField
            'Q(date="2020-10-06")',
            'Q(date="2020-10-06 16:00:01")',

            # regex field
            'Q(name__regex="(curry|wine)")',
            'Q(name__regex="^[a-z0-9]$")',

            # normal CharField with AND and CharField, with different spacing
            'Q(name="curry") & Q(name="wine")',
            'Q(name="curry")&Q(name="wine")',
            'Q(name="cur ry")& Q(name="wine")',
            'Q(name="curry") &Q(name="wine")',

            # normal CharField with OR and CharField, with different spacing
            'Q(name="curry")|Q(name="poulet")',
            'Q(name="curry") | Q(name="poulet")',
            'Q(name="curry")| Q(name="poulet")',
            'Q(name="curry") |Q(name="poulet")',

            # multiple char fields and OR, AND
            'Q(name="curry") | Q(name="wine") | Q(name="ham")',
            'Q(name="curry")|Q(name="wine")|Q(name="ham")',
            'Q(name="curry") |Q(name="wine")| Q(name="ham")',
            'Q(name="curry") & Q(name="wine") | Q(name="ham")',
            'Q(name="curry")&Q(name="wine")|Q(name="ham")',
            'Q(name="curry") | Q(name="wine") & Q(name="ham")',

            # mixed fields
            'Q(name="curry") & Q(active=True) & Q(created="2020-20-10")',
            
            # grouped queries
            '(Q(name="curry") & Q(active=True)) | Q(name="broccoli")',
            'Q(name="curry") & (Q(active=True) | Q(name="broccoli"))',
            '(Q(name="curry") & Q(active=True)) | (Q(name="celery") & Q(active=False))',

            # operators
            'Q(question__startswith="Who") | Q(question__startswith="What")',
            'Q(question__startswith="Who") | ~Q(pub_date__year=2005)',
            '~Q(question__startswith="Who") | ~Q(pub_date__year=2005)',
            '~Q(question__startswith="Who")&~Q(pub_date__year=2005)',
            'Q(date__gte="2020-10-06")',

            # manytomany
            'Q(ansiblefacts__ansiblefactsos__kernel__isnull=False) & Q(ansiblefacts__ansiblefactsos__uptime__isnull=False)',
            'Q(ansiblefacts__ansiblefactsmount__name="/home")',
            'Q(ansiblefacts__ansiblefactsipaddress__dns__contains=".")'
        ]

        for qfilter in QFILTER:
            try:
                qfilter_form = QueryFilterForm(data={'qfilter': qfilter})
                self.assertTrue(qfilter_form.is_valid())
            except AssertionError:
                print('FAILED:', qfilter)
                raise

    def test_invalid_qfilter(self):
        """
        Test invalid qfilters
        """
        QFILTER = [

            # evil stuff
            'os.system("ls")',
            "__import__('os').system('clear')",
            'import json',
            'Q(name=""import os"")'
            'Q(name="; DROP")',
            'Q(name="\'; drop")',
            'Q(name={asdf$})',
            'Q(name=${HOSTNAME})',

            # quoting
            'Q(question__startswith=\'Who\') \'asdf + asdf\'| Q(question__startswith=\'What\')',
            'Q(question__startswith=\'"\'Who\'"\') | Q(question__startswith=\'What\')',
            'Q(question__startswith=\'Who\') | Q(question__startswith=\'What\')',
            'Q(question__startswith=\'Who\') | ~Q(pub_date__year=2005)',
            '~Q(question__startswith=\'Who\') | ~Q(pub_date__year=2005)',

            # weird
            'Q(active=false)',
            'Q(name="curry") | Q(active=true)',
            'Q(name="curry") | ',
            'Q(name="curry") | Q()',
            '()Q(name="curry")()',
            'Q(name="(curry)")&Q()',
            'Q()&Q()',
            '((Q(name="asdf")))',
            'Q(name=$$$$$$$$$$$$$$$$$$$$$$$)',
        ]

        for qfilter in QFILTER:
            try:
                qfilter_form = QueryFilterForm(data={'qfilter': qfilter})
                self.assertFalse(qfilter_form.is_valid())
            except AssertionError:
                print('FAILED:', qfilter)
                raise
