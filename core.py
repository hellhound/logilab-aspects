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
Core module.
Defines base aspect class
"""

__revision__ = '$Id: core.py,v 1.16 2005-12-30 16:29:02 adim Exp $'


# XXX FIXME : importing weaver instance surely means bad conception :
# These two modules should be totally independant
from logilab.aspects.weaver import weaver

class AbstractAspect(object):
    """ Abstract Class for all aspects
    """

    def __init__(self, pointcut):
        """
        pointcut = the program pointcut
        """
        # Do not directly assign with pointcut since it will be done
        # in update_pointcut()
        self.pointcut = pointcut
        self._methods = {}
        
        # self.update_pointcut(pointcut)
        self._update_methods(pointcut)


    def update_pointcut(self, pointcut):
        """Updates self.pointcut and self._methods according to pointcut
        """
        # diff = pointcut - self.pointcut
        self.pointcut.update(pointcut)
        self._update_methods(pointcut) # diff ?

    def _update_methods(self, pointcut):
        """Updates the _method dictionnary
        Only updates methods that weren't in the pointcut
        """
        for weaved_object, method_names in pointcut.items():
            method_map = self._methods.get(weaved_object, {})
            for met_name in method_names:
                base_method, method = weaver.get_original_method(weaved_object,
                                                                 met_name)
                method_map[met_name] = (method, base_method)
                # base_method.im_func.func_globals
            self._methods[weaved_object] = method_map
        

    def set_pointcut(self, pointcut):
        """Sets the aspect pointcut
        """
        self.pointcut = pointcut
        self.update_pointcut(self.pointcut)
        
        
    def before(self, wobj, context, *args, **kwargs):
        """Define Here what you want to do before the method call
        """
        pass

    def after(self, wobj, context, *args, **kwargs):
        """Define Here what you want to do after the method call
        """
        pass

    def around(self, wobj, context, *args, **kwargs):
        """Define Here what you want to do around the method call
        around MUST call PROCEED !!
        """
        met_name = context['method_name']
        wclass = context['__class__']
        return self._proceed(wobj, wclass, met_name, *args, **kwargs)

    def _proceed(self, wobj, wclass, met_name, *args, **kwargs):
        """The real call
        """
        # XXX FIXME : ugly code, and not bugsafe !
        method = self._get_method(wobj, wclass, met_name)
        return method.im_func(wobj, *args, **kwargs)
    
    
    def _get_method(self, wobj, wclass, met_name):
        """Will try to find the appropriate method object according
        to wobj and met_name.
        Raises a KeyError if method cannot be found.
        """
        try:
            return self._methods[wobj][met_name][0]
        except KeyError:
            return self._methods[wclass][met_name][0]
        

    def _get_base_method(self, wobj, met_name):
        """Will try to find the appropriate base method object according
        to wobj and met_name.
        Raises a KeyError if method cannot be found.

        _get_base_method differs from _get_method because it will return
        the base method (i.e. the non aspected one) meanwhile _get_method
        will return the method as it was before this aspect was weaved.
        """
        try:
            return self._methods[wobj][met_name][1]
        except KeyError:
            return self._methods[wobj.__class__][met_name][1]
    


    def __str__(self):
        return self.__class__.__name__

