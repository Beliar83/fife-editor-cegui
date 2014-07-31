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

""" Contains the basic toolbar

.. module:: object_toolbar
    :synopsis: Contains the basic toolbar

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import PyCEGUI
from fife_rpg.game_scene import BaseOutliner

from .toolbarpage import ToolbarPage


class BasicToolbar(ToolbarPage):

    """A toolbar for basic actions, like selecting objects"""

    def __init__(self, editor):
        ToolbarPage.__init__(self, editor, "Basic")
        self.is_active = False
        x_adjust = 5
        pos = self.gui.getPosition()
        y_pos = pos.d_y
        x_pos = PyCEGUI.UDim(0, x_adjust)
        width = PyCEGUI.UDim(0.9, 0.0)
        label = self.gui.createChild("TaharezLook/Label",
                                     "LayersLabel")
        label.setText(_("Layer"))
        label.setWidth(width)
        label.setXPosition(x_pos)
        label.setProperty("HorzFormatting", "LeftAligned")
        self.layers_combo = self.gui.createChild("TaharezLook/Combobox",
                                                 "LayerCombo")
        self.layers_combo.setReadOnly(True)
        y_pos.d_scale = y_pos.d_scale + 0.02
        self.layers_combo.setPosition(pos)
        self.layers = []
        self.layers_combo.setWidth(width)
        self.layers_combo.setXPosition(x_pos)
        self.editor.add_map_switch_callback(self.cb_map_changed)
        self.outliner = BasicToolbarOutliner(self)
        mode = self.editor.current_mode
        mode.listener.add_callback("mouse_pressed",
                                   self.cb_map_clicked)

    @property
    def selected_layer(self):
        """Returns the selected layer in the combo box"""
        item = self.layers_combo.getSelectedItem()
        if item is not None:
            return str(item.getText())
        return None

    def update_contents(self):
        """Update the contents of the toolbar page"""
        pass

    def activate(self):
        """Called when the page gets activated"""
        self.is_active = True
        mode = self.editor.current_mode
        mode.outliner = self.outliner
        mode.listener.is_outlined = True

    def deactivate(self):
        """Called when the page gets deactivated"""
        self.is_active = False
        mode = self.editor.current_mode
        mode.outliner = None
        mode.listener.is_outlined = False

    def cb_map_changed(self, old_map_name, new_map_name):
        """Called when the map of the editor changed

            Args:

                old_map_name: Name of the map that was previously loaded

                new_map_name: Name of the map that was changed to
        """
        game_map = self.editor.maps[new_map_name]
        self.layers_combo.resetList()
        self.layers = []
        self.layers_combo.setText("")
        layers = game_map.fife_map.getLayers()
        for layer in layers:
            item = PyCEGUI.ListboxTextItem(layer.getId())
            item.setSelectionBrushImage("TaharezLook/MultiListSelectionBrush")
            self.layers_combo.addItem(item)
            self.layers.append(item)

    def cb_map_clicked(self, click_point, button):
        """Called when a position on the screen was clicked

        Args:

            click_point: A fife.ScreenPoint with the the position that was
            clicked on the screen

            button: The button that was clicked
        """
        if self.selected_layer is None or not self.is_active:
            return
        game_map = self.editor.current_map
        if game_map:
            instance = self.outliner.last_instance
            if instance is not None:
                self.editor.set_selected_object(instance)


class BasicToolbarOutliner(BaseOutliner):

    """Outliner used by the basic toolbar"""

    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.last_instance = None

    def get_outlines(self, world, instances):
        """Determines whether an instance should be outline and the data
        used for the outline.

        Args:
            world: The world

            instances: A list of instances

        Returns: A list with 2 tuple values: The instance that are to be
        outlined, and their outline data.
        """
        for instance in instances:
            inst_layer = instance.getLocationRef().getLayer().getId()
            if self.toolbar.selected_layer == inst_layer:
                self.last_instance = instance
                return ((instance, (255, 255, 255, 1)),)
        self.last_instance = None
        return ()
