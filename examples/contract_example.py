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
Sample program that shows how to use Contracts
"""

__revision__ = '$Id: contract_example.py,v 1.9 2005-12-30 16:29:04 adim Exp $'


class Stack:
    """A very simple stack interface
    (not very useful in Python)
    """

    
    def pop(self):
        """
        pre:
            # The stack must not be empty
            not self.is_empty()
        post:
            # The value returned should be the top one
            __return__ == __old__.self.top()
            # The number of elements should be decremented
            self.size() == __old__.self.size() - 1
        """
        raise NotImplementedError

    
    def push(self, obj):
        """
        pre:
            obj is not None
            not self.is_full()
        post:
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
    inv:
        self.size() <= self.max_size
    """

    def __init__(self, max_size = 10):
        """
        pre:
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
        post:
            self.size() == __old__.self.size() + 1
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
        return "elements = %s, max_size = %s" % (self.elements, self.max_size)


def run():
    """This is an example of how contracts work
    """
    print "*"*30
    print "Creating an empty stack (max_size = 3)"
    # Create a stack which can hold 3 elements
    stack = StackImpl(3)

    from logilab.aspects.weaver import weaver
    from logilab.aspects.lib.contracts import ContractAspect, \
         ContractFailedError

    weaver.weave_methods(stack, ContractAspect)

    try:
        print "Empty stack, pop() should fail"
        stack.pop()
    except ContractFailedError, excpt:
        print "\t failed with %s, (OK)" % excpt
    else:
        print "\t did not failed, (XXX)"

    print "\n\n\n"
    stack.push(1)
    print "push 1 done"
    stack.push(2)
    print "push 2 done"
    stack.push(3)
    print "push 3 done"
        
    try:
        print "The stack is full, push() should fail"
        stack.push(4)
    except ContractFailedError, excpt:
        print "\t failed with %s, (OK)" % excpt
    else:
        print "\t did not failed, (XXX)"

    print "\n\n\n"

    try:
        print "Pushing on the full stack (using directly stack.elements)"
        stack.elements.append(4)
        print "Class invariant is no more true, any method call should fail"
        print stack.is_full()
    except ContractFailedError, excpt:
        print "\t failed with %s, (OK)" % excpt
    else:
        print "\t did not failed, (XXX)"
    print "*"*30
    

if __name__ == '__main__':
    run()
