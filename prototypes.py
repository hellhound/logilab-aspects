# -*- coding: ISO-8859-1 -*-
# Copyright (c) 2003-2006 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
This module defines utilities functions to manage functions' prototypes.
"""

__revision__ = '$Id: prototypes.py,v 1.13 2005-12-30 16:29:02 adim Exp $'

import types

def reassign_function_arguments(method, varargs, kwargs):
    """This methods will analyze the prototype of method.

    To wrap a method easily, the most common way to do is
    to declare a simple prototype : def wrapper(self, *args, **kwargs)
    which can match any possible call.
    The problem is that you can't use variable_names originally passed
    in argument of the wrapped function/method.
    Suppose you have : 'def f(arg1, arg2)', your wrapper will be
    'def f_wrapper(*args, **kwargs)' and you then can neither use 'arg1'
    and 'arg2' in the scope of f_wrapper.
    reassign_function_arguments builds a dict (a kind of locals()) with
    the names of the args of the original function in KEYS, and the values
    with which they were called in VALUES.

    returns this dict. (You might use this function like this :

        def a_wrapper(self, *args, **kwargs):
            locals().update(reassign_function_arguments(ori_method,args,kwargs))
            ...

    """
    code = method.func_code
    assignment_dict = {}
    var_offset = 0
    default_values = ()
    
    if type(method) == types.MethodType:
        # if it's a method => skip 'self' from the variable arg list
        var_offset = 1
    
    # Get all arg names (without defaults / keywords)
    arg_list = code.co_varnames[var_offset:code.co_argcount]
    
    # Build the tuple of default values : will hold all the values
    # (in the right order) of all values which haven't been passed to
    # the method.

    # If the method has default arg values
    if method.func_defaults is not None:
        # Take the N right most values in func's default values
        # where N is the number of unspecified variables in the
        # method call.
        default_index = len(arg_list) - len(varargs)
        if default_index > 0:
            default_values = method.func_defaults[-default_index:]
    # Else : no default values for the method args

    # Reassign all values to their variables
    # len(arg_list) = len(varargs+default_values)
    index = 0
    passed_values = varargs+default_values
    if len(passed_values) > len(arg_list):
        raise TypeError('%s() takes at most %s arguments (%s given)' %
                        (method.__name__, len(arg_list),
                         len(passed_values)))
    for val in passed_values:
        assignment_dict[arg_list[index]] = val
        index += 1

    # Reassign keywords values if necessary
    for var, val in kwargs.items():
        assignment_dict[var] = val

    # Return dict
    return assignment_dict

