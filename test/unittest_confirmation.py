# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0232,C0103,R0801
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
Unit tests for confirmation aspect
"""

__revision__ = '$Id: unittest_confirmation.py,v 1.7 2005-12-30 16:29:12 adim Exp $'

import unittest
import sys

from logilab.aspects.lib.confirmation import ConfirmationAbstractAspect
from logilab.aspects.weaver import weaver, PointCut


class ConfirmationConcreteAspect(ConfirmationAbstractAspect):
    """A simple concrete confirmation aspect
    """
    def _do_confirm(self, wobj):
        """Confirms if wobj.confident is set to True"""
        return wobj.confident

    
class BaseJumper:
    """Simple class for tests"""
    def __init__(self):
        self.confident = True
        self.status = 'wondering'

    def set_paranoid(self):
        """Sets confident to False"""
        self.confident = False

    def set_confident(self):
        """Sets confident to True"""
        self.confident = True

    def jump(self):
        """We should ask confirmation before doing jump"""
        self.status = 'jumped'
        

class ConfirmTC(unittest.TestCase):
    """Test Case for confirmation aspect"""

    def setUp(self):
        """Create a BaseJumper instance and weave ConfirmationAspect around
        jump()
        """
        self.guy = BaseJumper()
        pcut = PointCut()
        pcut.add_method(self.guy, "jump")
        weaver.weave_pointcut(pcut, ConfirmationConcreteAspect)
        self.pcut = pcut

    
    def test_confirmation(self):
        """Tests confirmation"""
        self.guy.set_paranoid()
        self.guy.jump()
        self.assertEquals(self.guy.status, 'wondering',
                          "The guy jumped without confirmation !")
        self.guy.set_confident()
        self.guy.jump()
        self.assertEquals(self.guy.status, 'jumped',
                          "The guy should have jumped")


    def test_unweave(self):
        """Tests that unweaving() cancels confirmation"""
        weaver.unweave_pointcut(self.pcut, ConfirmationConcreteAspect)
        self.guy.set_paranoid()
        self.guy.jump()
        self.assertEquals(self.guy.status, 'jumped',
                          "The guy should have jumped")


    def test_aspect_is_abstract(self):
        """ensures that using ConfirmationAbstractAspect raises an exception"""
        jumper = BaseJumper()
        weaver.weave_object(jumper, ConfirmationAbstractAspect)
        self.assertRaises(NotImplementedError, jumper.jump)
    

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
