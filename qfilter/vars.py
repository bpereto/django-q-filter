"""
Regex Validation for a Django Q Query
https://docs.djangoproject.com/en/2.2/topics/db/queries/#complex-lookups-with-q-objects
"""

#
# QQUERY_ALLOWED_FIELD_CHARS:
# describes allowed chars to query for a field
#
# ex. Q(name="QQUERY_ALLOWED_FIELD_CHARS")
# Normal Chars: \w
# Spaces and Puncuation: \s - . /
# Regex for Q(name__regex="^[a-z]$"): * + $ | ( ) [ ] { } ^
QQUERY_ALLOWED_FIELD_CHARS = r'/\s\w\-\.\*\+\$\|\{\}\^\(\)\\[\]'

#
# Regex Hell
#
# QQUERY_REGEX to validate complete Q-Query
#
QQUERY_REGEX = r'^\(?~?Q\(\w+=(["][{allowed_field_chars}]*["]|True|False|\d+)\)(( ?[&|] ?\(?~?Q\(\w+=(["][{allowed_field_chars}]*["]|True|False|\d+)\)\)?)+)?$'.format(allowed_field_chars=QQUERY_ALLOWED_FIELD_CHARS)  # pylint: disable=line-too-long
