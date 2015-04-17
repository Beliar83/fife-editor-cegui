# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains an editor for editing lists

.. module:: list_editor
    :synopsis: Editor for editing lists

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from copy import copy

import PyCEGUI

from .dialog import Dialog


class ListEditor(Dialog):

    """Editor for editing lists"""

    def __init__(self, app, _list=None):
        Dialog.__init__(self, app)
        self.list = _list or []
        self.edit_list = None
        self.text_input = None
        self.add_button = None
        self.delete_button = None
        self.items = []
        self.values = []

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        font = root.getFont()
        text_height = font.getFontHeight() + 2
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.5, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.5, 4)))
        self.window.setText(_("Edit List"))

        list_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0), PyCEGUI.UDim(0.8, 0))
        edit_list = root.createChild("TaharezLook/ItemListbox",
                                     "EditList")
        edit_list.setSize(list_size)
        edit_list.subscribeEvent(PyCEGUI.ItemListbox.EventSelectionChanged,
                                 self.cb_edit_list_changed)
        edit_list.resetList()
        self.items = []
        self.values = []
        for value in self.list:
            item = edit_list.createChild("TaharezLook/ListboxItem")
            item.setText(value)
            self.items.append(item)
            self.values.append(value)
        edit_list.performChildWindowLayout()
        self.edit_list = edit_list
        text_input = root.createChild("TaharezLook/Editbox", "text_input")
        text_input.setHeight(PyCEGUI.UDim(0.0, text_height))
        text_input.setWidth(PyCEGUI.UDim(1.0, 0))
        text_input.subscribeEvent(PyCEGUI.Editbox.EventTextChanged,
                                  self.cb_text_changed)
        self.text_input = text_input

        buttons_layout = root.createChild("HorizontalLayoutContainer",
                                          "buttons_layout")
        buttons_layout.setHorizontalAlignment(PyCEGUI.HA_CENTRE)
        add_button = buttons_layout.createChild("TaharezLook/Button",
                                                "add_button")
        add_button.setText("Add")
        add_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        add_button.setEnabled(False)
        add_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_add_clicked)
        self.add_button = add_button
        delete_button = buttons_layout.createChild("TaharezLook/Button",
                                                   "delete_button")
        delete_button.setText("Delete")
        delete_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        delete_button.setEnabled(False)
        delete_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                     self.cb_delete_clicked)
        self.delete_button = delete_button

    def cb_edit_list_changed(self, args):
        """Called when something in the list was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        self.delete_button.setEnabled(args.window.getSelectedCount() > 0)

    def cb_text_changed(self, args):
        """Called when the editbox was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        self.add_button.setEnabled(len(args.window.getText()) > 0)

    def cb_add_clicked(self, args):
        """Called when the add button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        value = self.text_input.getText()
        item = self.edit_list.createChild("TaharezLook/ListboxItem")
        item.setText(value)
        self.edit_list.performChildWindowLayout()
        self.items.append(item)
        self.values.append(value)

    def cb_delete_clicked(self, args):
        """Called when the delete button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        item = self.edit_list.getFirstSelectedItem()
        self.values.remove(item.getText())
        self.edit_list.removeItem(item)

    def get_values(self):
        return {"items": copy(self.values)}

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        return True
