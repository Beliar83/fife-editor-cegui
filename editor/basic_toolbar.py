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
        self.outliner = BasicToolbarOutliner(self)
        mode = self.editor.current_mode
        mode.listener.add_callback("mouse_pressed",
                                   self.cb_map_clicked)

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

    def cb_map_clicked(self, click_point, button):
        """Called when a position on the screen was clicked

        Args:

            click_point: A fife.ScreenPoint with the the position that was
            clicked on the screen

            button: The button that was clicked
        """
        if self.editor.selected_layer is None or not self.is_active:
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
            if self.toolbar.editor.selected_layer == inst_layer:
                self.last_instance = instance
                return ((instance, (255, 255, 255, 1)),)
        self.last_instance = None
        return ()
