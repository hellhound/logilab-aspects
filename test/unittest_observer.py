# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=C0103,W0232,R0903,R0801
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

__revision__ = '$Id: unittest_observer.py,v 1.5 2005-12-30 16:29:15 adim Exp $'

import unittest
import sys

from logilab.aspects.lib.observer import ObserverAspect
from logilab.aspects.weaver import weaver, PointCut


class SillyClass:
    """Simple test class"""
    def do_something(self):
        """This method should be 'observed'"""
        pass


class MyObserver:
    """An observer of ForeignClass ...
    """
    def __init__(self):
        self.update_calls = 0
    
    def update(self):
        """Called when a SillyClas instance 'does_something'"""
        self.update_calls += 1
    

class ObserverTC(unittest.TestCase):
    """Test Case for Observer aspect"""

    def setUp(self):
        """Initalizes observer / observable objects"""
        self.obj = SillyClass()
        pcut  = PointCut()
        pcut.add_method(self.obj, 'do_something')
        self.obs = MyObserver()
        weaver.weave_pointcut(pcut, ObserverAspect, [self.obs])
        self.pcut = pcut


    def test_observer(self):
        """Tests that objects are observed"""
        self.assertEquals(self.obs.update_calls, 0)
        self.obj.do_something()
        self.assertEquals(self.obs.update_calls, 1)
        self.obj.do_something()
        self.assertEquals(self.obs.update_calls, 2)
        

    def test_unweave(self):
        """Tests that unweaving() cancels observation"""
        weaver.unweave_pointcut(self.pcut, ObserverAspect)
        self.assertEquals(self.obs.update_calls, 0)
        self.obj.do_something()
        self.assertEquals(self.obs.update_calls, 0)




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
