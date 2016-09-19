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

"""Contains classes and functions for a the project settings

.. module:: project_settings
    :synopsis: Classes and functions for a the project settings

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from __future__ import print_function
import os

import PyCEGUI

from .dialog import Dialog
from .common import (cb_cut_copy_paste, is_dir_path_valid, select_path,
                     ask_create_path)


class ProjectSettings(Dialog):

    """Class that displays a project settings dialog"""

    def __init__(self, app, project_settings, project_dir):
        """Constructor"""
        Dialog.__init__(self, app)
        self.d_camera_editor = None
        self.agt_path_editor = None
        self.agt_path_cb = None
        self.p_name_editor = None
        self.d_camera_cb = None
        self.obj_nspace_editor = None
        self.obj_nspace_cb = None
        self.comp_file_editor = None
        self.comp_file_cb = None
        self.act_file_editor = None
        self.act_file_cb = None
        self.syst_file_editor = None
        self.syst_file_cb = None
        self.project_settings = project_settings
        self.project_dir = project_dir
        self.beh_file_editor = None
        self.beh_file_cb = None
        self.comb_file_editor = None
        self.comb_file_cb = None

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.55, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.55, 4)))
        self.window.setText(_("Project Settings"))

        font = root.getFont()

        browse_button_width = 50
        margin = 5
        cb_width = 15
        evt_select_state_changed = PyCEGUI.ToggleButton.EventSelectStateChanged
        evt_btn_clicked = PyCEGUI.ButtonBase.EventMouseClick
        evt_text_accepted = PyCEGUI.Editbox.EventTextAccepted
        evt_key_down = PyCEGUI.Window.EventKeyDown

        vert_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0),
                                   PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0))
        horz_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin),
                                   PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin))

        p_name_layout = root.createChild("HorizontalLayoutContainer")
        p_name_layout.setMargin(vert_margin)
        p_name_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        p_name_label = p_name_layout.createChild("TaharezLook/Label")
        p_name_label.setMargin(horz_margin)
        p_name_label.setText(_("Projectname"))
        p_name_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(p_name_label.getText())
        p_name_label.setWidth(PyCEGUI.UDim(0, text_width))
        p_name_editor = p_name_layout.createChild("TaharezLook/Editbox")
        p_name_editor.setMargin(horz_margin)
        p_name_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        p_name_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        self.p_name_editor = p_name_editor

        agt_path_layout = root.createChild("HorizontalLayoutContainer")
        agt_path_layout.setMargin(vert_margin)
        agt_path_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        agt_path_cb = agt_path_layout.createChild("TaharezLook/Checkbox")
        agt_path_cb.setMargin(horz_margin)
        agt_path_cb.setText(_("Agent Object Path"))
        text_width = font.getTextExtent(agt_path_cb.getText()) + cb_width
        agt_path_cb.setWidth(PyCEGUI.UDim(0, text_width))
        agt_path_edit_layout = agt_path_layout.createChild("HorizontalLayout"
                                                           "Container")
        agt_path_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                    (text_width +
                                                     4 * margin))))
        agt_path_edit_layout.setDisabled(True)
        agt_path_cb.subscribeEvent(evt_select_state_changed,
                                   (lambda args:
                                    cb_op_cb_selection_changed(
                                        args,
                                        agt_path_edit_layout)))
        self.agt_path_cb = agt_path_cb
        agt_path_editor = agt_path_edit_layout.createChild("TaharezLook/"
                                                           "Editbox")
        agt_path_editor.setMargin(horz_margin)
        agt_path_editor.setWidth(PyCEGUI.UDim(1.0, - (text_width + 4 * margin +
                                                      browse_button_width)))
        agt_path_editor.subscribeEvent(evt_text_accepted,
                                       self.cb_agent_path_accepted)
        agt_path_editor.subscribeEvent(evt_key_down,
                                       cb_cut_copy_paste)
        self.agt_path_editor = agt_path_editor
        agt_path_browse = agt_path_edit_layout.createChild("TaharezLook/"
                                                           "Button")
        agt_path_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        agt_path_browse.setText("...")
        agt_path_browse.subscribeEvent(evt_btn_clicked,
                                       self.cb_agent_path_browse_clicked)

        d_camera_layout = root.createChild("HorizontalLayoutContainer")
        d_camera_layout.setMargin(vert_margin)
        d_camera_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        d_camera_cb = d_camera_layout.createChild("TaharezLook/Checkbox")
        d_camera_cb.setMargin(horz_margin)
        d_camera_cb.setText(_("Default Camera"))
        text_width = font.getTextExtent(d_camera_cb.getText()) + cb_width
        d_camera_cb.setWidth(PyCEGUI.UDim(0, text_width))
        self.d_camera_cb = d_camera_cb
        d_camera_editor = d_camera_layout.createChild("TaharezLook/Editbox")
        d_camera_editor.setMargin(horz_margin)
        d_camera_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        d_camera_editor.setDisabled(True)
        d_camera_editor.subscribeEvent(evt_key_down,
                                       cb_cut_copy_paste)
        d_camera_cb.subscribeEvent(evt_select_state_changed,
                                   (lambda args:
                                    cb_op_cb_selection_changed(
                                        args,
                                        d_camera_editor)))
        self.d_camera_editor = d_camera_editor

        obj_nspace_layout = root.createChild("HorizontalLayoutContainer")
        obj_nspace_layout.setMargin(vert_margin)
        obj_nspace_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        obj_nspace_cb = obj_nspace_layout.createChild("TaharezLook/Checkbox")
        obj_nspace_cb.setMargin(horz_margin)
        obj_nspace_cb.setText(_("Object Namespace"))
        text_width = font.getTextExtent(obj_nspace_cb.getText()) + cb_width
        obj_nspace_cb.setWidth(PyCEGUI.UDim(0, text_width))
        self.obj_nspace_cb = obj_nspace_cb
        obj_nspace_editor = obj_nspace_layout.createChild(
            "TaharezLook/Editbox")
        obj_nspace_editor.setMargin(horz_margin)
        obj_nspace_editor.setWidth(PyCEGUI.UDim(1.0,
                                                -(text_width + 4 * margin)))
        obj_nspace_editor.setDisabled(True)
        obj_nspace_editor.subscribeEvent(evt_key_down,
                                         cb_cut_copy_paste)
        obj_nspace_cb.subscribeEvent(evt_select_state_changed,
                                     (lambda args:
                                      cb_op_cb_selection_changed(
                                          args,
                                          obj_nspace_editor)))
        self.obj_nspace_editor = obj_nspace_editor

        filetypes = [('yaml files', '.yaml'), ('all files', '.*')]

        comp_file_layout = root.createChild("HorizontalLayoutContainer")
        comp_file_layout.setMargin(vert_margin)
        comp_file_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        comp_file_cb = comp_file_layout.createChild("TaharezLook/Checkbox")
        comp_file_cb.setMargin(horz_margin)
        comp_file_cb.setText(_("Components File"))
        text_width = font.getTextExtent(comp_file_cb.getText()) + cb_width
        comp_file_cb.setWidth(PyCEGUI.UDim(0, text_width))
        comp_file_edit_layout = comp_file_layout.createChild("HorizontalLayout"
                                                             "Container")
        comp_file_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                     (text_width +
                                                      4 * margin))))
        comp_file_edit_layout.setDisabled(True)
        comp_file_cb.subscribeEvent(evt_select_state_changed,
                                    (lambda args:
                                     cb_op_cb_selection_changed(
                                         args,
                                         comp_file_edit_layout)))
        self.comp_file_cb = comp_file_cb
        comp_file_editor = comp_file_edit_layout.createChild("TaharezLook/"
                                                             "Editbox")
        comp_file_editor.setMargin(horz_margin)
        comp_file_editor.setWidth(PyCEGUI.UDim(1.0,
                                               - (text_width + 4 * margin +
                                                  browse_button_width)))
        comp_file_editor.subscribeEvent(evt_text_accepted,
                                        self.cb_open_file_path_accepted)
        comp_file_editor.subscribeEvent(evt_key_down,
                                        cb_cut_copy_paste)
        self.comp_file_editor = comp_file_editor
        comp_file_browse = comp_file_edit_layout.createChild("TaharezLook/"
                                                             "Button")
        comp_file_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        comp_file_browse.setText("...")
        comp_file_browse.subscribeEvent(
            evt_btn_clicked,
            lambda args: self.cb_open_file_browse_clicked(args,
                                                          comp_file_editor,
                                                          filetypes
                                                          ))

        act_file_layout = root.createChild("HorizontalLayoutContainer")
        act_file_layout.setMargin(vert_margin)
        act_file_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        act_file_cb = act_file_layout.createChild("TaharezLook/Checkbox")
        act_file_cb.setMargin(horz_margin)
        act_file_cb.setText(_("Actions File"))
        text_width = font.getTextExtent(act_file_cb.getText()) + cb_width
        act_file_cb.setWidth(PyCEGUI.UDim(0, text_width))
        act_file_edit_layout = act_file_layout.createChild("HorizontalLayout"
                                                           "Container")
        act_file_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                    (text_width +
                                                     4 * margin))))
        act_file_edit_layout.setDisabled(True)
        act_file_cb.subscribeEvent(evt_select_state_changed,
                                   (lambda args:
                                    cb_op_cb_selection_changed(
                                        args,
                                        act_file_edit_layout)))
        self.act_file_cb = act_file_cb
        act_file_editor = act_file_edit_layout.createChild("TaharezLook/"
                                                           "Editbox")
        act_file_editor.setMargin(horz_margin)
        act_file_editor.setWidth(PyCEGUI.UDim(1.0,
                                              - (text_width + 4 * margin +
                                                  browse_button_width)))
        act_file_editor.subscribeEvent(evt_text_accepted,
                                       self.cb_open_file_path_accepted)
        act_file_editor.subscribeEvent(evt_key_down,
                                       cb_cut_copy_paste)
        self.act_file_editor = act_file_editor
        act_file_browse = act_file_edit_layout.createChild("TaharezLook/"
                                                           "Button")
        act_file_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        act_file_browse.setText("...")
        act_file_browse.subscribeEvent(
            evt_btn_clicked,
            lambda args: self.cb_open_file_browse_clicked(args,
                                                          act_file_editor,
                                                          filetypes
                                                          ))

        syst_file_layout = root.createChild("HorizontalLayoutContainer")
        syst_file_layout.setMargin(vert_margin)
        syst_file_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        syst_file_cb = syst_file_layout.createChild("TaharezLook/Checkbox")
        syst_file_cb.setMargin(horz_margin)
        syst_file_cb.setText(_("Systems File"))
        text_width = font.getTextExtent(syst_file_cb.getText()) + cb_width
        syst_file_cb.setWidth(PyCEGUI.UDim(0, text_width))
        syst_file_edit_layout = syst_file_layout.createChild("HorizontalLayout"
                                                             "Container")
        syst_file_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                     (text_width +
                                                      4 * margin))))
        syst_file_edit_layout.setDisabled(True)
        syst_file_cb.subscribeEvent(evt_select_state_changed,
                                    (lambda args:
                                     cb_op_cb_selection_changed(
                                         args,
                                         syst_file_edit_layout)))
        self.syst_file_cb = syst_file_cb
        syst_file_editor = syst_file_edit_layout.createChild("TaharezLook/"
                                                             "Editbox")
        syst_file_editor.setMargin(horz_margin)
        syst_file_editor.setWidth(PyCEGUI.UDim(1.0,
                                               - (text_width + 4 * margin +
                                                  browse_button_width)))
        syst_file_editor.subscribeEvent(evt_text_accepted,
                                        self.cb_open_file_path_accepted)
        syst_file_editor.subscribeEvent(evt_key_down,
                                        cb_cut_copy_paste)
        self.syst_file_editor = syst_file_editor
        syst_file_browse = syst_file_edit_layout.createChild("TaharezLook/"
                                                             "Button")
        syst_file_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        syst_file_browse.setText("...")
        syst_file_browse.subscribeEvent(
            evt_btn_clicked,
            lambda args: self.cb_open_file_browse_clicked(args,
                                                          syst_file_editor,
                                                          filetypes
                                                          ))

        beh_file_layout = root.createChild("HorizontalLayoutContainer")
        beh_file_layout.setMargin(vert_margin)
        beh_file_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        beh_file_cb = beh_file_layout.createChild("TaharezLook/Checkbox")
        beh_file_cb.setMargin(horz_margin)
        beh_file_cb.setText(_("Behaviours File"))
        text_width = font.getTextExtent(beh_file_cb.getText()) + cb_width
        beh_file_cb.setWidth(PyCEGUI.UDim(0, text_width))
        beh_file_edit_layout = beh_file_layout.createChild("HorizontalLayout"
                                                           "Container")
        beh_file_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                    (text_width +
                                                     4 * margin))))
        beh_file_edit_layout.setDisabled(True)
        beh_file_cb.subscribeEvent(evt_select_state_changed,
                                   (lambda args:
                                    cb_op_cb_selection_changed(
                                        args,
                                        beh_file_edit_layout)))
        self.beh_file_cb = beh_file_cb
        beh_file_editor = beh_file_edit_layout.createChild("TaharezLook/"
                                                           "Editbox")
        beh_file_editor.setMargin(horz_margin)
        beh_file_editor.setWidth(PyCEGUI.UDim(1.0,
                                              - (text_width + 4 * margin +
                                                  browse_button_width)))
        beh_file_editor.subscribeEvent(evt_text_accepted,
                                       self.cb_open_file_path_accepted)
        beh_file_editor.subscribeEvent(evt_key_down,
                                       cb_cut_copy_paste)
        self.beh_file_editor = beh_file_editor
        beh_file_browse = beh_file_edit_layout.createChild("TaharezLook/"
                                                           "Button")
        beh_file_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        beh_file_browse.setText("...")
        beh_file_browse.subscribeEvent(
            evt_btn_clicked,
            lambda args: self.cb_open_file_browse_clicked(args,
                                                          beh_file_editor,
                                                          filetypes
                                                          ))

        comb_file_layout = root.createChild("HorizontalLayoutContainer")
        comb_file_layout.setMargin(vert_margin)
        comb_file_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        comb_file_cb = comb_file_layout.createChild("TaharezLook/Checkbox")
        comb_file_cb.setMargin(horz_margin)
        comb_file_cb.setText(_("Combined File"))
        text_width = font.getTextExtent(comb_file_cb.getText()) + cb_width
        comb_file_cb.setWidth(PyCEGUI.UDim(0, text_width))
        comb_file_edit_layout = comb_file_layout.createChild("HorizontalLayout"
                                                             "Container")
        comb_file_edit_layout.setWidth((PyCEGUI.UDim(1.0, -
                                                     (text_width +
                                                      4 * margin))))
        comb_file_edit_layout.setDisabled(True)
        comb_file_cb.subscribeEvent(evt_select_state_changed,
                                    (lambda args:
                                     cb_op_cb_selection_changed(
                                         args,
                                         comb_file_edit_layout)))
        self.comb_file_cb = comb_file_cb
        comb_file_editor = comb_file_edit_layout.createChild("TaharezLook/"
                                                             "Editbox")
        comb_file_editor.setMargin(horz_margin)
        comb_file_editor.setWidth(PyCEGUI.UDim(1.0,
                                               - (text_width + 4 * margin +
                                                  browse_button_width)))
        comb_file_editor.subscribeEvent(evt_text_accepted,
                                        self.cb_open_file_path_accepted)
        comb_file_editor.subscribeEvent(evt_key_down,
                                        cb_cut_copy_paste)
        self.comb_file_editor = comb_file_editor
        comb_file_browse = comb_file_edit_layout.createChild("TaharezLook/"
                                                             "Button")
        comb_file_browse.setWidth(PyCEGUI.UDim(0.0, browse_button_width))
        comb_file_browse.setText("...")
        comb_file_browse.subscribeEvent(
            evt_btn_clicked,
            lambda args: self.cb_open_file_browse_clicked(args,
                                                          comb_file_editor,
                                                          filetypes
                                                          ))

        if self.project_settings:
            self.fill_fields()

    def get_values(self):
        """Returns the values of the dialog fields"""
        values = {}
        try:
            values["ProjectName"] = self.p_name_editor.getText()
            if self.agt_path_cb.isSelected():
                values["AgentObjectsPath"] = self.agt_path_editor.getText()
            if self.d_camera_cb.isSelected():
                values["Camera"] = self.d_camera_editor.getText()
            if self.obj_nspace_cb.isSelected():
                values["ObjectNamespace"] = self.obj_nspace_editor.getText()
            if self.comp_file_cb.isSelected():
                values["ComponentsFile"] = self.comp_file_editor.getText()
            if self.act_file_cb.isSelected():
                values["ActionsFile"] = self.act_file_editor.getText()
            if self.syst_file_cb.isSelected():
                values["SystemsFile"] = self.syst_file_editor.getText()
            if self.beh_file_cb.isSelected():
                values["BehavioursFile"] = self.beh_file_editor.getText()
            if self.comb_file_cb.isSelected():
                values["CombinedFile"] = self.comb_file_editor.getText()
        except AttributeError:
            print("Please call setup_dialog before trying to get the values")
        return values

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        try:
            if not self.p_name_editor.getText().strip():
                return False
            if self.agt_path_cb.isSelected():
                if not self.agt_path_editor.getText().strip():
                    return False
                path = self.agt_path_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        self.agt_path_editor.getText())
                if not os.path.exists(path):
                    return False
                if not os.path.isdir(path):
                    return False
            if self.d_camera_cb.isSelected():
                if not self.d_camera_editor.getText().strip():
                    return False
            if self.comp_file_cb.isSelected():
                if not self.comp_file_editor.getText().strip():
                    return False
                path = self.comp_file_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        path)
                if not os.path.exists(path):
                    return False
                if not os.path.isfile(path):
                    return False
            if self.act_file_cb.isSelected():
                if not self.act_file_editor.getText().strip():
                    return False
                path = self.act_file_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        path)
                if not os.path.exists(path):
                    return False
                if not os.path.isfile(path):
                    return False
            if self.syst_file_cb.isSelected():
                if not self.syst_file_editor.getText().strip():
                    return False
                path = self.syst_file_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        path)
                if not os.path.exists(path):
                    return False
                if not os.path.isfile(path):
                    return False
            if self.beh_file_cb.isSelected():
                if not self.beh_file_editor.getText().strip():
                    return False
                path = self.beh_file_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        path)
                if not os.path.exists(path):
                    return False
                if not os.path.isfile(path):
                    return False
            if self.comb_file_cb.isSelected():
                if not self.comb_file_editor.getText().strip():
                    return False
                path = self.comb_file_editor.getText()
                if not os.path.isabs(path):
                    path = os.path.join(self.project_dir,
                                        path)
                if not os.path.exists(path):
                    return False
                if not os.path.isfile(path):
                    return False
            return True
        except AttributeError:
            print ("Please call setup_dialog before trying to validate "
                   "the values")
        return False

    def fill_fields(self):
        """Fills the fields from the data in the project file"""

        if "ProjectName" in self.project_settings:
            self.p_name_editor.setText(self.project_settings["ProjectName"])
        if "Camera" in self.project_settings:
            self.d_camera_editor.setText(self.project_settings["Camera"])
            self.d_camera_cb.setSelected(True)
        if "ObjectNamespace" in self.project_settings:
            self.obj_nspace_editor.setText(self.project_settings["Object"
                                                                 "Namespace"])
            self.obj_nspace_cb.setSelected(True)
        if "AgentObjectsPath" in self.project_settings:
            self.agt_path_editor.setText(self.project_settings["AgentObjects"
                                                               "Path"])
            self.agt_path_cb.setSelected(True)
        if "ComponentsFile" in self.project_settings:
            self.comp_file_editor.setText(self.project_settings["Components"
                                                                "File"])
            self.comp_file_cb.setSelected(True)
        if "ActionsFile" in self.project_settings:
            self.act_file_editor.setText(self.project_settings["Actions"
                                                               "File"])
            self.act_file_cb.setSelected(True)
        if "SystemsFile" in self.project_settings:
            self.syst_file_editor.setText(self.project_settings["Systems"
                                                                "File"])
            self.syst_file_cb.setSelected(True)
        if "BehavioursFile" in self.project_settings:
            self.beh_file_editor.setText(self.project_settings["Behaviours"
                                                               "File"])
            self.beh_file_cb.setSelected(True)
        if "CombinedFile" in self.project_settings:
            self.comb_file_editor.setText(self.project_settings["Combined"
                                                                "File"])
            self.comb_file_cb.setSelected(True)

    def make_relative_to_project(self, abspath):
        """Makes a path relative tot he current loaded project, if its inside
        the project directory.

        Returns: If the path is inside the project directory if will return a
        relative version of it, otherwise it will return the full path.
        """
        if abspath.startswith(self.project_dir):
            return os.path.relpath(abspath, self.project_dir)
        return abspath

    def check_agent_path(self, new_path):
        """Checks if path is valid and returns either the path, in relative
        form if possible, or None if invalid."""
        new_path = os.path.normpath(new_path)
        abspath = None
        if os.path.isabs(new_path):
            abspath = new_path
            new_path = self.make_relative_to_project(new_path)
        else:
            abspath = os.path.join(self.project_dir, new_path)
        if not is_dir_path_valid(abspath):
            return None
        return new_path

    def cb_agent_path_browse_clicked(self, args):
        """Callback for click on the browse button of the agent path"""
        initialdir = (self.agt_path_editor.getText().strip() or
                      self.project_dir)
        if not os.path.isabs(initialdir):
            initialdir = os.path.join(self.project_dir, initialdir)
        initialdir = os.path.normpath(initialdir)
        selected_path = select_path("Select Agent Object Path", initialdir)
        if not selected_path:
            return True
        checked_path = self.check_agent_path(selected_path)
        if not checked_path:
            import six.moves.tkinter_messagebox
            six.moves.tkinter_messagebox.showerror(_("Invalid path"),
                                   _("%s is not a valid path") % selected_path)
            return True
        abspath = checked_path
        if not os.path.isabs(abspath):
            abspath = os.path.join(self.project_dir, abspath)
        if not os.path.exists(abspath):
            if not ask_create_path(abspath):
                return
        self.agt_path_editor.setText(checked_path)

    def cb_agent_path_accepted(self, args):
        """Callback when a text was 'accepted' in the agent path editbox"""
        new_path = self.check_agent_path(self.agt_path_editor.getText())
        if new_path is not None:
            self.agt_path_editor.setText(new_path)
            self.agt_path_editor.setCaretIndex(0)

    def check_open_file_path(self, path):
        """Check a file path that should be opened

        Args:

            path: The path to check
        """
        path = os.path.normpath(path)
        if os.path.isabs(path):
            check_path = path
            path = self.make_relative_to_project(path)
        else:
            check_path = os.path.join(self.project_dir, path)
        if not os.path.exists(check_path):
            path = None
        elif not os.path.isfile(check_path):
            path = None
        return path

    def check_and_set_open_file_path(self, target, path):
        """Checks a path that should be opened and sets the contents
        of an editbox to it.

        Args:
            target: The editox that should be set

            path: The path that should be checked"""
        path = self.check_open_file_path(path)
        if path is not None:
            target.setText(path)
            target.setCaretIndex(0)

    def cb_open_file_path_accepted(self, args):
        """Callback when a text was 'accepted' a file path editbox"""
        self.check_and_set_open_file_path(args.window, args.window.getText())

    def cb_open_file_browse_clicked(self, args, target, filetypes):
        """Called when a button to browse a file to open was clicked

        Args:

            args: EventArgs passy ba cegui

            target: The editbox whose text should be set to the selected file

            filetypes: The available file types
        """
        import six.moves.tkinter_filedialog
        selected_file = six.moves.tkinter_filedialog.askopenfilename(
            filetypes=filetypes,
            title="Open file",
            initialdir=self.project_dir)
        if not selected_file:
            return
        self.check_and_set_open_file_path(target, selected_file)


def cb_op_cb_selection_changed(args, target):
    """Called when the selection state of a checkbox in front of an option
    was changed

    Args:

        args: WindowEventArgs passed by cegui

        target: The window to enabled/disable by the checkbox
    """
    window = args.window
    target.setDisabled(not window.isSelected())
