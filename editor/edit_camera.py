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

.. module:: edit_camera
    :synopsis: Classes and functions for a map options dialog

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from future import standard_library
standard_library.install_aliases()
from builtins import str
import PyCEGUI
from fife.fife import Rect, Point

from .dialog import Dialog
from .common import cb_cut_copy_paste


class CameraOptions(Dialog):

    """Class that displays a map options dialog"""

    def __init__(self, app, camera=None):
        Dialog.__init__(self, app)
        self.camera = camera
        self.c_name_editor = None
        self.c_vp_x_editor = None
        self.c_vp_y_editor = None
        self.c_vp_width_editor = None
        self.c_vp_height_editor = None
        self.c_cid_width_editor = None
        self.c_cid_height_editor = None
        self.c_rot_editor = None
        self.c_tilt_editor = None

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.5, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.5, 4)))
        self.window.setText(_("Camera Options"))

        font = root.getFont()

        margin = 5
        evt_key_down = PyCEGUI.Window.EventKeyDown

        vert_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0),
                                   PyCEGUI.UDim(0, margin), PyCEGUI.UDim(0, 0))
        horz_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin),
                                   PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, margin))

        # Camera name

        c_name_layout = root.createChild("HorizontalLayoutContainer")
        c_name_layout.setMargin(vert_margin)
        c_name_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        c_name_label = c_name_layout.createChild("TaharezLook/Label")
        c_name_label.setMargin(horz_margin)
        c_name_label.setText(_("Name of camera"))
        c_name_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_name_label.getText())
        c_name_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_name_editor = c_name_layout.createChild("TaharezLook/Editbox")
        c_name_editor.setMargin(horz_margin)
        c_name_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        c_name_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        self.c_name_editor = c_name_editor

        # Camera Viewport

        c_vp_layout = root.createChild("VerticalLayoutContainer")
        c_vp_layout.setMargin(vert_margin)
        c_vp_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        c_vp_label = c_vp_layout.createChild("TaharezLook/Label")
        c_vp_label.setMargin(horz_margin)
        c_vp_label.setText(_("Viewport"))
        c_vp_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_vp_label.getText())
        c_vp_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_vp_p_editor_layout = c_vp_layout.createChild(
            "HorizontalLayoutContainer")

        # Viewport X

        c_vp_x_label = c_vp_p_editor_layout.createChild("TaharezLook/Label")
        c_vp_x_label.setMargin(horz_margin)
        c_vp_x_label.setText(_("X"))
        c_vp_x_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_vp_x_label.getText())
        c_vp_x_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_vp_x_editor = c_vp_p_editor_layout.createChild("TaharezLook/Editbox")
        c_vp_x_editor.setMargin(horz_margin)
        c_vp_x_editor.setWidth(PyCEGUI.UDim(0.5, -(text_width + 4 * margin)))
        c_vp_x_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        self.c_vp_x_editor = c_vp_x_editor

        # Viewport Y

        c_vp_y_label = c_vp_p_editor_layout.createChild("TaharezLook/Label")
        c_vp_y_label.setMargin(horz_margin)
        c_vp_y_label.setText(_("Y"))
        c_vp_y_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_vp_y_label.getText())
        c_vp_y_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_vp_y_editor = c_vp_p_editor_layout.createChild("TaharezLook/Editbox")
        c_vp_y_editor.setMargin(horz_margin)
        c_vp_y_editor.setWidth(PyCEGUI.UDim(0.5, -(text_width + 4 * margin)))
        c_vp_y_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        self.c_vp_y_editor = c_vp_y_editor

        c_vp_s_editor_layout = c_vp_layout.createChild(
            "HorizontalLayoutContainer")

        # Viewport Width

        c_vp_width_label = c_vp_s_editor_layout.createChild(
            "TaharezLook/Label")
        c_vp_width_label.setMargin(horz_margin)
        c_vp_width_label.setText(_("Width"))
        c_vp_width_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_vp_width_label.getText())
        c_vp_width_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_vp_width_editor = c_vp_s_editor_layout.createChild(
            "TaharezLook/Editbox")
        c_vp_width_editor.setMargin(horz_margin)
        c_vp_width_editor.setWidth(PyCEGUI.UDim(0.5,
                                                -(text_width + 4 * margin)))
        c_vp_width_editor.subscribeEvent(evt_key_down,
                                         cb_cut_copy_paste)
        self.c_vp_width_editor = c_vp_width_editor

        # Viewport Height

        c_vp_height_label = c_vp_s_editor_layout.createChild(
            "TaharezLook/Label")
        c_vp_height_label.setMargin(horz_margin)
        c_vp_height_label.setText(_("Height"))
        c_vp_height_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_vp_height_label.getText())
        c_vp_height_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_vp_height_editor = c_vp_s_editor_layout.createChild(
            "TaharezLook/Editbox")
        c_vp_height_editor.setMargin(horz_margin)
        c_vp_height_editor.setWidth(PyCEGUI.UDim(0.5,
                                                 -(text_width + 4 * margin)))
        c_vp_height_editor.subscribeEvent(evt_key_down,
                                          cb_cut_copy_paste)
        self.c_vp_height_editor = c_vp_height_editor

        # Camera cell image dimensions

        c_cid_layout = root.createChild("VerticalLayoutContainer")
        c_cid_layout.setMargin(vert_margin)
        c_cid_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        c_cid_label = c_cid_layout.createChild("TaharezLook/Label")
        c_cid_label.setMargin(horz_margin)
        c_cid_label.setText(_("Cell image dimensions"))
        c_cid_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_cid_label.getText())
        c_cid_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_cid_editor_layout = c_cid_layout.createChild(
            "HorizontalLayoutContainer")

        # Cell image dimension Width

        c_cid_width_label = c_cid_editor_layout.createChild(
            "TaharezLook/Label")
        c_cid_width_label.setMargin(horz_margin)
        c_cid_width_label.setText(_("Width"))
        c_cid_width_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_cid_width_label.getText())
        c_cid_width_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_cid_width_editor = c_cid_editor_layout.createChild(
            "TaharezLook/Editbox")
        c_cid_width_editor.setMargin(horz_margin)
        c_cid_width_editor.setWidth(PyCEGUI.UDim(0.5,
                                                 -(text_width + 4 * margin)))
        c_cid_width_editor.subscribeEvent(evt_key_down, cb_cut_copy_paste)
        self.c_cid_width_editor = c_cid_width_editor

        # Cell image dimension Height

        c_cid_height_label = c_cid_editor_layout.createChild(
            "TaharezLook/Label")
        c_cid_height_label.setMargin(horz_margin)
        c_cid_height_label.setText(_("Height"))
        c_cid_height_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_cid_height_label.getText())
        c_cid_height_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_cid_height_editor = c_cid_editor_layout.createChild(
            "TaharezLook/Editbox")
        c_cid_height_editor.setMargin(horz_margin)
        c_cid_height_editor.setWidth(PyCEGUI.UDim(0.5,
                                                  -(text_width + 4 * margin)))
        c_cid_height_editor.subscribeEvent(evt_key_down,
                                           cb_cut_copy_paste)
        self.c_cid_height_editor = c_cid_height_editor

        # Camera rotation

        c_rot_layout = root.createChild("HorizontalLayoutContainer")
        c_rot_layout.setMargin(vert_margin)
        c_rot_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        c_rot_label = c_rot_layout.createChild("TaharezLook/Label")
        c_rot_label.setMargin(horz_margin)
        c_rot_label.setText(_("Rotation"))
        c_rot_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_rot_label.getText())
        c_rot_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_rot_editor = c_rot_layout.createChild("TaharezLook/Editbox")
        c_rot_editor.setMargin(horz_margin)
        c_rot_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        c_rot_editor.subscribeEvent(evt_key_down,
                                    cb_cut_copy_paste)
        self.c_rot_editor = c_rot_editor

        # Camera tilt

        c_tilt_layout = root.createChild("HorizontalLayoutContainer")
        c_tilt_layout.setMargin(vert_margin)
        c_tilt_layout.setHeight(PyCEGUI.UDim(0.05, 0))
        c_tilt_label = c_tilt_layout.createChild("TaharezLook/Label")
        c_tilt_label.setMargin(horz_margin)
        c_tilt_label.setText(_("Tilt"))
        c_tilt_label.setProperty("HorzFormatting", "LeftAligned")
        text_width = font.getTextExtent(c_tilt_label.getText())
        c_tilt_label.setWidth(PyCEGUI.UDim(0, text_width))
        c_tilt_editor = c_tilt_layout.createChild("TaharezLook/Editbox")
        c_tilt_editor.setMargin(horz_margin)
        c_tilt_editor.setWidth(PyCEGUI.UDim(1.0, -(text_width + 4 * margin)))
        c_tilt_editor.subscribeEvent(evt_key_down,
                                     cb_cut_copy_paste)
        self.c_tilt_editor = c_tilt_editor

        if self.camera is not None:
            self.c_name_editor.setText(self.camera.getId())
            viewport = self.camera.getViewPort()
            self.c_vp_x_editor.setText(str(viewport.x))
            self.c_vp_y_editor.setText(str(viewport.y))
            self.c_vp_width_editor.setText(str(viewport.w))
            self.c_vp_height_editor.setText(str(viewport.h))
            cell_image_dimensions = self.camera.getCellImageDimensions()
            self.c_cid_width_editor.setText(str(cell_image_dimensions.x))
            self.c_cid_height_editor.setText(str(cell_image_dimensions.y))
            self.c_rot_editor.setText(str(self.camera.getRotation()))
            self.c_tilt_editor.setText(str(self.camera.getTilt()))

    def get_values(self):
        """Returns the values of the dialog fields"""
        values = {}
        try:
            values["CameraName"] = self.c_name_editor.getText().encode()
            vp_x = int(self.c_vp_x_editor.getText())
            vp_y = int(self.c_vp_y_editor.getText())
            vp_width = int(self.c_vp_width_editor.getText())
            vp_height = int(self.c_vp_height_editor.getText())
            values["ViewPort"] = Rect(vp_x, vp_y, vp_width, vp_height)
            cid_width = int(self.c_cid_width_editor.getText())
            cid_height = int(self.c_cid_height_editor.getText())
            values["CellImageDimensions"] = Point(cid_width, cid_height)
            values["Rotation"] = float(self.c_rot_editor.getText())
            values["Tilt"] = float(self.c_tilt_editor.getText())
        except ValueError:
            pass
        return values

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        if not self.c_name_editor.getText().strip():
            return False
        try:
            if int(self.c_vp_x_editor.getText()) < 0:
                return False
            if int(self.c_vp_y_editor.getText()) < 0:
                return False
            if int(self.c_vp_width_editor.getText()) < 0:
                return False
            if int(self.c_vp_height_editor.getText()) < 0:
                return False
            if int(self.c_cid_width_editor.getText()) <= 0:
                return False
            if int(self.c_cid_height_editor.getText()) <= 0:
                return False
            float(self.c_rot_editor.getText())
            float(self.c_tilt_editor.getText())

        except ValueError:
            return False
        return True
