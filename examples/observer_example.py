# -*- coding: iso-8859-1 -*-
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
Observer Aspect example
"""


__revision__ = '$Id: observer_example.py,v 1.6 2005-12-30 16:29:05 adim Exp $'


from logilab.aspects.lib.observer import ObserverAspect
from logilab.aspects.weaver import weaver, PointCut

class ForeignClass:
    """Consider that this class is written by someone else, and
    that you don't want it to be modified.
    But you may still want to make it observable !
    """

    def __init__(self, value):
        """
        """
        self.value = value


    def set_value(self, val):
        """sets self.value to val.
        This method should notify observers that self has changed. But
        you do not want to change this code, and you don't want to
        subclass ForeignClass.
        """
        self.value = val



class MyObserver:
    """An observer of ForeignClass ...
    """

    def update(self):
        """Called when a ForeignClass instance is changed
        """
        print "-"*10,"I'm an Observer : ForeignClass has changed !","-"*10


def run():
    """Observer example
    """
    
    foreign = ForeignClass(10)
    obs = MyObserver()

    print "*"*30
    print "Before weaving ObserverAspect, changes on foo won't be observerd"
    print ""
    print "Changing foo ..."
    foreign.set_value(11)
    print "Did the observer see anything ?"
    print ""
    print "Now : weave observer aspect, and re-change foo ..."
    pcut = PointCut()
    pcut.add_method(foreign, 'set_value')
    weaver.weave_pointcut(pcut, ObserverAspect, [obs])
    foreign.set_value(12)
    print "Did the observer see anything ?"
    
    print "*"*30
    

if __name__ == '__main__':
    run()
        
