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
Weaver module.
The weaver defines how to (des)apply aspects on classes
or instances
"""

__revision__ = '$Id: weaver.py,v 1.28 2005-12-30 16:29:03 adim Exp $'

import new
import types
from inspect import getmembers, ismethod

from logilab.aspects._exceptions import AlreadyAspectedError, ClassNotWeaved, \
     AspectFailure

import sys, traceback


# PointCut Class ###############################################################
class PointCut(dict):
    """The PointCut class. A pointcut is a dict of breakpoints
    """

    def __init__(self):
        dict.__init__(self)

    
    def add_method(self, obj, met_name):
        """adds a method to the set of breakpoints
        obj = the class or instance
        met_name = the method name
        """
        if obj not in self:
            self[obj] = [met_name]
        else:
            self[obj].append(met_name)
        
    def remove_method(self, obj, met_name):
        """Removes a method from the breakpoints set
        obj = the class or instnace
        met_nae = the method name
        If obj is not in self, then we'll try to look
        for obj.__class__ if possible
        Raises a ValueError if obj (or obj.__class__) was in self
        but met_name wasn't
        Raises a KeyError if neither obj nor obj.__class__ were in self
        """
        # XXX FIXME, we should also search into base classes

        try:
            self[obj].remove(met_name)
        except KeyError:
            # Key Error <=> obj is not in self, so let's try obj.__class__
            try:
                self[obj.__class__].remove(met_name)
            except (AttributeError, KeyError):
                raise

    def remove_obj(self, obj):
        """Removes obj from self
        Returns 'obj' associated methods or None if obj was not in self.
        This will not search for obj.__class__ in self
        """
        try:
            method_names = self[obj]
            del self[obj]
            return method_names
        except KeyError:
            return None

        
    def update(self, other):
        """Redefines our update. We don't want to overwrite existing
        values, but rather merge both lists.
        other = the ohter pointcut
        """
        if not isinstance(other, dict):
            return

        for wobj, method_names in other.items():
            try:
                existing_list = self[wobj]
            except KeyError:
                self[wobj] = method_names
                continue

            for met_name in method_names:
                if met_name not in existing_list:
                    existing_list.append(met_name)
    

    def __sub__(self, other):
        """Returns a pointcut listing all breakpoints that are in 'self' and
        not in 'other'.
        """
        if not isinstance(other, PointCut):
            raise TypeError('Can only call sub between two PointCut instances !')
        
        result = PointCut()
        for obj, method_names in self.items():
            try:
                existing_list = other[obj]
            except KeyError:
                existing_list = []

            sub_list = [met_name for met_name in method_names
                        if met_name not in existing_list]
            if sub_list:
                result[obj] = sub_list

        return result

    
    def difference(self, other):
        """Returns a pointcut listing all breakpoints that are in 'self' and
        not in 'other'.

        difference <=> __sub__
        """
        return self - other
    
    
    
    def create_from_object(obj):
        """Static method that creates a PointCut with all the methods
        exisiting in obj.
        obj should either be a module object, a class object, or an instance
        object.
        """
        if type(obj) == types.ModuleType:
            return PointCut.create_from_module(obj)
        elif type(obj) in (types.InstanceType,
                            types.ClassType, types.TypeType):
            return PointCut.create_from_class(obj)
        

    def create_from_class(obj):
        """Static method that creates a PointCut from a class or class instance
        obj : the class or class instance
        """
        pointcut = PointCut()
        obj_dict = dict(getmembers(obj, ismethod))
        for met_name in obj_dict:
            if not met_name.startswith('__'):
                pointcut.add_method(obj, met_name)

        return pointcut
        
        
    def create_from_module(mod):
        """Static method that creates a PointCut from a module object
        mod : the module object
        """
        pointcut = PointCut()
        for obj_name in dir(mod):
            if not obj_name.startswith('_'):
                obj = getattr(mod, obj_name)
                obj_type = type(obj)
                if obj_type in (types.InstanceType,
                                types.ClassType, types.TypeType):
                    pointcut.update(PointCut.create_from_class(obj))
                    
        return pointcut
                        

    create_from_object = staticmethod(create_from_object)
    create_from_class = staticmethod(create_from_class)
    create_from_module = staticmethod(create_from_module)


# Method wrapper ###############################################################
from inspect import isclass
def wrap_method(aspect, weaved_object, met_name):
    """Wraps the method called 'met_name' in weaved_object
    """

    ####################################
    # The wrapper SCOPE begins here
    ####################################
    def wrapper(wobj, *args, **kwargs):
        """The wrapped method
        raises an AspectFailure if aspect fails
        """
        #
        context = {}

        context['method_name'] = met_name
        if isclass(weaved_object):
            context['__class__'] = weaved_object
        else:
            context['__class__'] = weaved_object.__class__
            
        exec_excpt = None # The exception raised by the wrapped method
        tcbk = None       # The exception's traceback

        # before is a shortcut for aspect.before => it's a bound method
        # (the real first arg (the aspect instance) is hidden here)
        # wobj represents the object weaved instance
        aspect.before(wobj, context, *args, **kwargs)

        
        # Catch the exception
        try:
            ret_v = aspect.around(wobj, context, *args, **kwargs)
            context['ret_v'] = ret_v
        except:
            dummy, exec_excpt, tcbk = sys.exc_info()
            # Skip the first element of the traceback which refers to
            # this method ('wrapped')
            tcbk_list = traceback.format_tb(tcbk)[1:]
            # Append traceback to exception args
            exec_excpt.args += (''.join(tcbk_list),)
            # According to Python Doc, not deleting tcbk would cause
            # a ref cycle
            # del tcbk
            context['ret_v'] = None

        context['exception'] = exec_excpt
            
        try:
            aspect.after(wobj, context, *args, **kwargs)
        except AspectFailure, failure:
            failure.set_method_exception(exec_excpt)
            raise # failure

        # If no exception, then return ret_v
        if not exec_excpt:
            return ret_v
        # Else, re-raise exception
        else:
            try:
                raise exec_excpt, None, tcbk
            finally:
                del tcbk

    ####################################
    # The wrapper SCOPE ends here
    ####################################

    original_method = getattr(weaved_object, met_name)
    # original_method = self._get_method(weaved_object, met_name)
    # This is important if we want the wrapped_func to behave
    # totally like the original one
    wrapper.__doc__ = original_method.__doc__
    
    if original_method.im_self is not None:
        met = new.instancemethod(wrapper, weaved_object,
                                 weaved_object.__class__)
    else:
        met = new.instancemethod(wrapper, None, weaved_object)
    # We need to setattr the new wrapper method
    setattr(weaved_object, met_name, met)



# The Weaver Class #############################################################
class _Weaver:
    """The Weaver class weaves aspects in classes
    A Weaver object is used to change the code of a class
    in order to weave an aspect.
    """

    def __init__(self):
        """ Initializes the woven dict
        """

        # An example of woven_dict :
        #  {'AClass': {'method_f': {'original' : ori_method,
        #                           'aspects' : [Aspect1,Aspect2]}},
        #   'AnotherClass': {'method_h': ... }
        #   }
        self.__woven_dict =  {}
        # aspect_dict is a map between aspect_classes and their
        # relatives pointcuts
        # The weaver makes the aspects behave like Singletons
        self.__aspect_dict = {}
        

    # Is it really useful ?
    def reset(self):
        """Re-initializes dictionnaries
        """
        self.__woven_dict = {}
        self.__aspect_dict = {}

    ## Weaver's WEAVE methods ##################################################
    def weave_object(self, obj, aspect_class, *args):
        """Weaves obj with aspect_class
        obj should be either a module, a class, or a class instance.
        """
        pointcut = PointCut.create_from_object(obj)
        self.weave_pointcut(pointcut, aspect_class, *args)
        

    def weave_module(self, mod, aspect_class, *args):
        """Will weave the aspect in all classes and instances
        found in module mod.
        The varargs list is used in the aspect's class __init__ method

        This method is here for convenience
        weave_module(mod, AspectClass) <=> weave_object(mod, AspectClass)
        """
        pointcut = PointCut.create_from_module(mod)
        self.weave_pointcut(pointcut, aspect_class, *args)
    
    
    def weave_methods(self, obj, aspect_class, *args):
        """ Will weave the aspect code in all the methods of obj
        obj : the class or class instance to weave
        aspect_class : the aspect's class we want to apply
        The varargs list is used in the aspect's class __init__ method

        This method is here for convenience
        weave_methods(obj, AspectClass) <=> weave_object(obj, AspectClass)
        """
        pointcut = PointCut.create_from_class(obj)
        self.weave_pointcut(pointcut, aspect_class, *args)
        

    def weave_pointcut(self, pointcut, aspect_class, *args):
        """Weaves the aspect code"""
        if aspect_class in self.__aspect_dict:
            aspect = self.__aspect_dict[aspect_class]
            unweaved_pointcut = pointcut - aspect.pointcut
        else:
            aspect = aspect_class(pointcut, *args)
            self.__aspect_dict[aspect_class] = aspect
            unweaved_pointcut = pointcut
        # Updates the pointcut BEFORE weaving because we need to
        # store the original method (= unweaved method) in aspect
        aspect.update_pointcut(pointcut)
        
        for obj, method_names in unweaved_pointcut.items():
            if type(obj) == types.InstanceType:
                # if object's class has already been aspected,
                # then don't rewrap its method, just add obj as a
                # key in the dict 
                if self.obj_class_is_aspected(obj, aspect_class):
                    print "Obj's class has already been aspected with ", \
                          aspect_class
                    continue
            # Add obj to the woven_dict if it's not already done
            if obj not in self.__woven_dict:
                self.__woven_dict[obj] = {}

            for met_name in method_names:
                self._weave_method(obj, met_name, aspect)



    def _weave_method(self, obj, met_name, aspect):
        """Weaves the aspect's code in met_name
        WARNING : aspect is an **INSTANCE** here
        """
        weaved_methods =  self.__woven_dict[obj]
        if met_name not in weaved_methods:
            self.__woven_dict[obj][met_name] = {
                'original' : getattr(obj, met_name),
                'aspects' : []
                }
        try:
            self._register_aspect(obj, met_name, aspect)
        except AlreadyAspectedError, excpt:
            print "already aspected : ", excpt
            return
        wrap_method(aspect, obj, met_name)

    ## Weaver's UNWEAVE methods ################################################
    def unweave_pointcut(self, pointcut, aspect_class):
        """Unweaves the aspect_class in all the pointcut
        """
        for weaved_object, method_names in pointcut.items():
            for met_name in method_names:
                self._unweave_method(weaved_object, met_name, aspect_class)

            if not self.__woven_dict[weaved_object]:
                del self.__woven_dict[weaved_object]
        
        aspect = self.__aspect_dict[aspect_class]
        # Remove this pointcut part from aspect.pointcut
        aspect.set_pointcut(aspect.pointcut - pointcut)
        # Check if aspect.pointcut still contains an element
        # If not, then this aspect is no longer used, delete it !
        if not aspect.pointcut:
            del self.__aspect_dict[aspect_class]

    
    def unweave_methods(self, obj, aspect_class):
        """Unweaves the aspect_class in all obj's methods

        This method is here for convenience
        unweave_methods(obj, AspectClass) <=> unweave_methods(obj, AspectClass)
        """
        pointcut = PointCut.create_from_class(obj)
        self.unweave_pointcut(pointcut, aspect_class)
        

    def unweave_module(self, mod, aspect_class):
        """Unweaves the aspect_class in all mod's objects

        This method is here for convenience
        unweave_module(mod, AspectClass) <=> unweave_object(mod, AspectClass)
        """
        pointcut = PointCut.create_from_module(mod)
        self.unweave_pointcut(pointcut, aspect_class)

        
    def unweave_object(self, obj, aspect_class):
        """Unweaves the aspect_class in all obj.
        obj should be either a module, a class, or a class instance.        
        """
        pointcut = PointCut.create_from_object(obj)
        self.unweave_pointcut(pointcut, aspect_class)
        

    def _unweave_method(self, obj, met_name, aspect_class):
        """Unweaves aspect code from met_name
        """
        weave_info = self.__woven_dict[obj][met_name]
        
        pointcut = PointCut()
        pointcut.add_method(obj, met_name)
        
        aspects = weave_info['aspects']

##         # Remove this method from the aspect's pointcut
##         for aspect in aspects:
##             aspect.set_pointcut(aspect.pointcut - pointcut)
            
        
        # Make a list of all remaining aspects
        remaining_aspects = [aspect for aspect in aspects
                             if aspect.__class__ != aspect_class]
        
        weave_info['aspects'] = []
        # Retreive the base method (with no wrap at all)
        base_method = weave_info['original']
        
        setattr(obj, met_name, base_method)
        # The new method is the base method wrapped by all
        # remaining aspects
        for aspect in remaining_aspects:
##             aspect._methods[obj][met_name] = (getattr(obj, met_name), \
##                                              base_method)
            aspect.update_pointcut(pointcut)
            self._weave_method(obj, met_name, aspect)

        if not remaining_aspects:
            del self.__woven_dict[obj][met_name]

        

    ## Weaver's Helper Part ####################################################
    def _register_aspect(self, obj, met_name, aspect):
        """Adds an aspect in the woven_dict
        obj : the class (or class instance)
        met_name : the method's name
        aspect : the aspect to add
        """
        aspect_list = self.__woven_dict[obj][met_name]['aspects']
        for added_aspect in aspect_list:
            if added_aspect.__class__ == aspect.__class__:
                raise AlreadyAspectedError, "%s is already aspected with %s"% \
                      (met_name, aspect.__class__.__name__)
            
        aspect_list.append(aspect)
    

    def obj_class_is_aspected(self, obj, aspect_class):
        """ Checks if 
        obj : the object to check
        aspect_class : the aspect_class

        returns True if aspect_class has already been woven in
        obj's class
        """
        if not hasattr(obj, '__class__'):
            return False
        
        if obj.__class__ in self.__woven_dict:
            class_info = self.__woven_dict[obj.__class__]
            aspect_classes = [aspect_class for aspect_class in class_info]
            if aspect_class in aspect_classes:
                # self.__woven_dict[obj] = dict(class_info)
                return True

        return False

    def get_weaved_classes(self):
        """Returns the list of the aspected classes
        """
        weaved_objects = self.__woven_dict.keys()
        return [weaved for weaved in weaved_objects
                if type(weaved) == types.ClassType]

    def get_weaved_instances(self):
        """Returns the list of the aspected instances
        """
        weaved_objects = self.__woven_dict.keys()
        return [weaved for weaved in weaved_objects
                if type(weaved) != types.ClassType]

    def get_weaved_methods(self, cls):
        """
        cls : the class to look at
        returns the weaved methods' names
        """
        try:
            return self.__woven_dict[cls].keys()
        except KeyError:
            raise ClassNotWeaved, "%s is not weaved" % cls
        

    def get_aspects(self, obj, met_name):
        """Returns the list of aspects weaved for a method
        obj : the class or class instance to look at
        met_name : the method's name
        """
        try:
            return self.__woven_dict[obj][met_name]['aspects']
        except KeyError:
            raise ClassNotWeaved, "%s.%s is not weaved " % (obj, met_name)


    def get_aspect(self, aspect_class):
        """Returns the aspect instance of class aspect_class that was
        weaved into classes, or None is no aspect was found
        """
        try:
            return self.__aspect_dict[aspect_class]
        except KeyError:
            return None
        

    def get_original_method(self, obj, met_name):
        """Returns a tuple containing the original method (<=> not aspected)
        and the result of getattr(obj, met_name).

        Note : The second element is only returned for convenience
        
        obj : the class (or class instance)
        met_name : the method's name
        If 'get_original_method' didn't find the method, AND if 'obj' is an
        instance, then it will try to look for obj.__class__ entry. If the
        method is then found, it is returned.
        If method is not weaved, then getattr(obj, met_name) is returned
        # Raises a KeyError if method was not weaved.
        """
        basemethod = method = getattr(obj, met_name)
        try:
            basemethod = self.__woven_dict[obj][met_name]['original']
        except KeyError:
            # if the method wasn't found AND if 'obj' is an isntance,
            # try to look at the obj.__class__ entry (convenience behaviour)
            if type(obj) == types.InstanceType:
                klass = obj.__class__
                try:
                    basemethod = self.__woven_dict[klass][met_name]['original']
                except KeyError:
                    return basemethod, method
        return basemethod, method
    
    
    def __str__(self):
        info  = []
        for cls, methods in self.__woven_dict.items():
            if type(cls) == types.ClassType:
                info.append('Class %s : ' % cls.__name__)
            else:
                info.append('Class %s : ' % cls)
            for met_name, method_info in methods.items():
                aspects = method_info['aspects']
                info.append('\tAspects weaved for method %s : '%met_name)
                for aspect in aspects:
                    info.append('\t\t - %s'%aspect)
        return '\n'.join(info)


# create global instance
weaver = _Weaver()
del _Weaver
