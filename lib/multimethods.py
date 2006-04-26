# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0142
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
Aspect that implements multimethods in Python in an AOP way.

Still lacks :
    - inheritance management
    - default arg types (even in no default args)
    - keywords args (**)  management
"""


__revision__ = '$Id: multimethods.py,v 1.11 2005-12-30 16:29:08 adim Exp $'

from logilab.aspects.core import AbstractAspect


class DispatchRule:
    """Defines how to dispatch methods
    """

    def __init__(self, original_name, dest_name, arg_classes):
        """
        original_name : the orignal method's name
        arg_classes : the argument types for this rule
        """
        self.original_name = original_name
        self.dest_name = dest_name
        self.arg_classes = arg_classes


    def match_func_call(self, func_args):
        """Tests if the dynamic types match this rules'types
        func_args : the list of args
        returns True if matches, else, False.
        """

        if len(func_args) != len(self.arg_classes):
            return False
        
        index = 0
        for arg in func_args:
            if arg.__class__ != self.arg_classes[index]:
                return False
            index += 1
        
        return True
        


class DispatcherAspect(AbstractAspect):
    """ Dispatcher aspect allows use of multimethods in Python
    """

    def __init__(self, pointcut, rules):
        """
        cls : class or instance to aspect
        method_name : the method name
        rules : the multimethod rules
        """
        AbstractAspect.__init__(self, pointcut)
        
        self.rules = rules        
    
    def around(self, wobj, context, *args, **kwargs):
        """Dispatcher around implementation
        """

        met_name = context['method_name']
        method_rules = [rule for rule in self.rules
                        if rule.original_name == met_name]

        for rule in method_rules:
            if rule.match_func_call(args):
                dest_met_name = rule.dest_name

        klass = context['__class__']
        try:
            method = getattr(klass, dest_met_name)
        except AttributeError:
            method = getattr(wobj, dest_met_name)
        return method.im_func(wobj, *args, **kwargs)
    


    
