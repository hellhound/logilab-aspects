# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0142,W0613
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
Observer / Observable DP as an aspect.

This module can be useful when using foreign python modules
(that is written by others) and when you don't want its source to
be changed.
"""

__revision__ = '$Id: observer.py,v 1.8 2005-12-30 16:29:09 adim Exp $'


from logilab.aspects.core import AbstractAspect

class ObserverAspect(AbstractAspect):
    """Observer Apsect class
    """

    def __init__(self, pointcut, observers):
        """
        """
        AbstractAspect.__init__(self, pointcut)
        self.observers = observers


    def after(self, wobj, context, *args, **kwargs):
        """After method : notify all observers.
        """        
        for obs in self.observers:
            obs.update()


    
