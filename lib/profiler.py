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
Aspect Implementation of Logger
"""

__revision__ = '$Id: profiler.py,v 1.11 2005-12-30 16:29:10 adim Exp $'


from logilab.aspects.core import AbstractAspect
from logilab.aspects.weaver import weaver

import time

class ProfilerAspect(AbstractAspect):
    """Logger Aspect Class.
    The Logger will log all informations related to method calls
    """

    
    def __init__(self, pointcut):
        """
        """
        self.__profile_dict = {}
        AbstractAspect.__init__(self, pointcut)

                

    def _update_methods(self, pointcut):
        """Override AbstractAspect's update_methods because we also need
        to update our profile stats. (We might fix this with
        an appropriate hook)
        """
        for weaved_object, method_names in pointcut.items():
            method_map = self._methods.get(weaved_object, {})
            if weaved_object not in self.__profile_dict:
                self.__profile_dict[weaved_object] = {}

            for met_name in method_names:
                base_method, method = weaver.get_original_method(weaved_object,
                                                                 met_name)
                method_map[met_name] = (method, base_method)
                if met_name not in self.__profile_dict[weaved_object]:
                    self.__profile_dict[weaved_object][met_name] = []
                
            self._methods[weaved_object] = method_map
    
    
    def around(self, wobj, context, *args, **kwargs):
        """Around implementation for Profiler
        """        
        met_name = context['method_name']
        wclass = context['__class__']
        start_time = time.time()
        try:
            return self._proceed(wobj, wclass, met_name, *args, **kwargs)
        finally:
            end_time = time.time()
            self._add_profile_entry(wobj, met_name,
                                    start_time, end_time-start_time)
        
            
##     def _get_profile_entry(self):
##         """Returns the correct entry in the profile dictionnary
##         """
##         return self.__profile_dict[self.weaved_obj][self.method_name]

    
    def _add_profile_entry(self, wobj, met_name,
                           call_time, exec_time):
        """Add an entry to the profile dictionnary
        wobj : the weaved object
        met_name : the profiled method's name
        call_time : the time when method was called
        exec_time : the execution time of the method
        """
        entry = self.__profile_dict[wobj.__class__][met_name]
        entry.append((call_time, exec_time))
        

    def dump_profiles_html(self, stream):
        """Static Method to dump results in a readable way
        """
        stream.write('<h3>Results</h3>\n<ul>')
        for cls in self.__profile_dict:
            stream.write('<li>%r\n<ul>\n'%cls)
            for met_name in self.__profile_dict[cls]:
                entries = self.__profile_dict[cls][met_name]
                stream.write('<li>%s (called %d times):\n<ul>\n'% \
                             (met_name, len(entries)))
                for entry in entries:
                    stream.write(
                        '<li> - Called at %s, exec_time = %s sec</li>\n' % \
                        (time.ctime(entry[0]),entry[1]))
                stream.write('</ul>\n')
        stream.write('</ul>\n')


    def dump_readable_profiles(self, stream):
        """Static Method to dump results in a readable way
        """
        stream.write("*"*15+"  Results  "+"*"*15+'\n')
        for cls in self.__profile_dict:
            stream.write('In %r :\n'%cls)
            for met_name in self.__profile_dict[cls]:
                entries = self.__profile_dict[cls][met_name]
                stream.write('\t %s (called %d times):\n'% \
                             (met_name, len(entries)))
                for entry in entries:
                    stream.write('\t\t - Called at %s, exec_time = %s sec\n' % \
                                 (time.ctime(entry[0]),entry[1]))
                stream.write('\t\n')
                
        stream.write("*"*41+'\n')


