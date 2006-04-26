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
A small example to illustrate how profiler aspect works
"""

__revision__ = '$Id: profiler_example.py,v 1.6 2005-12-30 16:29:05 adim Exp $'

from logilab.aspects.lib.profiler import ProfilerAspect
from logilab.aspects.weaver import weaver

class MyClass:
    """A class to illustrate ProfilerAspect
    """

    def write_one_char(self, char):
        """Writes one char
        """
        res = ""
        res += char
        return res

    def write_two_chars(self, char):
        """Writes two times 'char'
        """
        res = ""
        res += char
        res += char
        return res


    def write_thousands_chars(self, char):
        """Writes a 100000 times 'char'
        """
        res = ""
        for index in range(100000):
            res += char
        return res


    def write_thousands_cstringio(self, char):
        """Writes a 100000 times 'char' in a cStringIO
        """
        from cStringIO import StringIO
        res = StringIO()
        for index in range(100000):
            res.write(char)

        return res


    def write_thousands_stringio(self, char):
        """Writes a 100000 times 'char' in a cStringIO
        """
        from StringIO import StringIO
        res = StringIO()
        for index in range(100000):
            res.write(char)

        return res


    def write_thousands_join(self, char):
        """Writes a 100000 times 'char' in a list and joins it
        """
        str_list = []
        for index in range(100000):
            str_list.append(char)

        return ''.join(str_list)

    


def run():
    """Run example
    """
    writer = MyClass()
    weaver.weave_methods(MyClass, ProfilerAspect)
    print "Warning : this can take a while ...., be patient"
    writer.write_one_char('a')
    writer.write_two_chars('a')
    writer.write_thousands_chars('a')
    writer.write_thousands_stringio('a')
    writer.write_thousands_cstringio('a')
    writer.write_thousands_join('a')
    writer.write_one_char('a')

    import sys
    aspect_instance = weaver.get_aspect(ProfilerAspect)
    aspect_instance.dump_readable_profiles(sys.stdout)

    

if __name__ == '__main__':
    run()
