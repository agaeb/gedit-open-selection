# -*- coding: utf-8 -*-
#
# openselection.py
# This file is part of OpenSelectionPlugin, a plugin for gedit
#
# Copyright (C) 2014 Andreas Gaeb <a.gaeb@web.de>
# https://github.com/agaeb/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk, Gedit, Gio
import os.path
import glob

class OpenSelectionAppActivatable(GObject.Object, Gedit.AppActivatable):

    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.menu_ext = self.extend_menu("file-section")
        item = Gio.MenuItem.new( ("Op_en Selection"), "win.OpenSelection")
        self.menu_ext.append_menu_item(item)

        self.app.add_accelerator("<Primary><Shift>O", "win.OpenSelection", None)

    def do_deactivate(self):
        self.menu_ext = None
        self.app.remove_accelerator("win.OpenSelection", None)


class OpenSelectionWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    """Open the currently selected path in a new tab

    Consider the currently selected text to be the name of a (local) file
    which is opened in a new tab by pressing Ctrl-Shift-O or the corresponding
    menu entry. Globs like * are expanded, possibly to multiple files in
    multiple new tabs. Tilde (~) is expanded as well.
    """

    __gtype_name__ = "GeditOpenSelectionPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        action = Gio.SimpleAction(name="OpenSelection")
        action.connect("activate", self.on_open_selection_activate)
        self.window.add_action(action)

    def do_deactivate(self):
        self.window.remove_action("OpenSelection")

    def do_update_state(self):
        pass

    def on_open_selection_activate(self, action, data=None):
        """main function, executed on activation of the menu entry"""
        doc = self.window.get_active_document()
        if doc is None:
            return

        # ensure something is selected
        if not doc.get_has_selection():
            statusbar = self.window.get_statusbar()
            context_id = statusbar.get_context_id(self.__gtype_name__)
            statusbar.push(context_id, "Nothing selected.")
            return

        # extract the selection
        start = doc.get_iter_at_mark(doc.get_selection_bound())
        end = doc.get_iter_at_mark(doc.get_insert())
        selection = doc.get_text(start, end, False)

        # do fancy stuff to turn the selection into a valid filename
        # (or possibly several)
        selection = os.path.expanduser(selection)
        path_iterator = glob.iglob(selection)

        # finally open the file(s) in a new tab
        for path in path_iterator:
            self.window.create_tab_from_location(
                location=Gio.File.new_for_path(path),
                encoding=None,
                line_pos=1,
                column_pos=1,
                create=False,
                jump_to=True)

        # none found? notify user in the statusbar
        else:
            statusbar = self.window.get_statusbar()
            context_id = statusbar.get_context_id(self.__gtype_name__)
            statusbar.push(context_id, "File does not exist: %s" % selection)
            return
