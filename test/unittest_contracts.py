# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0613,W0142,W0232,C0103,R0904,W0404,R0801
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
Unit tests for aspects
"""

__revision__ = '$Id: unittest_contracts.py,v 1.17 2005-12-30 16:29:13 adim Exp $'


import unittest
import sys

from logilab.aspects.weaver import weaver
from logilab.aspects.lib.contracts import ContractAspect, ContractFailedError, \
     forall, exists, parse_docstring, get_ancestors_conditions
import module_test


class SillyClass:
    """
    inv:
        self.invariant == 12
    """
    def __init__(self):
        self.invariant = 12
    
    def silly_func(self, value, *args, **kwargs):
        """
        pre:
            value < 10
        post:
            type(__return__) == type('') and int(__return__) < 15
            # Silly condition (just for tests on __old__)
            __old__.value != __old__.self.invariant
        """
        return "%d" % value
    

    def bad_post(self, val, *args, **kwargs):
        """
        pre:
            val < 10
        post:
            type(__return__) == type('') and int(__return__) < 15
        """
        
        return "20"


    def sort(self, array):
        """
        post:
            # array size is unchanged
            len(array) == len(__old__.array)
        
            # array is ordered
            forall([array[i] >= array[i-1] for i in range(1, len(array))])
        """
        array.sort()


    def corrupt(self):
        """This method will raise an exception after changing
        invariant to check that invariant are still checked even
        if an exception was raised
        """
        self.invariant = 14
        raise Exception("...")


    def post_strength(self):
        """
        post:
            __return__ < 10
        """
        return 5

    
    
class SillySubclass(SillyClass):
    """Just a class to test inheritance csq in contracts
    """

    def __init__(self):
        SillyClass.__init__(self)
        self.age = 12
        
    def silly_func(self, value, *args, **kwargs):
        """
        pre:
            True
        ---
        post:
            self.age == __old__.self.age * 2
        """        
        self.age *= 2
        return "%d" % value


    def bad_post(self, val, *args, **kwargs):
        """ Always bad post condition !
        """
        return 20


    def post_strength(self):
        """
        post
            __return__ > 5
        """
        return 5


class ContractTC(unittest.TestCase):
    """TestCase for aspects
    """

    def setUp(self):
        """setUp method for tests
        """
        self.a = SillyClass()
        self.b = SillySubclass()
        weaver.weave_methods(self.a, ContractAspect)
        weaver.weave_methods(self.b, ContractAspect)
        weaver.get_aspect(ContractAspect)
        # self.aspect = ContractAspect(SillySubclass,'silly_func')
        
    def test_pre_conditions(self):
        """Tests if preconditions work
        """
        self.a.silly_func(3)
        self.assertRaises(ContractFailedError, self.a.silly_func, 20)
    

    def test_post_conditions(self):
        """Tests if postconditions work"""
        self.assertRaises(ContractFailedError, self.a.bad_post, 5)
        
        
    def test_parse_docstring(self):
        """tests parse_docstring()"""
        self.assertEquals(parse_docstring(""), ([], [], []))
        docstring = SillySubclass.silly_func.__doc__
        pre, post, inv = parse_docstring(docstring)
        self.assertEquals(pre, ['True'])
        self.assertEquals(post, ["self.age == __old__.self.age * 2"])
        self.assertEquals(inv, [])

        
    def test_ancestors_conditions(self):
        """tests get_ancestors_conditions()"""
        pre, post, inv = get_ancestors_conditions(SillySubclass, 'silly_func')
        self.assertEquals(pre, [['value < 10']])
        self.assertEquals(post, [
            ["type(__return__) == type('') and int(__return__) < 15",
             "__old__.value != __old__.self.invariant"]
            ])
        self.assertEquals(inv, [[], ['self.invariant == 12'], []])


    def test_preconditions_weaken(self):
        """Tests if pre_conditions are weaken
        """
        # If this test passes, then the pre-condition has been weaken
        self.b.silly_func(13)



    def test_postconditions_strengthen(self):
        """Tests if post_conditions are strengthen
        """
        self.a.post_strength()
        # self.assertRaises(ContractFailedError, self.b.post_strength)

    def test_invariant(self):
        """Tests if invariant conditions work
        """
        # self.assert_(self.aspect.inv == [['self.invariant == 12']])
        # This test should pass
        self.a.silly_func(3)
        self.a.invariant = 15
        # This one should not pass since the invariant condition is not
        # true anymore
        self.assertRaises(ContractFailedError, self.a.silly_func, 3)


    def test_invariant_with_several_modules(self):
        """tests invariant list when classes are defined in several modules"""
        class FakeModule:
            """inv:
            a is None
            """
        class AnotherFakeModule:
            """inv:
            b is None
            """
        class BaseClass:
            def foo(self): pass
        class ExtendedClass(BaseClass):
            def foo(self): pass
        BaseClass.__module__ = FakeModule
        ExtendedClass.__module__ = AnotherFakeModule
        # print ".................. ", ExtendedClass.__module__
        pre, post, inv = get_ancestors_conditions(ExtendedClass, 'foo')
        self.assertEquals(inv, [['b is None'], ['a is None'], [], []])


    def test_forall_function(self):
        """tests forall() behaviour"""
        self.assertEquals(forall([]), True)
        self.assertEquals(forall([True, True]), True)
        self.assertEquals(forall([True, False]), False)


    def test_exists_function(self):
        """tests exists() behaviour"""
        self.assertEquals(exists([False, True]), True)
        self.assertEquals(exists([False, False]), False)
        self.assertEquals(exists([]), False)

    def test_forall_contract(self):
        """Tests if forall works well
        """
        self.a.sort([12, 5, 8, 19, 0])


    def test_exception_process(self):
        """Checks if exception are correctly processed
        """
        try:
            self.a.corrupt()
        except ContractFailedError, error:
            self.assert_(error.method_exception is not None)
        else:
            self.fail("No invariant checks after exception raised !")


    def test_func_dict(self):
        """Checks if the wrapped func's global_dict is
        corretcly taken in account.
        """
        weaver.weave_methods(module_test.Sorter,
                             ContractAspect)
        sorter = module_test.Sorter()
        sorter.sort([12, 1, 5])
        self.assertRaises(ContractFailedError, sorter.sort, "bad input")
        

    

def suite():
    """return the unitest suite"""
    loader = unittest.TestLoader()
    testsuite = loader.loadTestsFromModule(sys.modules[__name__])
    return testsuite
    
    
def Run(runner=None):
    """run tests"""
    testsuite = suite()
    if runner is None:
        runner = unittest.TextTestRunner()
    return runner.run(testsuite)
    
if __name__ == '__main__':
    Run()
    
