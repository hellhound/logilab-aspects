# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0613,W0232,C0103,R0903,R0801
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

__revision__ = '$Id: unittest_multimethods.py,v 1.7 2005-12-30 16:29:14 adim Exp $'



import unittest
import sys

from logilab.aspects.lib.multimethods import DispatcherAspect, DispatchRule
from logilab.aspects.weaver import weaver

def define_rules():
    """Define shapes' combining rules
    """
    rule_s = DispatchRule("combine_shape",
                          "combine_with_square", [Square])
    rule_t = DispatchRule("combine_shape",
                          "combine_with_triangle", [Triangle])
    return [rule_s, rule_t]


NO_DISPATCH = 0
TRIANGLE_SQUARE = 1
TRIANGLE_TRIANGLE = 2
SQUARE_TRIANGLE = 3
SQUARE_SQUARE = 4


class Shape:
    """Basic interface for shape
    """
    def combine_shape(self, other_shape):
        """The 'KEY' function for this example. This one will be called
        by user without any tests to do to check which other shape will
        be combined to self object.
        """
        return NO_DISPATCH

        

class Square(Shape):
    """Square implementation of Shape interface
    """
    def combine_with_square(self, square):
        """Combine self with square
        """
        # Combine stuff ...
        return SQUARE_SQUARE
    
    def combine_with_triangle(self, triangle):
        """Combine self with triangle
        """
        # Combine stuff ...
        return SQUARE_TRIANGLE



class Triangle(Shape):
    """Triangle implementation of Shape interface
    """
    def combine_with_square(self, square):
        """Combine self with square
        """
        # Combine stuff ...
        return TRIANGLE_SQUARE

    def combine_with_triangle(self, triangle):
        """Combine self with triangle
        """
        # Combine stuff ...
        return TRIANGLE_TRIANGLE


class DispatcherTC(unittest.TestCase):
    """TestCase for dispatch management"""

    def setUp(self):
        """Creates misc. shapes"""
        self.square = Square()
        self.triangle = Triangle()
        weaver.weave_methods(Shape, DispatcherAspect, define_rules())


    def test_dispatch(self):
        """Tests dispatch management"""
        self.assertEquals(self.triangle.combine_shape(self.triangle),
                          TRIANGLE_TRIANGLE)
        self.assertEquals(self.triangle.combine_shape(self.square),
                          TRIANGLE_SQUARE)
        self.assertEquals(self.square.combine_shape(self.triangle),
                          SQUARE_TRIANGLE)
        self.assertEquals(self.square.combine_shape(self.square),
                          SQUARE_SQUARE)


    def test_unweave(self):
        """Tests that unweaving cancels dispatch"""
        weaver.unweave_methods(Shape, DispatcherAspect)        
        self.assertEquals(self.triangle.combine_shape(self.triangle),
                          NO_DISPATCH)
        self.assertEquals(self.triangle.combine_shape(self.square),
                          NO_DISPATCH)
        self.assertEquals(self.square.combine_shape(self.triangle),
                          NO_DISPATCH)
        self.assertEquals(self.square.combine_shape(self.square),
                          NO_DISPATCH)


    def test_rules_match(self):
        """tests DispatchRule.match_func_call()"""
        rule = DispatchRule("combine_shape", "combine_with_square", [Square])
        square = Square()
        triangle = Triangle()
        self.assertEquals(rule.match_func_call([]), False)
        self.assertEquals(rule.match_func_call([square, triangle]), False)
        self.assertEquals(rule.match_func_call([triangle]), False)
        self.assertEquals(rule.match_func_call([square]), True)


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
