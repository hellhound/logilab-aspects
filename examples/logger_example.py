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
Sample program that shows how to use the LoggerAspect
"""

__revision__ = '$Id: logger_example.py,v 1.7 2005-12-30 16:29:04 adim Exp $'


class Stack:
    """A very simple stack interface
    (not very useful in Python)
    """

    
    def pop(self):
        """
        --pre:
        # The stack must not be empty
        not self.is_empty()
        --post:
        # The value returned should be the top one
        rv == __old__.self.top()
        # The number of elements should be decremented
        # self.size() == __old__.self.size() - 1
        """
        raise NotImplementedError

    
    def push(self, obj):
        """
        --pre:
        obj is not None
        not self.is_full()
        --post:
        not self.is_empty()
        self.top() == obj
        """
        raise NotImplementedError


    def top(self):
        """Returns the top element of the stack
        """
        raise NotImplementedError

    
    def is_empty(self):
        """Tells whether or not the stack is empty
        """
        raise NotImplementedError


    def is_full(self):
        """Tells whether or not the stack is full
        """
        raise NotImplementedError
    
    def size(self):
        """Returns the current size of the stack
        """
        raise NotImplementedError


class StackImpl(Stack):
    """
    --inv:
    len(self.elements) <= self.max_size
    """

    def __init__(self, max_size = 10):
        """
        --pre:
        max_size > 0
        """
        self.max_size = max_size
        self.elements = []

    def pop(self):
        """Pops the top element, and returns it
        """
        return self.elements.pop()
    

    def push(self, obj):
        """ Pushes obj on the top of the stack
        --post:
        # self.size() == __old__.size() + 1
        """
        self.elements.append(obj)
        

    def top(self):
        """Returns the top element, or None if the stack is emtpy.
        """
        if self.elements:
            return self.elements[-1]
        return None

    def is_empty(self):
        """Tells whether or not the stack is empty
        """
        return len(self.elements) == 0

    def is_full(self):
        """Tells whether or not the stack is full
        """
        return len(self.elements) == self.max_size

    def size(self):
        """Returns the current size of the stack
        """
        return len(self.elements)

    def __str__(self):
        return "elements = %s, max_size = %s"%(self.elements, self.max_size)    


def run():
    """This is an example of how contracts work
    """

    print "*"*30
    # Create a stack which can hold 3 elements
    stack = StackImpl(10)
    from logilab.aspects.weaver import weaver
    from logilab.aspects.lib.logger import LoggerAspect
    import sys
    
    weaver.weave_methods(stack, LoggerAspect, sys.stderr)
    print "Tracing stack's method calls"
    stack.is_empty()
    print "-"*20
    stack.push("un élément")
    print "-"*20
    stack.push("un autre élément")
    print "-"*20
    stack.pop()
    print "*"*30

    print "Unweaving Logger Aspect ..."
    weaver.unweave_methods(stack, LoggerAspect)
    print "Now, calling a stack's method shouldn't be traced"
    stack.push("Un autre élement")
    print "Did it work ?"

    

if __name__ == "__main__":
    run()


