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

"""Contains a class to display a messagebox

.. module:: object_toolbar
    :synopsis: Contains a class to display a messagebox

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import PyCEGUI
from fife_rpg.helpers import Enum


class MessageBox(object):

    """A class that displays a message box"""

    BUTTONS = Enum(("OK",
                    "OK_CANCEL",
                    "YES_NO",
                    "YES_NO_CANCEL"))
    RETURN_VALUES = Enum(("OK", "YES", "NO", "CANCEL"))
    MAX_TEXT_WIDTH = 0.3
    WIDGET_MARGIN = 5

    def __init__(self, title, message, buttons=BUTTONS.OK):
        self.__title = title
        self.__mesage = message
        self.__buttons = buttons
        self.__main_gui = None
        self.__retval = None

    @property
    def return_value(self):
        """The value of the clicked button.

        None if the dialog is still active

        RETURN_VALUES.OK if an Ok button was clicked

        RETURN_VALUES.YES if a Yes button was clicked

        RETURN_VALUES.NO if a No button was clicked

        RETURN_VALUES.CANCEL if a Cancel button was clicked
        """
        return self.__retval

    def setup_gui(self, root):
        """Create the gui elements"""
        try:
            _("")
        except (NameError, TypeError):
            _ = str
        self.__main_gui = root.createChild("TaharezLook/"
                                           "FrameWindow")
        self.__main_gui.setText(self.__title)
        self.__main_gui.setCloseButtonEnabled(False)
        self.__main_gui.setSizingEnabled(False)
        font = self.__main_gui.getFont()
        root_width = root.getPixelSize().d_width
        max_text_width_px = self.MAX_TEXT_WIDTH * root_width
        gui_width = font.getTextExtent(self.__title) + 75
        label = self.__main_gui.createChild("TaharezLook/Label")
        words = self.__mesage.split(' ')
        start = 0
        lines = 0
        formatted_message = ""
        for counter in xrange(len(words) + 1):
            cur_message = ' '.join(words[start:counter])
            cur_width = font.getTextExtent(cur_message)
            if cur_width > max_text_width_px:
                if lines >= 1:
                    formatted_message += "\n"
                formatted_message += ' '.join(words[start:counter - 1])
                start = counter - 1
                lines += 1
        if start <= len(words):
            if lines >= 1:
                formatted_message += "\n"
            formatted_message += ' '.join(words[start:])
            lines += 1
        font_height = font.getFontHeight()
        line_spacing = font.getLineSpacing()
        text_height = (lines * (font_height))
        label.setHeight(PyCEGUI.UDim(0, text_height))
        label.setText(formatted_message)
        text_width = font.getTextExtent(formatted_message)
        if text_width > max_text_width_px:
            label.setWidth(PyCEGUI.UDim(0, max_text_width_px))
            label_width = max_text_width_px
        else:
            label_width = text_width
            label.setWidth(PyCEGUI.UDim(0, text_width))
        if label_width > gui_width:
            gui_width = label_width
        gui_height = text_height + self.WIDGET_MARGIN

        btn_ok_text = _("OK")
        btn_ok_width = font.getTextExtent(btn_ok_text)
        btn_cancel_text = _("Cancel")
        btn_cancel_width = font.getTextExtent(btn_cancel_text)
        btn_ok_cancel_width = (btn_ok_width + self.WIDGET_MARGIN +
                               btn_cancel_width)
        btn_yes_text = _("Yes")
        btn_yes_width = font.getTextExtent(btn_yes_text)
        btn_no_text = _("No")
        btn_no_width = font.getTextExtent(btn_no_text)
        btn_yes_no_width = (btn_yes_width + self.WIDGET_MARGIN + btn_no_width)
        btn_yes_no_cancel_width = (btn_yes_width + self.WIDGET_MARGIN +
                                   btn_no_width + self.WIDGET_MARGIN +
                                   btn_cancel_width)
        if self.__buttons == self.BUTTONS.OK:
            btn_ok = self.__main_gui.createChild("TaharezLook/Button")
            btn_ok.setWidth(PyCEGUI.UDim(0, btn_ok_width))
            btn_ok.setText(btn_ok_text)
            btn_ok.setHeight(PyCEGUI.UDim(0, font_height))
            y_pos = PyCEGUI.UDim(0, gui_height + self.WIDGET_MARGIN)
            btn_ok.setYPosition(y_pos)
            btn_ok.setXPosition(PyCEGUI.UDim(0.5, -(btn_ok_width / 2)))
            btn_ok.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_ok_clicked)
            if btn_ok_width > gui_width:
                gui_width = btn_ok_width
            gui_height += font_height + self.WIDGET_MARGIN
        if self.__buttons == self.BUTTONS.OK_CANCEL:
            btn_cont = self.__main_gui.createChild("DefaultWindow")
            btn_cont.setHeight(PyCEGUI.UDim(0, font_height))
            btn_cont.setWidth(PyCEGUI.UDim(0, btn_ok_cancel_width))
            y_pos = PyCEGUI.UDim(0, gui_height + self.WIDGET_MARGIN)
            btn_cont.setYPosition(y_pos)
            btn_cont.setXPosition(PyCEGUI.UDim(0.5,
                                               -(btn_ok_cancel_width / 2)))
            btn_ok = btn_cont.createChild("TaharezLook/Button")
            btn_ok.setWidth(PyCEGUI.UDim(0, btn_ok_width))
            btn_ok.setText(btn_ok_text)
            btn_ok.setHeight(PyCEGUI.UDim(0, font_height))
            btn_ok.setXPosition(PyCEGUI.UDim(0, 0))
            btn_ok.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_ok_clicked)
            btn_cancel = btn_cont.createChild("TaharezLook/Button")
            btn_cancel.setWidth(PyCEGUI.UDim(0, btn_cancel_width))
            btn_cancel.setText(btn_cancel_text)
            btn_cancel.setHeight(PyCEGUI.UDim(0, font_height))
            btn_cancel_x_pos = PyCEGUI.UDim(0.0,
                                            btn_ok_width + self.WIDGET_MARGIN)
            btn_cancel.setXPosition(btn_cancel_x_pos)
            btn_cancel.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                      self.cb_cancel_clicked)
            if btn_ok_cancel_width > gui_width:
                gui_width = btn_ok_cancel_width
            gui_height += font_height + self.WIDGET_MARGIN
        elif self.__buttons == self.BUTTONS.YES_NO:
            btn_cont = self.__main_gui.createChild("DefaultWindow")
            btn_cont.setHeight(PyCEGUI.UDim(0, font_height))
            btn_cont.setWidth(PyCEGUI.UDim(0, btn_yes_no_width))
            y_pos = PyCEGUI.UDim(0, gui_height + self.WIDGET_MARGIN)
            btn_cont.setYPosition(y_pos)
            btn_cont.setXPosition(PyCEGUI.UDim(0.5,
                                               -(btn_yes_no_width / 2)))
            btn_yes = btn_cont.createChild("TaharezLook/Button")
            btn_yes.setWidth(PyCEGUI.UDim(0, btn_yes_width))
            btn_yes.setText(btn_yes_text)
            btn_yes.setHeight(PyCEGUI.UDim(0, font_height))
            btn_yes_x_pos = PyCEGUI.UDim(0, 0)
            btn_yes.setXPosition(btn_yes_x_pos)
            btn_yes.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                   self.cb_yes_clicked)
            btn_no = btn_cont.createChild("TaharezLook/Button")
            btn_no.setWidth(PyCEGUI.UDim(0, btn_no_width))
            btn_no.setText(btn_no_text)
            btn_no.setHeight(PyCEGUI.UDim(0, font_height))
            btn_no_x_pos = PyCEGUI.UDim(0.0,
                                        btn_yes_width + self.WIDGET_MARGIN)
            btn_no.setXPosition(btn_no_x_pos)
            btn_no.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_no_clicked)
            if btn_yes_no_width > gui_width:
                gui_width = btn_yes_no_width
            gui_height += font_height + self.WIDGET_MARGIN
        elif self.__buttons == self.BUTTONS.YES_NO_CANCEL:
            btn_cont = self.__main_gui.createChild("DefaultWindow")
            btn_cont.setHeight(PyCEGUI.UDim(0, font_height))
            btn_cont.setWidth(PyCEGUI.UDim(0, btn_yes_no_cancel_width))
            y_pos = PyCEGUI.UDim(0, gui_height + self.WIDGET_MARGIN)
            btn_cont.setYPosition(y_pos)
            btn_cont.setXPosition(PyCEGUI.UDim(0.5,
                                               -(btn_yes_no_cancel_width / 2)))
            btn_yes = btn_cont.createChild("TaharezLook/Button")
            btn_yes.setWidth(PyCEGUI.UDim(0, btn_yes_width))
            btn_yes.setText(btn_yes_text)
            btn_yes.setHeight(PyCEGUI.UDim(0, font_height))
            btn_yes_x_pos = PyCEGUI.UDim(0, 0)
            btn_yes.setXPosition(btn_yes_x_pos)
            btn_yes.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                   self.cb_yes_clicked)
            btn_no = btn_cont.createChild("TaharezLook/Button")
            btn_no.setWidth(PyCEGUI.UDim(0, btn_no_width))
            btn_no.setText(btn_no_text)
            btn_no.setHeight(PyCEGUI.UDim(0, font_height))
            btn_no_x_pos = PyCEGUI.UDim(0.0,
                                        btn_yes_width + self.WIDGET_MARGIN)
            btn_no.setXPosition(btn_no_x_pos)
            btn_no.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_no_clicked)
            btn_cancel = btn_cont.createChild("TaharezLook/Button")
            btn_cancel.setWidth(PyCEGUI.UDim(0, btn_cancel_width))
            btn_cancel.setText(btn_cancel_text)
            btn_cancel.setHeight(PyCEGUI.UDim(0, font_height))
            btn_cancel_x_pos = PyCEGUI.UDim(
                0.0,
                btn_yes_width + self.WIDGET_MARGIN +
                btn_no_width + self.WIDGET_MARGIN)
            btn_cancel.setXPosition(btn_cancel_x_pos)
            btn_cancel.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                      self.cb_cancel_clicked)
            if btn_yes_no_cancel_width > gui_width:
                gui_width = btn_yes_no_cancel_width
            gui_height += font_height + self.WIDGET_MARGIN

        gui_height += 2 * (self.WIDGET_MARGIN + line_spacing)
        self.__main_gui.setWidth(PyCEGUI.UDim(0, gui_width))
        self.__main_gui.setHeight(PyCEGUI.UDim(0, gui_height))
        middle_x = PyCEGUI.UDim(0.5, -(gui_width / 2))
        middle_y = PyCEGUI.UDim(0.5, -(gui_height / 2))
        self.__main_gui.setPosition(PyCEGUI.UVector2(middle_x, middle_y))

    def __close(self):
        """Close the box"""
        self.__main_gui.setModalState(False)
        self.__main_gui.hide()
        self.__main_gui.getParent().removeChild(self.__main_gui)

    def cb_ok_clicked(self, args):
        """Called when an ok button was clicked"""
        self.__retval = self.RETURN_VALUES.OK
        self.__close()

    def cb_yes_clicked(self, args):
        """Called when a yes button was clicked"""
        self.__retval = self.RETURN_VALUES.YES
        self.__close()

    def cb_no_clicked(self, args):
        """Called when a no button was clicked"""
        self.__retval = self.RETURN_VALUES.NO
        self.__close()

    def cb_cancel_clicked(self, args):
        """Called when a cancel button was clicked"""
        self.__retval = self.RETURN_VALUES.CANCEL
        self.__close()

    def show(self, window):
        """Show the dialog

        Args:

            window: The window that the dialog is displayed on
        """
        self.__retval = None
        self.setup_gui(window)
        self.__main_gui.show()
        self.__main_gui.setModalState(True)
