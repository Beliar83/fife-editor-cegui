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

"""Contains an editor for editing dicts

.. module:: dict_editor
    :synopsis: Editor for editing dicts

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import absolute_import
import PyCEGUI

from .dialog import Dialog
import six


class DictEditor(Dialog):

    """Editor for editing dicts"""

    def __init__(self, app, _dict=None):
        Dialog.__init__(self, app)
        self.dict = _dict or {}
        self.edit_dict = None
        self.key_input = None
        self.value_input = None
        self.add_button = None
        self.delete_button = None
        self.items = []
        self.values = {}

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
        self.window.setText(_("Edit Dict"))

        dict_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0), PyCEGUI.UDim(0.8, 0))
        edit_dict = root.createChild("TaharezLook/MultiColumnList",
                                     "EditDict")
        edit_dict.setSize(dict_size)
        edit_dict.subscribeEvent(PyCEGUI.MultiColumnList.EventSelectionChanged,
                                 self.cb_edit_dict_changed)
        edit_dict.resetList()
        edit_dict.addColumn("Key", 0, PyCEGUI.UDim(0.4, 0))
        edit_dict.addColumn("Value", 1, PyCEGUI.UDim(0.4, 0))
        edit_dict.setSelectionMode(PyCEGUI.MultiColumnList.
                                   SelectionMode.RowSingle)
        self.items = []
        self.values = {}
        for key, value in six.iteritems(self.dict):
            row = edit_dict.addRow()
            item = PyCEGUI.ListboxTextItem(str(key))
            item.setSelectionBrushImage("TaharezLook/"
                                        "MultiListSelectionBrush")
            edit_dict.setItem(item, 0, row)
            self.items.append(item)
            item = PyCEGUI.ListboxTextItem(str(value))
            item.setSelectionBrushImage("TaharezLook/"
                                        "MultiListSelectionBrush")
            edit_dict.setItem(item, 1, row)
            self.items.append(item)
            self.values[key] = value
        edit_dict.performChildWindowLayout()
        self.edit_dict = edit_dict
        input_layout = root.createChild("HorizontalLayoutContainer",
                                        "input_layout")
        key_layout = input_layout.createChild("HorizontalLayoutContainer",
                                              "key_layout")
        key_layout.setWidth(PyCEGUI.UDim(0.5, 0))
        key_label = key_layout.createChild("TaharezLook/Label",
                                           "key_label")
        key_label.setProperty("HorzFormatting", "LeftAligned")
        key_label.setText(_("Key"))
        text_width = font.getTextExtent(key_label.getText())
        key_label.setHeight(PyCEGUI.UDim(0.0, text_height))
        key_label.setWidth(PyCEGUI.UDim(0.0, text_width))
        key_input = key_layout.createChild("TaharezLook/Editbox",
                                           "key_input")
        key_input.setHeight(PyCEGUI.UDim(0.0, text_height))
        key_input.setWidth(PyCEGUI.UDim(0.5, -text_width))
        key_input.subscribeEvent(PyCEGUI.Editbox.EventTextChanged,
                                 self.cb_text_changed)
        self.key_input = key_input
        value_layout = input_layout.createChild("HorizontalLayoutContainer",
                                                "value_layout")
        value_layout.setWidth(PyCEGUI.UDim(0.5, 0))
        value_label = value_layout.createChild("TaharezLook/Label",
                                               "value_label")
        value_label.setProperty("HorzFormatting", "LeftAligned")
        value_label.setText(_("Value"))
        text_width = font.getTextExtent(value_label.getText())
        value_label.setHeight(PyCEGUI.UDim(0.0, text_height))
        value_label.setWidth(PyCEGUI.UDim(0.0, text_width))

        value_input = value_layout.createChild("TaharezLook/Editbox",
                                               "value_input")
        value_input.setHeight(PyCEGUI.UDim(0.0, text_height))
        value_input.setWidth(PyCEGUI.UDim(0.5, -text_width))
        value_input.subscribeEvent(PyCEGUI.Editbox.EventTextChanged,
                                   self.cb_text_changed)
        self.value_input = value_input

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

    def cb_edit_dict_changed(self, args):
        """Called when something in the dict was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        self.delete_button.setEnabled(args.window.getSelectedCount() > 0)

    def cb_text_changed(self, args):
        """Called when the editbox was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        self.add_button.setEnabled(len(self.key_input.getText()) > 0 and
                                   len(self.value_input.getText()) > 0)

    def cb_add_clicked(self, args):
        """Called when the add button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        key = self.key_input.getText()
        value = self.value_input.getText()
        item = self.edit_dict.findColumnItemWithText(key, 0, None)
        if item is not None:
            row = self.edit_dict.getItemRowIndex(item)
            pos = PyCEGUI.MCLGridRef(row, 1)
            item = self.edit_dict.getItemAtGridReference(pos)
            item.setText(value)
        else:
            row = self.edit_dict.addRow()
            item = PyCEGUI.ListboxTextItem(str(key))
            item.setSelectionBrushImage("TaharezLook/"
                                        "MultiListSelectionBrush")
            self.edit_dict.setItem(item, 0, row)
            self.items.append(item)
            item = PyCEGUI.ListboxTextItem(str(value))
            item.setSelectionBrushImage("TaharezLook/"
                                        "MultiListSelectionBrush")
            self.edit_dict.setItem(item, 1, row)
            self.items.append(item)
        self.values[key] = value
        self.edit_dict.performChildWindowLayout()
        self.edit_dict.invalidate(True)

    def cb_delete_clicked(self, args):
        """Called when the delete button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        item = self.edit_dict.getFirstSelectedItem()
        row = self.edit_dict.getItemRowIndex(item)
        del self.values[item.getText()]
        self.edit_dict.removeRow(row)

    def get_values(self):
        return self.values

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        return True
