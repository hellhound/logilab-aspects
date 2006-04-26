# -*- coding: ISO-8859-1 -*-
# Copyright (c) 2004-2006 Sylvain Thénault
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
"""pytrace [options] <python program> [program options / arguments]

plug a logger aspect on some modules/classes before running the program
"""

__revision__ = '$Id: pytrace.py,v 1.2 2005-12-30 16:29:05 adim Exp $'
version = ('0.1.0')

import os
import sys
import time
import threading

from logilab.common.configuration import OptionsManagerMixIn, \
     OptionsProviderMixIn
from logilab.common.modutils import load_module_from_name

from logilab.aspects.weaver import weaver
from logilab.aspects.core import AbstractAspect
from logilab.aspects.prototypes import reassign_function_arguments


class LoggerAspect(AbstractAspect):
    """Logger Aspect Class.
    The Logger will log all informations related to method calls
    """
    name = 'logging'
    priority = 0
    
    def filter(name):
        """log everything"""
        return 1
    
    filter = staticmethod(filter)
    
    def __init__(self, pointcut, output, config):
        """
        cls : the class or class instance to aspect
        method_name : the name of the method to wrap
        output : the stream to write log messages in
        """
        AbstractAspect.__init__(self, pointcut)
        self.config = config
        self.output = output
        
        
    def before(self, wobj, context, *args, **kwargs):
        """Before method"""
        self.base_info(wobj, context)
        write = self.output.write
        if self.config.parameters:
            write("(")
            method = self._get_base_method(wobj, context['method_name'])
            call_dict = reassign_function_arguments(method, args, kwargs)
            write(', '.join(['%s=%r' % (var, val)
                             for var, val in call_dict.items()]))
            write(")")
        write('\n')
                
    def after(self, wobj, context, *args, **kwargs):
        """After method.
        Logs the return value or the exception raised
        """
        self.base_info(wobj, context)
        exec_excpt = context['exception']
        if exec_excpt is not None:
            try:
                self.output.write(" exception : %s\n" % (exec_excpt,))
            except:
                self.output.write(" exception : %s\n" % (exec_excpt.__class__,))
        else:
            self.output.write(" return : %r\n" % (context['ret_v'],))

    def base_info(self, wobj, context):
        """print base information according to context and configuration"""
        write = self.output.write
        if self.config.time:
            write('[%s] ' % time.strftime('%X', time.localtime()))
        if self.config.threads:
            write('[%s] ' % threading.currentThread().getName())
        if self.config.oid:
            write("<%s at 0x%x>." % (wobj.__class__.__name__, id(wobj)))
        else:
            write("%s." % wobj.__class__.__name__)
        write(context['method_name'])


class Runner(OptionsProviderMixIn, OptionsManagerMixIn):
    """command line runner"""
    
    name = "selection"
    priority = 0
    def __init__(self, args):
        self.options = (("class",
                {'type' : "string", 'metavar' : "<class name>",
                 'action' : "callback", 'callback': self.cb_plug_class,
                 'help' : """Plug the logger on the given class."""}),
               ("module",
                {'type':'string', 'metavar' : "<module name>",
                 'action' : "callback", 'callback': self.cb_plug_module,
                 'help' : """Plug the logger on the given module."""}),
                        
                        ("threads",
                         {'default' :0, 'type' : "yn", 'metavar' : "<y_or_n>",
                          'help' : """Log thread information."""}),
                        ("time",
                         {'default': 0, 'type' : 'yn', 'metavar' : '<y_or_n>',
                          'help' : 'Log time information.'}),               
                        ("oid",
                         {'default' :1, 'type' : "yn", 'metavar' : "<y_or_n>",
                          'help' : """Log object ids."""}),
               ("parameters",
                {'default': 1, 'type' : 'yn', 'metavar' : '<y_or_n>',
                 'help' : 'Log arguments\'values.'}),               
                        )
               
        OptionsProviderMixIn.__init__(self)
        OptionsManagerMixIn.__init__(self, usage=__doc__,
                                     version=version,
                                     config_file='.pytracerc')
        self.register_options_provider(self)
        #self._weaved = {}
        # insert current working directory to the python path to have a correct
        # behaviour
        sys.path.insert(0, os.getcwd())
        # load configuration
        self.load_file_configuration()
        args = self.load_command_line_configuration(args)
        if not args:
            print self.help()            
        sys.argv = args        
        execfile(args[0], globals())
    
    def cb_plug_module(self, option, opt_name, value, parser):
        """optik callback to plug the aspect on a module"""
        module = load_module_from_name(value)
        #self._weaved[value] = module
        weaver.weave_module(module, LoggerAspect, sys.stderr, self.config)
        
    def cb_plug_class(self, option, opt_name, value, parser):
        """optik callback to plug the aspect on a class"""
        parts = value.split('.')
        modulename, klassname = '.'.join(parts[:-1]), parts[-1]
        module = load_module_from_name(modulename)
        klass = getattr(module, klassname)
        #self._weaved[modulename] = module
        weaver.weave_methods(klass, LoggerAspect, sys.stderr, self.config)

def run():
    Runner(sys.argv[1:])
        
if __name__ == '__main__':
    run()

