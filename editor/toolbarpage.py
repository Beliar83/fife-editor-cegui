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

""" Contains the base class for a toolbar page

.. module:: toolbarpage
    :synopsis: Contains the base class for a toolbar page.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from abc import ABCMeta, abstractmethod
import PyCEGUI


class ToolbarPage(object):
    """The base class for toolbars, sets up the basic gui"""

    # pylint: disable=unused-argument
    def __init__(self, editor, name, metaclass=ABCMeta):
        if False:  # FOR IDEs
            from fife_rpg_editor import EditorApplication
            self.editor = EditorApplication(None)
        self.editor = editor
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.name = name
        self.gui = window_manager.loadLayoutFromFile("toolbar_page.layout")
        self.gui.setName(name)
        self.gui.setText(name)
        self.gui.setShowHorzScrollbar(False)
    # pylint: enable=unused-argument

    @abstractmethod
    def update_contents(self):
        """Update the contents of the toolbar page"""

    @abstractmethod
    def activate(self):
        """Called when the page gets activated"""

    @abstractmethod
    def deactivate(self):
        """Called when the page gets deactivated"""
