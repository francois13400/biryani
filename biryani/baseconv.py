# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/Biryani/
#
# This file is part of Biryani.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Base Conversion Functions

.. note:: Most converters do only one operation and can fail when given wrong data. To ensure that they don't fail, they
   must be combined with other converters.

.. note:: Most converters work on unicode strings. To use them you must first convert your strings to unicode. By using
   converter :func:`string_to_unicode`, for example.
"""


import re

from . import states


__all__ = [
    'boolean_to_unicode',
    'clean_unicode_to_boolean',
    'clean_unicode_to_email',
    'clean_unicode_to_json',
    'clean_unicode_to_url',
    'clean_unicode_to_url_path_and_query',
    'cleanup_empty',
    'cleanup_line',
    'cleanup_text',
    'condition',
    'default',
    'dict_to_instance',
    'extract_when_singleton',
    'fail',
    'first_match',
    'form_data_to_boolean',
    'function',
    'item_or_sequence',
    'noop',
    'pipe',
    'python_data_to_boolean',
    'python_data_to_float',
    'python_data_to_integer',
    'python_data_to_unicode',
    'rename_item',
    'require',
    'set_value',
    'string_to_unicode',
    'structured_mapping',
    'structured_sequence',
    'test',
    'test_between',
    'test_equals',
    'test_greater_or_equal',
    'test_in',
    'test_is',
    'test_isinstance',
    'test_less_or_equal',
    'to_value',
    'translate',
    'unicode_to_boolean',
    'unicode_to_email',
    'unicode_to_float',
    'unicode_to_integer',
    'unicode_to_json',
    'unicode_to_url',
#    'uniform_mapping',
    'uniform_sequence',
    ]

domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][-A-Za-z0-9_:.]+$')
html_name_re = html_id_re
N_ = lambda s: s
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Level-1 Converters


def boolean_to_unicode(value, state = states.default_state):
    """Convert a boolean to unicode.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> boolean_to_unicode(False)
    (u'0', None)
    >>> boolean_to_unicode(True)
    (u'1', None)
    >>> boolean_to_unicode(0)
    (u'0', None)
    >>> boolean_to_unicode('')
    (u'0', None)
    >>> boolean_to_unicode('any non-empty string')
    (u'1', None)
    >>> boolean_to_unicode('0')
    (u'1', None)
    >>> boolean_to_unicode(None)
    (None, None)
    >>> pipe(default(False), boolean_to_unicode)(None)
    (u'0', None)
    """
    if value is None:
        return None, None
    return unicode(int(bool(value))), None


def clean_unicode_to_boolean(value, state = states.default_state):
    """Convert a clean unicode string to a boolean.

    .. note:: For a converter that doesn't require a clean unicode string, see :func:`unicode_to_boolean`.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> clean_unicode_to_boolean(u'0')
    (False, None)
    >>> clean_unicode_to_boolean(u'1')
    (True, None)
    >>> clean_unicode_to_boolean(None)
    (None, None)
    >>> clean_unicode_to_boolean(u'true')
    (None, 'Value must be a boolean number')
    """
    if value is None:
        return None, None
    try:
        return bool(int(value)), None
    except ValueError:
        return None, state._('Value must be a boolean number')


def clean_unicode_to_email(value, state = states.default_state):
    """Convert a clean unicode string to an email address.

    .. note:: For a converter that doesn't require a clean unicode string, see :func:`unicode_to_email`.

    >>> clean_unicode_to_email(u'spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> clean_unicode_to_email(u'mailto:spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> clean_unicode_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> clean_unicode_to_email(u'root@127.0.0.1')
    (None, 'Invalid domain name')
    >>> clean_unicode_to_email(u'root')
    (None, 'An email must contain exactly one "@"')
    """
    if value is None:
        return None, None
    value = value.lower()
    if value.startswith(u'mailto:'):
        value = value.replace(u'mailto:', u'')
    try:
        username, domain = value.split('@', 1)
    except ValueError:
        return None, state._('An email must contain exactly one "@"')
    if not username_re.match(username):
        return None, state._('Invalid username')
    if not domain_re.match(domain) and domain != 'localhost':
        return None, state._('Invalid domain name')
    return value, None


def clean_unicode_to_json(value, state = states.default_state):
    """Convert a clean unicode string to a JSON value.

    .. note:: For a converter that doesn't require a clean unicode string, see :func:`unicode_to_json`.

    .. note:: This converter uses module ``simplejson``  when it is available, or module ``json`` otherwise.

    >>> clean_unicode_to_json(u'{"a": 1, "b": 2}')
    ({u'a': 1, u'b': 2}, None)
    >>> clean_unicode_to_json(u'null')
    (None, None)
    >>> clean_unicode_to_json(None)
    (None, None)
    """
    if value is None:
        return None, None
    try:
        import simplejson as json
    except ImportError:
        import json
    if isinstance(value, str):
        # Ensure that json.loads() uses unicode strings.
        value = value.decode('utf-8')
    try:
        return json.loads(value), None
    except json.JSONDecodeError, e:
        return None, unicode(e)


def clean_unicode_to_url(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a converter that converts a clean unicode string to an URL.

    .. note:: For a converter that doesn't require a clean unicode string, see :func:`unicode_to_url`.

    >>> clean_unicode_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> clean_unicode_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> clean_unicode_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> clean_unicode_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (None, 'URL must be complete')
    >>> clean_unicode_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    """
    def clean_unicode_to_url_converter(value, state = states.default_state):
        if value is None:
            return None, None
        import urlparse
        split_url = list(urlparse.urlsplit(value))
        if full and add_prefix and not split_url[0] and not split_url[1] and split_url[2] \
                and not split_url[2].startswith('/'):
            split_url = list(urlparse.urlsplit(add_prefix + value))
        scheme = split_url[0]
        if scheme != scheme.lower():
            split_url[0] = scheme = scheme.lower()
        if full and not scheme:
            return None, state._('URL must be complete')
        if scheme and schemes is not None and scheme not in schemes:
            return None, state._('Scheme must belong to {0}').format(sorted(schemes))
        network_location = split_url[1]
        if network_location != network_location.lower():
            split_url[1] = network_location = network_location.lower()
        if scheme in ('http', 'https') and not split_url[2]:
            # By convention a full HTTP URL must always have at least a "/" in its path.
            split_url[2] = '/'
        if remove_fragment and split_url[4]:
            split_url[4] = ''
        return unicode(urlparse.urlunsplit(split_url)), None
    return clean_unicode_to_url_converter


def clean_unicode_to_url_path_and_query(value, state = states.default_state):
    """Convert a clean unicode string to the path and query of an URL.

    >>> clean_unicode_to_url_path_and_query(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html', None)
    >>> clean_unicode_to_url_path_and_query(u'/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    >>> clean_unicode_to_url_path_and_query(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (None, 'URL must not be complete')
    >>> import urlparse
    >>> pipe(
    ...     clean_unicode_to_url(),
    ...     function(lambda value: urlparse.urlunsplit(['', ''] + list(urlparse.urlsplit(value))[2:])),
    ...     clean_unicode_to_url_path_and_query,
    ...     )(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    """
    if value is None:
        return None, None
    import urlparse
    split_url = list(urlparse.urlsplit(value))
    if split_url[0] or split_url[1]:
        return None, state._('URL must not be complete')
    if split_url[4]:
        split_url[4] = ''
    return unicode(urlparse.urlunsplit(split_url)), None


def cleanup_empty(value, state = states.default_state):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is.

    >>> cleanup_empty(0)
    (None, None)
    >>> cleanup_empty('')
    (None, None)
    >>> cleanup_empty([])
    (None, None)
    >>> cleanup_empty({})
    (None, None)
    >>> cleanup_empty(u'hello world')
    (u'hello world', None)
    >>> cleanup_empty(u'   hello world   ')
    (u'   hello world   ', None)
    """
    return value if value else None, None


def condition(test_converter, ok_converter, error_converter = None):
    """When *test_converter* succeeds (ie no error), then apply *ok_converter*, otherwise apply *error_converter*.

    .. note:: See also :func:`first_match`.

    >>> detect_unknown_values = condition(
    ...     test_in(['?', 'x']),
    ...     set_value(False),
    ...     set_value(True),
    ...     )
    >>> detect_unknown_values(u'Hello world!')
    (True, None)
    >>> detect_unknown_values(u'?')
    (False, None)
    """
    def condition_converter(value, state = states.default_state):
        test, error = test_converter(value, state = state)
        if error is None:
            return ok_converter(value, state = state)
        elif error_converter is None:
            return value, None
        else:
            return error_converter(value, state = state)
    return condition_converter


def default(constant):
    """Return a converter that replace a missing value (aka ``None``) by given one.

    >>> default(42)(None)
    (42, None)
    >>> default(42)(u'1234')
    (u'1234', None)
    >>> pipe(unicode_to_integer, default(42))(u'1234')
    (1234, None)
    >>> pipe(unicode_to_integer, default(42))(u'    ')
    (42, None)
    >>> pipe(unicode_to_integer, default(42))(None)
    (42, None)
    """
    return lambda value, state = states.default_state: (constant, None) if value is None else (value, None)


def dict_to_instance(cls):
    """Return a converter that creates in instance of a class from a dictionary.

    >>> class C(object):
    ...     pass
    >>> dict_to_instance(C)(dict(a = 1, b = 2))
    (<C object at 0x...>, None)
    >>> c = to_value(dict_to_instance(C))(dict(a = 1, b = 2))
    >>> c.a, c.b
    (1, 2)
    >>> dict_to_instance(C)(None)
    (None, None)
    """
    def dict_to_instance_converter(value, state = states.default_state):
        if value is None:
            return None, None
        instance = cls()
        instance.__dict__ = value
        return instance, None
    return dict_to_instance_converter


def fail(msg = N_('An error occured')):
    """Return a converter that always returns an error.

    >>> fail('Wrong answer')(42)
    (None, 'Wrong answer')
    >>> fail()(42)
    (None, 'An error occured')
    """
    def fail_converter(value, state = states.default_state):
        return None, state._(msg)
    return fail_converter


def first_match(*converters):
    """Try each converter successively until one succeeds. When every converter fail, return the result of the last one.

    >>> first_match(test_equals(u'NaN'), unicode_to_integer)(u'NaN')
    (u'NaN', None)
    >>> first_match(test_equals(u'NaN'), unicode_to_integer)(u'42')
    (42, None)
    >>> first_match(test_equals(u'NaN'), unicode_to_integer)(u'abc')
    (None, 'Value must be an integer')
    >>> first_match(test_equals(u'NaN'), unicode_to_integer, set_value(0))(u'Hello world!')
    (0, None)
    >>> first_match()(u'Hello world!')
    (u'Hello world!', None)
    """
    def first_match_converter(value, state = states.default_state):
        convertered_value = value
        error = None
        for converter in converters:
            convertered_value, error = converter(value, state = state)
            if error is None:
                return convertered_value, error
        return convertered_value, error
    return first_match_converter


def function(function, handle_none = False):
    """Return a converter that applies a function to value and returns a new value.

    .. note:: Like most converters, by default a missing value (aka ``None``) is not converted (ie function is not
       called). Set ``handle_none`` to ``True`` to call function when value is ``None``.

    .. note:: When your function doesn't modify value but may generate an error, use a :func:`test` instead.

    .. note:: When your function modifies value and may generate an error, write a full converter instead of a function.

    >>> function(int)('42')
    (42, None)
    >>> function(sorted)([3, 2, 1])
    ([1, 2, 3], None)
    >>> function(lambda value: value + 1)(42)
    (43, None)
    >>> function(lambda value: value + 1)(None)
    (None, None)
    >>> function(lambda value: value + 1)(u'hello world')
    Traceback (most recent call last):
    TypeError: coercing to Unicode: need string or buffer, int found
    >>> function(lambda value: value + 1, handle_none = True)(None)
    Traceback (most recent call last):
    TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
    """
    def function_converter(value, state = states.default_state):
        if value is None and not handle_none or function is None:
            return value, None
        return function(value), None
    return function_converter


def item_or_sequence(converter, constructor = list, keep_null_items = False):
    """Return a converter that accepts either an item or a sequence of items and applies a converter to them.

    >>> item_or_sequence(unicode_to_integer)(u'42')
    (42, None)
    >>> item_or_sequence(unicode_to_integer)([u'42'])
    (42, None)
    >>> item_or_sequence(unicode_to_integer)([u'42', u'43'])
    ([42, 43], None)
    >>> item_or_sequence(unicode_to_integer)([u'42', u'43', u'Hello world!'])
    ([42, 43], {2: 'Value must be an integer'})
    >>> item_or_sequence(unicode_to_integer)([u'42', None, u'43'])
    ([42, 43], None)
    >>> item_or_sequence(unicode_to_integer)([None, None])
    (None, None)
    >>> item_or_sequence(unicode_to_integer, keep_null_items = True)([None, None])
    ([None, None], None)
    >>> item_or_sequence(unicode_to_integer, keep_null_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> item_or_sequence(unicode_to_integer, keep_null_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, None], {2: 'Value must be an integer'})
    >>> item_or_sequence(unicode_to_integer, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    return condition(
        test_isinstance(constructor),
        pipe(
            uniform_sequence(converter, constructor = constructor, keep_null_items = keep_null_items),
            extract_when_singleton,
            ),
        converter,
        )


def noop(value, state = states.default_state):
    """Return value as is.

    >>> noop(42)
    (42, None)
    >>> noop(None)
    (None, None)
    """
    return value, None


def pipe(*converters):
    """Return a compound converter that applies each of its converters till the end or an error occurs.

    >>> unicode_to_boolean(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute 'strip'
    >>> pipe(unicode_to_boolean)(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute 'strip'
    >>> pipe(test_isinstance(unicode), unicode_to_boolean)(42)
    (None, "Value is not an instance of <type 'unicode'>")
    >>> pipe(python_data_to_unicode, test_isinstance(unicode), unicode_to_boolean)(42)
    (True, None)
    >>> pipe()(42)
    (42, None)
    """
    def pipe_converter(*args, **kwargs):
        if not converters:
            return noop(*args, **kwargs)
        for converter in converters:
            if converter is None:
                continue
            value, error = converter(*args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
        return value, None
    return pipe_converter


def python_data_to_float(value, state = states.default_state):
    """Convert any python data to a float.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_float(42)
    (42.0, None)
    >>> python_data_to_float('42')
    (42.0, None)
    >>> python_data_to_float(u'42')
    (42.0, None)
    >>> python_data_to_float(42.75)
    (42.75, None)
    >>> python_data_to_float(None)
    (None, None)
    """
    if value is None:
        return None, None
    try:
        return float(value), None
    except ValueError:
        return None, state._('Value must be a float')


def python_data_to_integer(value, state = states.default_state):
    """Convert any python data to an integer.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_integer(42)
    (42, None)
    >>> python_data_to_integer('42')
    (42, None)
    >>> python_data_to_integer(u'42')
    (42, None)
    >>> python_data_to_integer(42.75)
    (42, None)
    >>> python_data_to_integer(None)
    (None, None)
    """
    if value is None:
        return None, None
    try:
        return int(value), None
    except ValueError:
        return None, state._('Value must be an integer')


def python_data_to_unicode(value, state = states.default_state):
    """Convert any Python data to unicode.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_unicode(42)
    (u'42', None)
    >>> python_data_to_unicode('42')
    (u'42', None)
    >>> python_data_to_unicode(None)
    (None, None)
    """
    if value is None:
        return None, None
    if isinstance(value, str):
        return value.decode('utf-8'), None
    try:
        return unicode(value), None
    except UnicodeDecodeError:
        return str(value).decode('utf-8'), None


def rename_item(old_key, new_key):
    """Return a converter that renames a key in a mapping.

    >>> rename_item('a', 'c')(dict(a = 1, b = 2))
    ({'c': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(None)
    (None, None)
    """
    def rename_item_converter(value, state = states.default_state):
        if value is None:
            return None, None
        if old_key in value:
            value[new_key] = value.pop(old_key)
        return value, None
    return rename_item_converter


def require(value, state = states.default_state):
    """Returns an error when value is missing (aka ``None``).

    >>> require(42)
    (42, None)
    >>> require(u'')
    (u'', None)
    >>> require(None)
    (None, 'Missing value')
    """
    if value is None:
        return None, state._('Missing value')
    else:
        return value, None


def set_value(constant):
    """Return a converter that replaces any non-null value by given one.

    .. note:: This is the opposite behaviour of func:`default`.

    >>> set_value(42)(u'Answer to the Ultimate Question of Life, the Universe, and Everything')
    (42, None)
    >>> set_value(42)(None)
    (None, None)
    """
    return lambda value, state = states.default_state: (constant, None) if value is not None else (None, None)


def string_to_unicode(encoding = 'utf-8'):
    """Return a string to unicode converter that uses given *encoding*.

    >>> string_to_unicode()('   Hello world!   ')
    (u'   Hello world!   ', None)
    >>> string_to_unicode()(42)
    (42, None)
    >>> string_to_unicode()(None)
    (None, None)
    """
    return function(lambda value: value.decode(encoding) if isinstance(value, str) else value)


def structured_mapping(converters, constructor = dict, default = None, keep_empty = False):
    """Return a converter that maps a mapping of converters to a mapping (ie dict, etc) of values.

    >>> strict_converter = structured_mapping(dict(
    ...     name = pipe(cleanup_line, require),
    ...     age = unicode_to_integer,
    ...     email = unicode_to_email,
    ...     ))
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = None, email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, {'phone': 'Unexpected item'})
    >>> non_strict_converter = structured_mapping(
    ...     dict(
    ...         name = pipe(cleanup_line, require),
    ...         age = unicode_to_integer,
    ...         email = unicode_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'+33 9 12 34 56 78', 'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = unicode_to_integer,
    ...         email = unicode_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )(dict(name = u'   ', email = None))
    (None, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = unicode_to_integer,
    ...         email = unicode_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_empty = True,
    ...     )(dict(name = u'   ', email = None))
    ({}, None)
    """
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )
    def structured_mapping_converter(values, state = states.default_state):
        if values is None:
            return None, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters.copy()
            for name in values:
                if name not in values_converter:
                    values_converter[name] = default if default is not None else fail(N_('Unexpected item'))
        errors = {}
        convertered_values = {}
        for name, converter in values_converter.iteritems():
            convertered_value, error = converter(values.get(name), state = state)
            if error is not None:
                errors[name] = error
            elif convertered_value is not None:
                convertered_values[name] = convertered_value
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_mapping_converter


def structured_sequence(converters, constructor = list, default = None, keep_empty = False):
    """Return a converter that map a sequence of converters to a sequence of values.

    >>> strict_converter = structured_sequence([
    ...     pipe(cleanup_line, require),
    ...     unicode_to_integer,
    ...     unicode_to_email,
    ...     ])
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', None, None], {1: 'Value must be an integer'})
    >>> strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', None], {3: 'Unexpected item'})
    >>> non_strict_converter = structured_sequence(
    ...     [
    ...         pipe(cleanup_line, require),
    ...         unicode_to_integer,
    ...         unicode_to_email,
    ...         ],
    ...     default = cleanup_line,
    ...     )
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', None, None], {1: 'Value must be an integer'})
    >>> non_strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', u'+33 9 12 34 56 78'], None)
    """
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]
    def structured_sequence_converter(values, state = states.default_state):
        if values is None:
            return None, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters[:]
            while len(values) > len(values_converter):
                values_converter.append(default if default is not None else fail(N_('Unexpected item')))
        import itertools
        errors = {}
        convertered_values = []
        for i, (converter, value) in enumerate(itertools.izip_longest(
                values_converter, itertools.islice(values, len(values_converter)))):
            convertered_value, error = converter(value, state = state)
            if error is not None:
                errors[i] = error
            convertered_values.append(convertered_value)
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_sequence_converter


def test(function, error = 'Test failed', handle_none = False):
    """Return a converter that applies a test function to a value and returns an error when test fails.

    ``test`` always returns the initial value, even when test fails.

    >>> test(lambda value: isinstance(value, basestring))('hello')
    ('hello', None)
    >>> test(lambda value: isinstance(value, basestring))(1)
    (None, 'Test failed')
    >>> test(lambda value: isinstance(value, basestring), error = 'Value is not a string')(1)
    (None, 'Value is not a string')
    """
    def test_converter(value, state = states.default_state):
        if value is None and not handle_none or function is None or function(value):
            return value, None
        return None, state._(error)
    return test_converter


def test_between(min_value, max_value):
    """Return a converter that accepts only values between the two given bounds (included).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_between(0, 9)(5)
    (5, None)
    >>> test_between(0, 9)(0)
    (0, None)
    >>> test_between(0, 9)(9)
    (9, None)
    >>> test_between(0, 9)(10)
    (None, 'Value must be between 0 and 9')
    >>> test_between(0, 9)(None)
    (None, None)
    """
    return test(lambda value: min_value <= value <= max_value,
        error = N_('Value must be between {0} and {1}').format(min_value, max_value))


def test_equals(constant):
    """Return a converter that accepts only values equals to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_equals(42)(42)
    (42, None)
    >>> test_equals(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> test_equals(41)(42)
    (None, 'Value must be equal to 41')
    >>> test_equals(None)(42)
    (42, None)
    >>> test_equals(42)(None)
    (None, None)
    """
    return test(lambda value: value == constant if constant is not None else True,
        error = N_('Value must be equal to {0}').format(constant))


def test_greater_or_equal(constant):
    """Return a converter that accepts only values greater than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_greater_or_equal(0)(5)
    (5, None)
    >>> test_greater_or_equal(9)(5)
    (None, 'Value must be greater than or equal to 9')
    >>> test_greater_or_equal(9)(None)
    (None, None)
    >>> test_greater_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value >= constant) if constant is not None else True,
        error = N_('Value must be greater than or equal to {0}').format(constant))


def test_in(values):
    """Return a converter that accepts only values belonging to a given set (or list or...).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *values* is
       ``None``, value is never compared.

    >>> test_in('abcd')('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('z')
    (None, "Value must be one of ['a', 'b', 'c', 'd']")
    >>> test_in([])('z')
    (None, 'Value must be one of []')
    >>> test_in(None)('z')
    ('z', None)
    >>> test_in(['a', 'b', 'c', 'd'])(None)
    (None, None)
    """
    return test(lambda value: value in values if values is not None else True,
        error = N_('Value must be one of {0}').format(values))


def test_is(constant):
    """Return a converter that accepts only values that are strictly equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_is(42)(42)
    (42, None)
    >>> test_is(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    (None, "Value must be {'a': 1, 'b': 2}")
    >>> test_is(41)(42)
    (None, 'Value must be 41')
    >>> test_is(None)(42)
    (42, None)
    >>> test_is(42)(None)
    (None, None)
    """
    return test(lambda value: value is constant if constant is not None else True,
        error = N_('Value must be {0}').format(constant))


def test_isinstance(class_or_classes):
    """Return a converter that accepts only an instance of given class (or tuple of classes).

    >>> test_isinstance(basestring)('This is a string')
    ('This is a string', None)
    >>> test_isinstance(basestring)(42)
    (None, "Value is not an instance of <type 'basestring'>")
    >>> test_isinstance((float, int))(42)
    (42, None)
    """
    return test(lambda value: isinstance(value, class_or_classes),
        error = N_('Value is not an instance of {0}').format(class_or_classes))


def test_less_or_equal(constant):
    """Return a converter that accepts only values less than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_less_or_equal(9)(5)
    (5, None)
    >>> test_less_or_equal(0)(5)
    (None, 'Value must be less than or equal to 0')
    >>> test_less_or_equal(9)(None)
    (None, None)
    >>> test_less_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value <= constant) if constant is not None else True,
        error = N_('Value must be less than or equal to {0}').format(constant))


def translate(conversions):
    """Return a converter that converts values found in given dictionary and keep others as is.

    .. warning:: Like most converters, a missing value (aka ``None``) is not handled => It is never translated.

    >>> translate({0: u'bad', 1: u'OK'})(0)
    (u'bad', None)
    >>> translate({0: u'bad', 1: u'OK'})(1)
    (u'OK', None)
    >>> translate({0: u'bad', 1: u'OK'})(2)
    (2, None)
    >>> translate({0: u'bad', 1: u'OK'})(u'three')
    (u'three', None)
    >>> translate({None: u'problem', 0: u'bad', 1: u'OK'})(None)
    (None, None)
    >>> pipe(translate({0: u'bad', 1: u'OK'}), default(u'no problem'))(None)
    (u'no problem', None)
    """
    return function(lambda value: value
        if value is None or conversions is None or value not in conversions
        else conversions[value])


def unicode_to_url(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a converter that converts an unicode string to an URL.

    >>> unicode_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> unicode_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> unicode_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> unicode_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (None, 'URL must be complete')
    >>> unicode_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> unicode_to_url()(u'    http://packages.python.org/Biryani/   ')
    (u'http://packages.python.org/Biryani/', None)
    """
    return pipe(
        cleanup_line,
        clean_unicode_to_url(add_prefix = add_prefix, full = full, remove_fragment = remove_fragment,
            schemes = schemes),
        )


#def uniform_mapping(key_converter, value_converter, constructor = dict, keep_empty = False, keep_null_keys = False,
#        keep_null_values = False):
#    """Return a converter that applies a unique converter to each key and another unique converter to each value of a mapping."""
#    def uniform_mapping_converter(values, state = states.default_state):
#        if values is None:
#            return None, None
#        errors = {}
#        convertered_values = {}
#        for key, value in values.iteritems():
#            convertered_key, error = key_converter(key, state = state)
#            if error is not None:
#                errors[key] = error
#                continue
#            if convertered_key is None and not keep_null_keys:
#                continue
#            convertered_value, error = value_converter(value, state = state)
#            if error is not None:
#                errors[key] = error
#            if convertered_value is None and not keep_null_values:
#                continue
#            convertered_values[convertered_key] = convertered_value
#        if keep_empty or convertered_values:
#            convertered_values = constructor(convertered_values)
#        else:
#            convertered_values = None
#        return convertered_values, errors or None
#    return uniform_mapping_converter


def uniform_sequence(converter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a converter that applies the same converter to each value of a list.

    >>> uniform_sequence(unicode_to_integer)([u'42'])
    ([42], None)
    >>> uniform_sequence(unicode_to_integer)([u'42', u'43'])
    ([42, 43], None)
    >>> uniform_sequence(unicode_to_integer)([u'42', u'43', u'Hello world!'])
    ([42, 43], {2: 'Value must be an integer'})
    >>> uniform_sequence(unicode_to_integer)([u'42', None, u'43'])
    ([42, 43], None)
    >>> uniform_sequence(unicode_to_integer)([None, None])
    (None, None)
    >>> uniform_sequence(unicode_to_integer, keep_empty = True)([None, None])
    ([], None)
    >>> uniform_sequence(unicode_to_integer, keep_empty = True, keep_null_items = True)([None, None])
    ([None, None], None)
    >>> uniform_sequence(unicode_to_integer, keep_null_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> uniform_sequence(unicode_to_integer, keep_null_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, None], {2: 'Value must be an integer'})
    >>> uniform_sequence(unicode_to_integer, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    def uniform_sequence_converter(values, state = states.default_state):
        if values is None:
            return None, None
        errors = {}
        convertered_values = []
        for i, value in enumerate(values):
            convertered_value, error = converter(value, state = state)
            if error is not None:
                errors[i] = error
            if keep_null_items or convertered_value is not None:
                convertered_values.append(convertered_value)
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return uniform_sequence_converter


# Level-2 Converters


cleanup_line = pipe(
    function(lambda value: value.strip()),
    cleanup_empty,
    )
"""Strip spaces from a string and remove it when empty.

    >>> cleanup_line(u'   Hello world!   ')
    (u'Hello world!', None)
    >>> cleanup_line('   ')
    (None, None)
    >>> cleanup_line(None)
    (None, None)
    """

cleanup_text = pipe(
    function(lambda value: value.replace('\r\n', '\n').replace('\r', '\n')),
    cleanup_line,
    )
"""Replaces CR + LF or CR to LF in a string, then strip spaces and remove it when empty.

    >>> cleanup_text(u'   Hello\\r\\n world!\\r   ')
    (u'Hello\\n world!', None)
    >>> cleanup_text('   ')
    (None, None)
    >>> cleanup_text(None)
    (None, None)
    """

extract_when_singleton = condition(
    test(lambda value: len(value) == 1 and not isinstance(value[0], (list, set, tuple))),
    function(lambda value: list(value)[0]),
    )
"""Extract first item of sequence when it is a singleton and it is not itself a sequence, otherwise keep it unchanged.

    >>> extract_when_singleton([42])
    (42, None)
    >>> extract_when_singleton([42, 43])
    ([42, 43], None)
    >>> extract_when_singleton([])
    ([], None)
    >>> extract_when_singleton(None)
    (None, None)
    >>> extract_when_singleton([[42]])
    ([[42]], None)
"""


# Level-3 Converters


form_data_to_boolean = pipe(cleanup_line, clean_unicode_to_boolean, default(False))
"""Convert an unicode string submitted by an HTML form to a boolean.

    Like :data:`unicode_to_boolean`, but when value is missing, ``False`` is returned instead of ``None``.

    >>> form_data_to_boolean(u'0')
    (False, None)
    >>> form_data_to_boolean(u'1')
    (True, None)
    >>> form_data_to_boolean(u'  0  ')
    (False, None)
    >>> form_data_to_boolean(None)
    (False, None)
    >>> form_data_to_boolean(u'    ')
    (False, None)
    >>> form_data_to_boolean(u'true')
    (None, 'Value must be a boolean number')
"""

python_data_to_boolean = function(lambda value: bool(value))
"""Convert any Python data to a boolean.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_boolean(0)
    (False, None)
    >>> python_data_to_boolean(-1)
    (True, None)
    >>> python_data_to_boolean(u'0')
    (True, None)
    >>> python_data_to_boolean(u'1')
    (True, None)
    >>> python_data_to_boolean(u'true')
    (True, None)
    >>> python_data_to_boolean(u'false')
    (True, None)
    >>> python_data_to_boolean(u'  0  ')
    (True, None)
    >>> python_data_to_boolean(u'    ')
    (True, None)
    >>> python_data_to_boolean(None)
    (None, None)
    """

unicode_to_boolean = pipe(cleanup_line, clean_unicode_to_boolean)
"""Convert an unicode string to a boolean.

    Like most converters, a missing value (aka ``None``) is not converted.

    >>> unicode_to_boolean(u'0')
    (False, None)
    >>> unicode_to_boolean(u'1')
    (True, None)
    >>> unicode_to_boolean(u'  0  ')
    (False, None)
    >>> unicode_to_boolean(None)
    (None, None)
    >>> unicode_to_boolean(u'    ')
    (None, None)
    >>> unicode_to_boolean(u'true')
    (None, 'Value must be a boolean number')
"""

unicode_to_email = pipe(cleanup_line, clean_unicode_to_email)
"""Convert an unicode string to an email address.

    >>> unicode_to_email(u'spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> unicode_to_email(u'mailto:spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> unicode_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> unicode_to_email('root@127.0.0.1')
    (None, 'Invalid domain name')
    >>> unicode_to_email(u'root')
    (None, 'An email must contain exactly one "@"')
    >>> unicode_to_email(u'    spam@easter-eggs.com  ')
    (u'spam@easter-eggs.com', None)
    >>> unicode_to_email(None)
    (None, None)
    >>> unicode_to_email(u'    ')
    (None, None)
    """

unicode_to_float = pipe(cleanup_line, python_data_to_float)
"""Convert an unicode string to float.

    >>> unicode_to_float('42')
    (42.0, None)
    >>> unicode_to_float(u'   42.25   ')
    (42.25, None)
    >>> unicode_to_float(u'hello world')
    (None, 'Value must be a float')
    >>> unicode_to_float(None)
    (None, None)
    """


unicode_to_integer = pipe(cleanup_line, python_data_to_integer)
"""Convert an unicode string to an integer.

    >>> unicode_to_integer('42')
    (42, None)
    >>> unicode_to_integer(u'   42   ')
    (42, None)
    >>> unicode_to_integer(u'42.75')
    (None, 'Value must be an integer')
    >>> unicode_to_integer(None)
    (None, None)
    """

unicode_to_json = pipe(cleanup_line, clean_unicode_to_json)
"""Convert an unicode string to a JSON value.

    .. note:: This converter uses module ``simplejson``  when it is available, or module ``json`` otherwise.

    >>> unicode_to_json(u'{"a": 1, "b": 2}')
    ({u'a': 1, u'b': 2}, None)
    >>> unicode_to_json(u'null')
    (None, None)
    >>> unicode_to_json(u'   {"a": 1, "b": 2}    ')
    ({u'a': 1, u'b': 2}, None)
    >>> unicode_to_json(None)
    (None, None)
    >>> unicode_to_json(u'    ')
    (None, None)
    """


# Utility Functions


def to_value(converter, ignore_error = False):
    """Return a function that calls given converter and returns its result or raises an exception when an error occurs.

    >>> to_value(unicode_to_integer)(u'42')
    42
    >>> to_value(unicode_to_integer)(u'hello world')
    Traceback (most recent call last):
    ValueError: Value must be an integer
    >>> to_value(pipe(python_data_to_unicode, test_isinstance(unicode), unicode_to_boolean))(42)
    True
    """
    def to_value_converter(*args, **kwargs):
        value, error = converter(*args, **kwargs)
        if not ignore_error and error is not None:
            raise ValueError(error)
        return value
    return to_value_converter
