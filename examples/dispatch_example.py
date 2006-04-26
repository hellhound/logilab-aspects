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
Example to show how DispatcherAspect (multimethods) works.

The shape example has been taken from the following article :
http://www.onlamp.com/pub/a/python/2003/05/29/multimethods.html
"""

__revision__ = '$id$'

# XXX ??? Is it useful ???
# Maybe use it with the Visitor DP ...

class Shape:
    """Basic interface for shape
    """

    def area(self):
        """returns the object's area
        """
        pass

    def combine_shape(self, other_shape):
        """The 'KEY' function for this example. This one will be called
        by user without any tests to do to check which other shape will
        be combined to self object.
        """
        print "I'm a %s and I don't want to check anything !" % \
              (self.__class__.__name__)

        

class Square(Shape):
    """Square implementation of Shape interface
    """

    def __init__(self, size):
        """
        """
        self.size = size
        
    def area(self):
        """returns the area of this square
        """
        return self.size**2

    def combine_with_square(self, square):
        """Combine self with square
        """
        # Combine stuff ...
        print "Combining a %s with a Square" % (self.__class__.__name__)

    def combine_with_circle(self, circle):
        """Combine self with circle
        """
        # Combine stuff ...
        print "Combining a %s with a Circle" % (self.__class__.__name__)
        
    
    def combine_with_triangle(self, triangle):
        """Combine self with triangle
        """
        # Combine stuff ...
        print "Combining a %s with a Triangle" % (self.__class__.__name__)



class Triangle(Shape):
    """Triangle implementation of Shape interface
    """

    def __init__(self, base_size, highness):
        """
        """
        self.base_size = base_size
        self.highness = highness

    def area(self):
        """returns the area of this triangle
        """
        return (self.base_size*self.highness) / 2.


    def combine_with_square(self, square):
        """Combine self with square
        """
        # Combine stuff ...
        print "Combining a %s with a Square" % (self.__class__.__name__)

    def combine_with_circle(self, circle):
        """Combine self with circle
        """
        # Combine stuff ...
        print "Combining a %s with a Circle" % (self.__class__.__name__)
        
    
    def combine_with_triangle(self, triangle):
        """Combine self with triangle
        """
        # Combine stuff ...
        print "Combining a %s with a Triangle" % (self.__class__.__name__)


class Circle(Shape):
    """Circle implementation of Shape interface
    """

    def __init__(self, radius):
        """
        """
        self.radius = radius
        

    def area(self):
        """returns the area of this cirlce
        """
        return 3.14159 * self.radius * self.radius

    def combine_with_square(self, square):
        """Combine self with square
        """
        # Combine stuff ...
        print "Combining a %s with a Square" % (self.__class__.__name__)

    def combine_with_circle(self, circle):
        """Combine self with circle
        """
        # Combine stuff ...
        print "Combining a %s with a Circle" % (self.__class__.__name__)
        
    
    def combine_with_triangle(self, triangle):
        """Combine self with triangle
        """
        # Combine stuff ...
        print "Combining a %s with a Triangle" % (self.__class__.__name__)



# Main Stuff ###################################################################

from logilab.aspects.lib.multimethods import DispatcherAspect, DispatchRule
from logilab.aspects.weaver import weaver


def define_rules():
    """Define shapes' combining rules
    """
    
    rule_s = DispatchRule("combine_shape",
                          "combine_with_square", [Square])
    
    rule_t = DispatchRule("combine_shape",
                          "combine_with_triangle", [Triangle])

    rule_c = DispatchRule("combine_shape",
                          "combine_with_circle", [Circle])
    
    
    return [rule_c, rule_s, rule_t]
    

def run():
    """Example
    """

    rules = define_rules()
    circle = Circle(12)
    square = Square(12)
    triangle = Triangle(10, 15)

    print "*"*30
    print "Trying to combine a square in a triangle : "
    triangle.combine_shape(square)

    print "Now, weave multimethods aspect, this should make a difference !"
    weaver.weave_methods(Shape, DispatcherAspect, rules)

    # Combining Triangle
    print "COMBINING Triangle with all types of shapes"
    triangle.combine_shape(square)
    triangle.combine_shape(circle)
    triangle.combine_shape(triangle)

    # Combining Circle
    print "COMBINING Circles with all types of shapes"
    circle.combine_shape(square)
    circle.combine_shape(circle)
    circle.combine_shape(triangle)

    # Combining Square
    print "COMBINING Square with all types of shapes"
    square.combine_shape(square)
    square.combine_shape(circle)
    square.combine_shape(triangle)

    print "*" * 30
    
    

if __name__ == '__main__':
    run()
