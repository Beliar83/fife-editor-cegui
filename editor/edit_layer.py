# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains classes and functions for a layer options dialog

.. module:: edit_layer
    :synopsis: Classes and functions for a layer options dialog

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
import PyCEGUI

from .dialog import Dialog
from .common import cb_cut_copy_paste


class LayerOptions(Dialog):

    """Class that displays a layer options dialog"""

    def __init__(self, app, grid_types, layer=None):
        Dialog.__init__(self, app)
        self.layer = layer
        self.grid_types = grid_types
        self.l_name_editor = None
        self.cellgrid_edit = None
        self.cellgrid_combo_items = []

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.25, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.25, 4)))
        self.window.setText(_("Layer Options"))

        font = root.getFont()

        margin = 5
        evt_key_down = PyCEGUI.Window.EventKeyDown

        vert_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0),
                                   PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0))
        horz_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin),
                                   PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin))

        l_name_layout = root.createChild("HorizontalLayoutContainer")
        l_name_layout.setMargin(vert_margin)
        l_name_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        l_name_label = l_name_layout.createChild("TaharezLook/Label")
        l_name_label.setMargin(horz_margin)
        l_name_label.setText(_("Name of layer"))
        l_name_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(l_name_label.getText())
        l_name_label.setWidth(PyCEGUI.UDim(0, text_width))
        l_name_editor = l_name_layout.createChild("TaharezLook/Editbox")
        l_name_editor.setMargin(horz_margin)
        l_name_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        l_name_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        if self.layer is not None:
            l_name_editor.setText(self.layer.getId())
        self.l_name_editor = l_name_editor

        cellgrid_layout = root.createChild("HorizontalLayoutContainer")
        cellgrid_layout.setMargin(vert_margin)
        cellgrid_layout.setHeight(PyCEGUI.UDim(0.10, 0))
        cellgrid_label = cellgrid_layout.createChild("TaharezLook/Label")
        cellgrid_label.setMargin(horz_margin)
        cellgrid_label.setText(_("Cellgrid type"))
        cellgrid_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(cellgrid_label.getText())
        cellgrid_label.setWidth(PyCEGUI.UDim(0, text_width))
        cellgrid_edit = cellgrid_layout.createChild("TaharezLook/Combobox")
        for grid_type in self.grid_types:
            item = PyCEGUI.ListboxTextItem(grid_type.capitalize())
            cellgrid_edit.addItem(item)
            self.cellgrid_combo_items.append(item)
        cellgrid_edit.setReadOnly(True)
        cellgrid_edit.setHeight(PyCEGUI.UDim(0.25 * len(self.grid_types), 0))
        if self.layer is not None:
            cur_grid_type = self.layer.getCellGrid().getType().capitalize()
            cellgrid_edit.setText(cur_grid_type)
            cellgrid_edit.selectListItemWithEditboxText()
        self.cellgrid_edit = cellgrid_edit

    def get_values(self):
        """Returns the values of the dialog fields"""
        values = {}
        values["LayerName"] = self.l_name_editor.getText().encode()
        selected_grid_type = self.cellgrid_edit.getSelectedItem()
        if selected_grid_type is not None:
            values["GridType"] = selected_grid_type.getText().encode().lower()
        else:
            values["GridType"] = ""
        return values

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        if not self.l_name_editor.getText().strip():
            return False
        if self.cellgrid_edit.getSelectedItem() is None:
            return False
        return True
