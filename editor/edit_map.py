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

"""Contains classes and functions for a map options dialog

.. module:: edit_map
    :synopsis: Classes and functions for a map options dialog

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import PyCEGUI

from .dialog import Dialog
from .common import cb_cut_copy_paste


class MapOptions(Dialog):

    """Class that displays a map options dialog"""

    def __init__(self, app, game_map=None):
        Dialog.__init__(self, app)
        self.m_name_editor = None
        self.game_map = game_map

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.125, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.125, 4)))
        self.window.setText(_("Map Options"))

        font = root.getFont()

        margin = 5
        evt_key_down = PyCEGUI.Window.EventKeyDown

        vert_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0),
                                   PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0))
        horz_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin),
                                   PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin))

        m_name_layout = root.createChild("HorizontalLayoutContainer")
        m_name_layout.setMargin(vert_margin)
        m_name_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        m_name_label = m_name_layout.createChild("TaharezLook/Label")
        m_name_label.setMargin(horz_margin)
        m_name_label.setText(_("Name of map"))
        m_name_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(m_name_label.getText())
        m_name_label.setWidth(PyCEGUI.UDim(0, text_width))
        m_name_editor = m_name_layout.createChild("TaharezLook/Editbox")
        m_name_editor.setMargin(horz_margin)
        m_name_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        m_name_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        if self.game_map is not None:
            m_name_editor.setText(self.game_map.name)
        self.m_name_editor = m_name_editor

    def get_values(self):
        """Returns the values of the dialog fields"""
        values = {}
        values["MapName"] = self.m_name_editor.getText().encode()
        return values

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        if not self.m_name_editor.getText().strip():
            return False
        return True
