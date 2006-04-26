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
A very simple confirmation aspect
"""

__revision__ = '$Id: confirmation.py,v 1.9 2005-12-30 16:29:07 adim Exp $'

from logilab.aspects.core import AbstractAspect


class ConfirmationAbstractAspect(AbstractAspect):
    """Confirmation abstract aspect
    """
    def __init__(self, pointcut):
        AbstractAspect.__init__(self, pointcut)
        

    def _do_confirm(self, wobj):
        """This defines how to ask confirmation. It should return
        True if user confirms, else False.
        Abstract method : must be  implemented in subclasses.
        """
        raise NotImplementedError()
    
        
    def around(self, wobj, context, *args, **kwargs):
        """Around implementation of aspect interface
        """
        met_name = context['method_name']
        wclass = context['__class__']
        if self._do_confirm(wobj):
            self._proceed(wobj, wclass, met_name, *args, **kwargs)


