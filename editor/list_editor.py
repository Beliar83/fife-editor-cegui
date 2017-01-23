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
from future import standard_library
standard_library.install_aliases()
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
        self.up_button = None
        self.down_button = None
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

        up_button = buttons_layout.createChild("TaharezLook/Button",
                                               "up_button")
        up_button.setText("Up")
        up_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        up_button.setEnabled(False)
        up_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                 self.cb_up_clicked)
        self.up_button = up_button

        down_button = buttons_layout.createChild("TaharezLook/Button",
                                                 "down_button")
        down_button.setText("Down")
        down_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        down_button.setEnabled(False)
        down_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                   self.cb_down_clicked)
        self.down_button = down_button

    def cb_edit_list_changed(self, args):
        """Called when something in the list was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        has_selected = args.window.getSelectedCount() > 0
        self.delete_button.setEnabled(has_selected)
        item_count = args.window.getItemCount()
        if not has_selected:
            self.up_button.setEnabled(has_selected)
            self.down_button.setEnabled(has_selected)
        elif item_count < 2:
            self.up_button.setEnabled(False)
            self.down_button.setEnabled(False)
        else:
            item = args.window.getFirstSelectedItem()
            index = args.window.getItemIndex(item)
            self.up_button.setEnabled(index > 0)
            self.down_button.setEnabled(index < item_count - 1)

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
        index = self.edit_list.getItemIndex(item)
        del self.values[index]
        self.edit_list.removeItem(item)

    def cb_up_clicked(self, args):
        """Called when the up button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        item = self.edit_list.getFirstSelectedItem()
        old_index = self.edit_list.getItemIndex(item)
        new_index = old_index - 1
        self.values.insert(new_index, self.values.pop(old_index))
        temp_item = self.edit_list.getItemFromIndex(new_index)
        item.setDestroyedByParent(False)
        self.edit_list.removeItem(item)
        self.edit_list.insertItem(item, temp_item)
        item.setDestroyedByParent(True)
        self.edit_list.performChildWindowLayout()
        self.edit_list.selectRange(new_index, new_index)

    def cb_down_clicked(self, args):
        """Called when the down button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        item = self.edit_list.getFirstSelectedItem()
        old_index = self.edit_list.getItemIndex(item)
        new_index = old_index + 1
        self.values.insert(new_index, self.values.pop(old_index))
        item.setDestroyedByParent(False)
        self.edit_list.removeItem(item)
        if new_index >= self.edit_list.getItemCount():
            self.edit_list.addItem(item)
        else:
            temp_item = self.edit_list.getItemFromIndex(new_index)
            self.edit_list.insertItem(item, temp_item)
        self.edit_list.selectRange(new_index, new_index)

        item.setDestroyedByParent(True)
        self.edit_list.performChildWindowLayout()

    def get_values(self):
        return {"items": copy(self.values)}

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        return True
