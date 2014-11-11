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

"""Contains classes and functions for a new project dialog"""
import os

import PyCEGUI

from .project_settings import ProjectSettings
from .common import (cb_cut_copy_paste, is_dir_path_valid, select_path,
                     ask_create_path)


class NewProject(ProjectSettings):

    """Class that displays new project dialog"""

    def __init__(self, editor):
        """Constructor"""
        ProjectSettings.__init__(self, editor, None, "")
        self.project_path_editor = None

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        font = root.getFont()

        browse_button_width = 50
        margin = 5

        evt_btn_clicked = PyCEGUI.ButtonBase.EventMouseClick
        evt_key_down = PyCEGUI.Window.EventKeyDown

        vert_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0),
                                   PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0))
        horz_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin),
                                   PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin))

        project_path_layout = root.createChild("HorizontalLayoutContainer")
        project_path_layout.setMargin(vert_margin)
        project_path_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        project_path_label = project_path_layout.createChild("TaharezLook/"
                                                             "Label")
        project_path_label.setMargin(horz_margin)
        project_path_label.setText(_("Project Path"))
        project_path_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = (font.getTextExtent(project_path_label.getText()))
        project_path_label.setWidth(PyCEGUI.UDim(0, text_width))
        project_path_editor = project_path_layout.createChild("TaharezLook/"
                                                              "Editbox")
        project_path_editor.setMargin(horz_margin)
        project_path_editor.setWidth(PyCEGUI.UDim(1.0, -
                                                  (text_width + 4 * margin +
                                                   browse_button_width)))
        project_path_editor.subscribeEvent(evt_key_down,
                                           cb_cut_copy_paste)

        self.project_path_editor = project_path_editor
        project_path_browse = project_path_layout.createChild("TaharezLook/"
                                                              "Button")
        project_path_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        project_path_browse.setText("...")
        project_path_browse.subscribeEvent(evt_btn_clicked,
                                           self.cb_project_path_browse_clicked)
        ProjectSettings.setup_dialog(self, root)

        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.61, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.61, 4)))
        self.window.setText(_("New Project"))

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        if not self.project_path_editor.getText().strip():
            return False
        path = self.project_path_editor.getText()
        if not os.path.exists(path):
            return False
        if not os.path.isdir(path):
            return False
        return ProjectSettings.validate(self)

    def get_values(self):
        """Returns the values of the dialog fields"""
        values = ProjectSettings.get_values(self)
        values["ProjectPath"] = self.project_path_editor.getText()
        return values

    def cb_project_path_browse_clicked(self, args):
        """Callback for click on the browse button of the project path"""
        old_path = self.project_path_editor.getText() or None
        selected_path = select_path("Select Project Path", old_path)
        if not selected_path:
            return True
        selected_path = os.path.normpath(selected_path)
        if not is_dir_path_valid(selected_path):
            import tkMessageBox
            tkMessageBox.showerror(_("Invalid path"),
                                   _("%s is not a valid path") % selected_path)
            return True
        if not os.path.exists(selected_path):
            if not ask_create_path(selected_path):
                return
        self.project_path_editor.setText(selected_path)
