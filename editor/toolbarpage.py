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

    def __init__(self, editor, name, metaclass=ABCMeta):
        if False:  # FOR IDEs
            from fife_rpg_editor import EditorApplication
            self.editor = EditorApplication(None)
        self.editor = editor
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.gui = window_manager.loadLayoutFromFile("toolbar_page.layout")
        title = self.gui.getChild("Title")
        assert isinstance(title, PyCEGUI.FrameWindow)
        title.setText(name)
        self.items = self.gui.getChild("Items")

    @abstractmethod
    def update_items(self):
        """Update the items of the toolbar page"""
