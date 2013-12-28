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
Aspect Implementation of Logger
"""

__revision__ = '$Id: logger.py,v 1.17 2005-12-30 16:29:08 adim Exp $'


import time

from logilab.aspects.core import AbstractAspect
from logilab.aspects.prototypes import reassign_function_arguments


class LoggerAspect(AbstractAspect):
    """Logger Aspect Class.
    The Logger will log all informations related to method calls
    """
    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, pointcut, log_device):
        """
        cls : the class or class instance to aspect
        method_name : the name of the method to wrap
        log_device : the stream to write log messages in
        """
        AbstractAspect.__init__(self, pointcut)
        self.log_device = log_device

    def _log_date_time_string(self):
        """Return the current time formatted for logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
                day, self.monthname[month], year, hh, mm, ss)
        return s
        
    def before(self, wobj, context, *args, **kwargs):
        """Before method
        """
        met_name = context['method_name']
        classname = context['__class__'].__name__
        property_func = context['property_func']
        method = self._get_base_method(wobj, met_name, property_func)
        self.log_device.write("[%s] Calling %s (%s) \n" % (
            self._log_date_time_string(), met_name, classname))
        self.log_device.write(
            "[%s]\twith values : \n" % self._log_date_time_string())
        call_dict = reassign_function_arguments(method, args, kwargs)
        for var, val in call_dict.items():
            self.log_device.write('[%s]\t\t "%s" = %r\n' % (
                self._log_date_time_string(), repr(var), val))

    def after(self, wobj, context, *args, **kwargs):
        """After method.
        Logs the return value
        """
        met_name = context['method_name']
        classname = context['__class__'].__name__
        exec_excpt = context['exception']
        ret_v = context['ret_v']
        
        if exec_excpt is not None:
            self.log_device.write(
                "[%s] End of %s (%s). Exception was raised : %s" %
                (self._log_date_time_string(), met_name, classname, exec_excpt))
        else:
            self.log_device.write(
                "[%s] End of %s (%s). Return Value is : %r\n"% \
                (self._log_date_time_string(), met_name, classname, ret_v))
