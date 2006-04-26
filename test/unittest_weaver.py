# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=C0103,W0232,R0904,C0102,W0404,R0801
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
Unit tests for Weaver
"""

__revision__ = '$Id: unittest_weaver.py,v 1.27 2005-12-30 16:29:16 adim Exp $'


import unittest
import sys

from logilab.aspects.weaver import weaver, wrap_method, PointCut
from logilab.aspects.lib.contracts import ContractAspect, ContractFailedError
from logilab.aspects.lib.logger import LoggerAspect
from logilab.aspects.lib.profiler import ProfilerAspect
from logilab.aspects._exceptions import ClassNotWeaved

import module_test

from sets import Set
from cStringIO import StringIO

class Test:
    """Small class used in Weaver_ClassTest
    """
    def foo(self, val):
        """
        pre:
            val < 10
        """
        if val >= 10:
            raise ValueError("just for tests ...")
        

    def bar(self):
        """ nothing to do ...
        """
        pass


class WeaverTC(unittest.TestCase):
    """TestCase for the aspect weaver.
    """

    def setUp(self):
        """setUp method for tests
        """
        self.instance = Test()
        self.klass    = Test
        self.log_device = sys.stdout
        self.mod = module_test
        weaver.reset()
        # redirect sys.stdout for convenience
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        
    def tearDown(self):
        """unweave aspects"""
        for obj in (self.klass, self.mod, self.instance):
            for aspect_class in (ContractAspect, LoggerAspect, ProfilerAspect):
                try:
                    weaver.unweave_object(obj, aspect_class)
                except:
                    pass
        sys.stdout = self.old_stdout
    
    
    def test_weave_methods(self):
        """Tests if the weaver weaves correctly methods
        """
        old_foo = getattr(self.instance, 'foo')
        old_bar = getattr(self.instance, 'bar')
        weaver.weave_methods(self.instance, ContractAspect)
        self.assert_(self.instance in weaver._Weaver__woven_dict)
        self.assert_(self.klass not in weaver._Weaver__woven_dict)
        new_foo = getattr(self.instance, 'foo')
        new_bar = getattr(self.instance, 'bar')
        self.assert_(old_foo != new_foo)
        self.assert_(old_bar != new_bar)


    def test_weave_object_class(self):
        """tests Weaver.weave_object() for a class"""
        weaver.weave_object(self.klass, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        another_instance = Test()
        self.assertRaises(ContractFailedError, another_instance.foo, 15)


    def test_weave_object_instance(self):
        """tests Weaver.weave_object() for an instance"""
        weaver.weave_object(self.instance, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        another_instance = Test()
        # In another instance : contracts are not activated, this should pass !
        self.assertRaises(ValueError, another_instance.foo, 15)

        
    def test_weave_object_module(self):
        """tests Weaver.weave_module() for an instance"""
        weaver.weave_object(self.mod, ContractAspect)
        stack = self.mod.StackImpl(3)
        self.assertRaises(ContractFailedError, stack.pop)

        
    def test_weave_instance(self):
        """Tests if only the right instance is weaved
        """
        weaver.weave_methods(self.instance, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        another_instance = Test()
        # In another instance : contracts are not activated, this should pass !
        self.assertRaises(ValueError, another_instance.foo, 15)
        

    def test_weave_class(self):
        """Tests if all new instances of a class are also weaved
        """
        weaver.weave_methods(self.klass, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        another_instance = Test()
        self.assertRaises(ContractFailedError, another_instance.foo, 15)


    def test_unweave_methods(self):
        """Tests if the weaver unweaves correctly methods
        """
        weaver.weave_methods(self.klass, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        weaver.unweave_methods(self.klass, ContractAspect)
        # Contracts are no more activated : this should pass !
        self.assertRaises(ValueError, self.instance.foo, 15)
        # Test on instances
        another_instance = Test()
        weaver.weave_methods(self.instance, ContractAspect)
        weaver.weave_methods(another_instance, ContractAspect)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        self.assertRaises(ContractFailedError, another_instance.foo, 15)
        weaver.unweave_methods(self.instance, ContractAspect)
        # Contracts are no more activated on self.instance: this should pass !
        self.assertRaises(ValueError, self.instance.foo, 15)
        # They should be still activated on another_instance
        self.assertRaises(ContractFailedError, another_instance.foo, 15)
        

    def test_multiple_weaving(self):
        """Tests if multiple aspects can be (un)weaved
        """
        log_device = open('tests.log','w')
        weaver.weave_methods(self.instance, ContractAspect)
        weaver.weave_methods(self.instance, LoggerAspect, log_device)
        self.assert_(len(weaver.get_aspects(self.instance,
                                                 'foo')) == 2)
        self.instance.foo(5)
        self.assertRaises(ContractFailedError, self.instance.foo, 15)
        weaver.unweave_methods(self.instance, ContractAspect)
        self.assert_(len(weaver.get_aspects(self.instance,
                                                 'foo')) == 1)
        # Tests if the remaining Aspect is not the Contract one.
        self.assertRaises(ValueError, self.instance.foo, 15)
        log_device.close()


    def test_weave_module(self):
        """Tests if module's weaving works correctly
        """
        weaver.weave_module(self.mod, ContractAspect)
        stack = self.mod.StackImpl(3)
        self.assertRaises(ContractFailedError, stack.pop)


    def test_unweave_module(self):
        """Tests if module's unweaving works correctly
        """
        weaver.weave_module(self.mod, ContractAspect)
        weaver.unweave_module(self.mod, ContractAspect)
        # Create a stack of max_size = 1 and push 2 elements
        # if module has been unweaved, this should be ok !
        stack = self.mod.StackImpl(1)
        stack.push(1)
        stack.push(2)


    def test_unweave_pointcut(self):
        """tests unweave() for pointcuts"""
        pcut = PointCut()
        pcut.add_method(self.klass, 'foo')
        weaver.weave_pointcut(pcut, ContractAspect)
        self.assertEquals(
            len(weaver.get_aspects(self.klass, 'foo')), 1)
        weaver.unweave_pointcut(pcut, ContractAspect)
        self.assertEquals(weaver.get_aspect(ContractAspect), None)
        

    def test_weave_same_aspect(self):
        """Checks that weaver forbids weaving multiple time the same
        aspect on a method.
        """
        weaver.weave_object(self.klass, ContractAspect)
        old_aspects = weaver.get_aspects(self.klass, 'foo')
        # Trying to weave a second time
        weaver.weave_object(self.klass, ContractAspect)
        new_aspects = weaver.get_aspects(self.klass, 'foo')
        self.assert_(old_aspects == new_aspects)
        # Now trying to weave on self.instance should produce warnings
        old_foo = self.instance.foo
        weaver.weave_methods(self.instance, ContractAspect)
        # self.instance.foo should not have been modified !
        self.assertEquals(old_foo, self.instance.foo)


    def test_register_aspect(self):
        """tests() aspect registration"""
        old_foo = self.instance.foo
        weaver.weave_object(self.klass, ContractAspect)
        # instances of self.klass must have been aspected !
        self.assertNotEquals(old_foo, self.instance.foo)
        contract = weaver.get_aspect(ContractAspect)
        old_foo = self.instance.foo
        # Trying to reaspect self.instance should not change its methods
        weaver._weave_method(self.klass, 'foo', contract)
        self.assertEquals(old_foo, self.instance.foo)

    
    def test_already_aspected(self):
        """tests weaver.obj_class_is_aspected()"""
        self.assertEquals(weaver.obj_class_is_aspected(self.instance,
                                                       ContractAspect),
                          False)
        weaver.weave_object(self.klass, ContractAspect)
        # obj_class_is_aspected() always returns False on classes
        self.assertEquals(weaver.obj_class_is_aspected(self.klass,
                                                       ContractAspect),
                          False)
        # but make sure it returns True on the aspected instance
        self.assertEquals(weaver.obj_class_is_aspected(self.instance,
                                                       ContractAspect),
                          True)
        

    def test_wrapped_method_doc(self):
        """ensures that wrapper and wrapped have the same docstring"""
        # Memorize old method object
        original_meth = self.instance.foo
        # Build simple pointcut on self.instance.foo
        pointcut = PointCut()
        pointcut.add_method(self.instance, 'foo')
        # Wrap method
        wrap_method(ContractAspect(pointcut), self.instance, 'foo')
        # Check new method object is not the old none
        wrapped_meth = self.instance.foo
        self.assert_(original_meth is not wrapped_meth,
                     "wrapped method should not have the same identity !")
        # Check docstrings are equal
        self.assertEquals(original_meth.__doc__, wrapped_meth.__doc__)


    def test_weaver_str(self):
        """ensures str cannot raise an exception"""
        weaver.weave_methods(self.instance, ContractAspect)
        str(weaver)
        class SomeClass:
            """some class to weave"""
            def some_method(self):
                """a method"""
        weaver.weave_methods(SomeClass, ContractAspect)
        str(weaver)
        

    def test_get_weaved_classes(self):
        """tests get_weaved_classes()"""
        class SomeClass:
            """some class to weave"""
            def some_method(self):
                """a method"""
        weaver.weave_object(self.klass, ContractAspect)
        weaver.weave_object(SomeClass, ContractAspect)
        classnames = [klass.__name__ for klass in weaver.get_weaved_classes()]
        classnames.sort()
        self.assertEquals(classnames, ['SomeClass', 'Test'])


    def test_get_weaved_instances(self):
        """tests weaved instances"""
        weaver.weave_object(self.instance, ContractAspect)
        instances = weaver.get_weaved_instances()
        self.assertEquals(instances, [self.instance])


    def test_get_aspect(self):
        """tests weaver.get_aspect()"""
        aspect = weaver.get_aspect(ProfilerAspect)
        self.assertEquals(aspect, None)
        weaver.weave_object(self.klass, ProfilerAspect)
        aspect = weaver.get_aspect(ProfilerAspect)
        self.assertEquals(isinstance(aspect, ProfilerAspect), True)


    def test_get_aspects(self):
        """tests weaver.get_aspects()"""
        class SomeClass:
            """a simple class"""
            def foo(self):
                """a simple method"""
        self.assertRaises(ClassNotWeaved, weaver.get_aspects, SomeClass, 'foo')
        weaver.weave_object(SomeClass, ProfilerAspect)
        weaver.weave_object(SomeClass, ContractAspect)
        aspects = weaver.get_aspects(SomeClass, 'foo')
        classes = [aspect.__class__ for aspect in aspects]
        self.assertEquals(classes, [ProfilerAspect, ContractAspect])

    
    def test_get_weaved_methods(self):
        """test weaved methods list"""
        self.assertRaises(ClassNotWeaved, weaver.get_weaved_methods,
                          self.klass)
        weaver.weave_object(self.klass, ProfilerAspect)
        method_names = Set(['foo', 'bar'])
        self.assertEquals(Set(weaver.get_weaved_methods(self.klass)),
                          method_names)
        

class Base:
    """base class"""
    def __init__(self):
        self.trace = []
        
    def some_method(self):
        """Base.some_method()"""
        self.trace.append('Base')
        
class Extended(Base):
    """extended class"""
    def some_method(self):
        """Extended.some_method"""
        self.trace.append('Extended')
        Base.some_method(self)


class InheritanceTC(unittest.TestCase):

    def setUp(self):
        """setUp method for tests
        """
        self.ext = Extended()
        self.base = Base()
        weaver.reset()
        # redirect sys.stdout for convenience
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()
        self.log_device = sys.stdout
        
    def tearDown(self):
        """unweave aspects"""
        for obj in (self.ext, self.base):
            for aspect_class in (ContractAspect, LoggerAspect, ProfilerAspect):
                try:
                    weaver.unweave_object(obj, aspect_class)
                except:
                    pass
        sys.stdout = self.old_stdout
    
    def test_weaving_impact(self):
        """make sure weaving base class doesn't impact extended class"""
        ext_orig = self.ext
        ext_orig = Extended.some_method
        base_orig = Base.some_method
        weaver.weave_object(Extended, LoggerAspect, self.log_device)
        ext_mid = Extended.some_method
        base_mid = Base.some_method
        # Weaving on extended class should not affect Base class
        self.assertNotEquals(ext_orig, ext_mid)
        self.assertEquals(base_orig, base_mid)
        weaver.weave_object(Base, LoggerAspect, self.log_device)
        ext_final = Extended.some_method
        base_final = Base.some_method
        # Weaving on Base class should not affect already weaved Extended class
        self.assertEquals(ext_mid, ext_final)
        self.assertNotEquals(base_mid, base_final)
        

    def test_who_is_called(self):
        """test which wrapper function is choosed"""
        weaver.weave_object(Extended, LoggerAspect, self.log_device)
        weaver.weave_object(Base, LoggerAspect, self.log_device)
        self.ext.some_method()
        self.assertEquals(self.ext.trace, ['Extended', 'Base'])
        self.ext.trace = []
        Base.some_method(self.ext)
        self.assertEquals(self.ext.trace, ['Base'])
        self.ext.trace = []
        Extended.some_method(self.ext)
        self.assertEquals(self.ext.trace, ['Extended', 'Base'])
        
        

class PointCutTC(unittest.TestCase):
    """Tests PointCut objects' behaviour"""
    def setUp(self):
        """just build an empty pointcut, and a basic object"""
        self.pointcut = PointCut()
        self.an_obj = object()


    def test_add_method(self):
        """tests PointCut.add_method()"""
        self.pointcut.add_method(self.an_obj, "method1")
        self.assertEquals(self.pointcut.items(), [(self.an_obj, ["method1"])])
        self.pointcut.add_method(self.an_obj, "method2")
        self.assertEquals(self.pointcut.items(),
                          [(self.an_obj, ["method1", "method2"])])


    def test_remove_method(self):
        """tests PointCut.remove_method()"""
        # We know this statement works thanks to test_add_method()
        self.pointcut.add_method(self.an_obj, "method1")
        self.pointcut.add_method(self.an_obj, "method2")
        self.pointcut.remove_method(self.an_obj, "method1")
        self.assertEquals(self.pointcut.items(), [(self.an_obj, ["method2"])])
        self.pointcut.remove_method(self.an_obj, "method2")
        self.assertEquals(self.pointcut.items(), [(self.an_obj, [])])
        

    def test_remove_unadded_method(self):
        """ensures PointCut.remove_method() raises a KeyError"""
        self.assertRaises(KeyError, self.pointcut.remove_method,
                          self.an_obj, "foo")
        self.assertRaises(KeyError, self.pointcut.remove_method,
                          object, "foo")
        
        
    def test_remove_class_method(self):
        """tests the try...except statement of remove_method()
        FIXME : Do we really want this behaviour ?!
        """
        self.pointcut.add_method(object, "method1")
        self.pointcut.remove_method(self.an_obj, "method1")
        self.assertEquals(self.pointcut.items(), [(object, [])])


    def test_remove_obj(self):
        """tests PointCut.remove_obj()"""
        method_names = ['method1', 'method2', 'method3']
        for name in method_names:
            self.pointcut.add_method(self.an_obj, name)
        removed_methods = self.pointcut.remove_obj(self.an_obj)
        self.assertEquals(method_names, removed_methods)
        self.assertEquals(len(self.pointcut), 0)
        

    def test_remove_unadded_obj(self):
        """ensures removing unadded object returns None"""
        removed_methods = self.pointcut.remove_obj(self.an_obj)
        self.assertEquals(removed_methods, None)
        

    def test_pointcut_update(self):
        """tests PointCut.update()"""
        other = PointCut()
        other.add_method(self.an_obj, "method2")
        self.pointcut.add_method(self.an_obj, "method1")
        self.pointcut.update(other)
        self.assertEquals(self.pointcut.values(), [["method1", "method2"]])

        
    def test_pointcut_update_notdict(self):
        """tests PointCut.update() when arg is not a dict"""
        # Test updating with a list
        other = []
        self.assertEquals(self.pointcut.update([]), None)
        self.assertEquals(len(self.pointcut), 0)


    def test_pointcut_difference(self):
        """tests PointCut.difference()"""
        method_names = ['method1', 'method2', 'method3']
        for name in method_names:
            self.pointcut.add_method(self.an_obj, name)
        other = PointCut()
        other.add_method(self.an_obj, "method1")
        result = self.pointcut - other
        self.assertEquals(result.values(), [["method2", "method3"]])


    def test_same_pointcut_difference(self):
        """tests pcut - pcut == {} """
        self.assertEquals(self.pointcut - self.pointcut, {})
    
        
    def test_pointcut_difference_notpointcut(self):
        """ensures __sub__ raises a TypeError when not used with PointCut"""
        other = []
        self.assertRaises(TypeError, self.pointcut.difference, other)


    def test_create_from_object(self):
        """tests PointCut.create_from_object()"""
        pointcut = PointCut.create_from_object(Test)
        keys = pointcut.keys()
        values = pointcut.values()
        values.sort()
        self.assertEquals(keys, [Test])
        self.assertEquals(values, [["foo", "bar"]])


    def test_create_from_object_module(self):
        """tests PointCut.create_from_object when it's a module"""
        pointcut = PointCut.create_from_object(module_test)
        keys = Set([obj.__name__ for obj in pointcut.keys()])
        self.assertEquals(keys, Set(['Stack', 'StackImpl', 'Sorter']))
        stack_methods = Set(pointcut[module_test.Stack])
        stackimpl_methods = Set(pointcut[module_test.Stack])
        sorter_methods = Set(pointcut[module_test.Sorter])
        self.assertEquals(stack_methods, Set(['is_empty', 'is_full', 'pop',
                                              'push', 'size', 'top']))
        self.assertEquals(stackimpl_methods, Set(['is_empty', 'is_full', 'pop',
                                                  'push', 'size', 'top']))
        self.assertEquals(sorter_methods, Set(['sort']))
        

class ProfilerTC(unittest.TestCase):
    """a basic profiler test case (FIXME: really needs more work)"""
    def setUp(self):
        """setUp method for tests
        """
        self.instance = Test()
        weaver.reset()
    
    def tearDown(self):
        """unweave aspects"""
        weaver.unweave_object(Test, ProfilerAspect)
    
    def test_dump_profiles_html(self):
        """tests that dump_profiles_html() doesn't raise an exception"""
        weaver.weave_object(Test, ProfilerAspect)
        self.instance.bar()
        aspect = weaver.get_aspect(ProfilerAspect)
        stream = StringIO()
        aspect.dump_profiles_html(stream)
            

    def test_dump_readable_profiles(self):
        """tests that dump_readable_profiles() doesn't raise an exception"""
        weaver.weave_object(Test, ProfilerAspect)
        self.instance.bar()
        aspect = weaver.get_aspect(ProfilerAspect)
        stream = StringIO()
        aspect.dump_readable_profiles(stream)
            
     
if __name__ == '__main__':
    unittest.main()
