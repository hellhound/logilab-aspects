# -*- coding: ISO-8859-1 -*-
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
Simple example for using ConfirmationAspect.

This example needs GTK2.2, glade-2, and pygtk1.99.15 to run
"""

__revision__ = '$Id: confirm_example.py,v 1.8 2005-12-30 16:29:04 adim Exp $'


import gtk, gtk.glade

from logilab.aspects.lib.confirmation import ConfirmationAbstractAspect
from logilab.aspects.weaver import weaver


class ConfirmationGTK2Aspect(ConfirmationAbstractAspect):
    """Confirmation Aspect implemented for GTK2
    """

    def __init__(self, pointcut, widget = None):
        ConfirmationAbstractAspect.__init__(self, pointcut)
        self.widget = widget

    def _do_confirm(self, wobj):
        """Asks for confirmation. Returns True if confirms, else, False.
        """
        dlg = gtk.MessageDialog(self.widget,
                                gtk.MESSAGE_QUESTION,
                                buttons = gtk.BUTTONS_YES_NO)
        dlg.label.set_text("Are you sure ?")
        dlg.set_default_response(gtk.RESPONSE_NO)
        ret = dlg.run()
        dlg.destroy()
        if ret == gtk.RESPONSE_NO:
            return False
        return True




class AppWindow:
    """Application window class
    """

    def __init__(self, glade_file):
        """
        glade_file : the glade XML file
        """
        self.widgets = gtk.glade.XML(glade_file)
        self.main_window = self.widgets.get_widget('main_window')

    def connect_signals(self):
        """connect handlers
        """
        handlers = {'on_new_activate' : self.new_cb,
                    'on_quit_activate' : self.quit_cb,
                    'on_quit_clicked' : self.quit_cb}
        self.widgets.signal_autoconnect(handlers)


    def new_cb(self, *args):
        """New callback
        """
        print "New ..."


    def quit_cb(self, *args):
        """Quit callback
        """
        print "Quitting ..."
        gtk.mainquit()


    def show(self):
        """shows the window
        """
        self.main_window.show()



def run():
    """main func
    """
    
    print "This window will ask confirmation before quitting, and " \
            "creating an new document."
    
    win = AppWindow('simple_window.glade')
    weaver.weave_methods(win, ConfirmationGTK2Aspect, win.main_window)
    weaver._unweave_method(win,'show',ConfirmationGTK2Aspect)
    weaver._unweave_method(win,'connect_signals',ConfirmationGTK2Aspect)
    win.show()
    win.connect_signals()
    gtk.main()


if __name__ == '__main__':
    run()

