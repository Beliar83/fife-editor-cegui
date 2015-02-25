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

"""Contains classes and functions for an empty dialog

.. module:: dialog
    :synopsis: Classes and functions for an empty dialog

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from abc import ABCMeta, abstractmethod

import PyCEGUI


class Dialog(object):  # pylint: disable=abstract-class-not-used
    """Class that displays an empty dialog"""

    __metaclass__ = ABCMeta

    def __init__(self, editor):
        """Constructor"""
        self._retval = None
        self.window = None
        self.editor = editor
        self.__area = None
        self.__dialog_title = None
        self.__ok_btn = None

    @property
    def return_value(self):
        """The value of the clicked button.

        None if the dialog is still active

        True if OK was clicked

        False if Cancel was clicked
        """
        return self._retval

    def setup_windows(self, root):
        """Sets up the windows"""
        font = root.getFont()
        btn_height = font.getFontHeight() + 2
        btn_margin = PyCEGUI.UBox(PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, 5),
                                  PyCEGUI.UDim(0, 0), PyCEGUI.UDim(0, 5))

        if self.window:
            self.window.destroy()

        self.window = root.createChild("TaharezLook/FrameWindow",
                                       "ProjectSettings")
        self.window.hide()
        # self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
        #                    PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.5, 4))
        self.window.setRollupEnabled(False)
        self.window.setCloseButtonEnabled(False)
        self.window.setAlwaysOnTop(True)
        main = self.window.createChild("VerticalLayoutContainer", "Main")
        main.setWidth(PyCEGUI.UDim(1.0, 0))
        main.setHeight(PyCEGUI.UDim(1.0, 0))
        self.setup_dialog(main)

        btn_window = main.createChild("HorizontalLayoutContainer", "Buttons")
        btn_window.setHorizontalAlignment(PyCEGUI.HA_CENTRE)
        ok_btn = btn_window.createChild("TaharezLook/Button", "OK")
        ok_btn.setText(_("OK"))
        text_width = font.getTextExtent(ok_btn.getText())
        ok_btn.setHeight(PyCEGUI.UDim(0.0, btn_height))
        ok_btn.setWidth(PyCEGUI.UDim(0.0, text_width + 30))
        ok_btn.setMargin(btn_margin)
        self.__ok_btn = ok_btn
        cancel_btn = btn_window.createChild("TaharezLook/Button", "Cancel")
        cancel_btn.setText(_("Cancel"))
        text_width = font.getTextExtent(cancel_btn.getText())
        cancel_btn.setHeight(PyCEGUI.UDim(0.0, btn_height))
        cancel_btn.setWidth(PyCEGUI.UDim(0.0, text_width + 30))
        cancel_btn.setMargin(btn_margin)

        ok_btn.subscribeEvent(PyCEGUI.ButtonBase.EventActivated, self.cb_ok)

        cancel_btn.subscribeEvent(PyCEGUI.ButtonBase.EventActivated,
                                  self.cb_cancel)

    @abstractmethod
    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """

    def __show(self, window):
        """Show the dialog

        Args:

            window: The window that the dialog is displayed on
        """
        self._retval = None
        self.setup_windows(window)
        self.window.show()

    def show_modal(self, window, proc_func):
        """Show the dialog modally

        Args:

            window: The window that the dialog is displayed on

            proc_func: Function to periodically call while waiting for window
            to close
        """
        self.__show(window)
        self.window.setModalState(True)
        while self.return_value is None:
            proc_func()
            if self.editor.quitRequested:
                return None
            is_valid = False
            try:
                is_valid = self.validate()
            except Exception as error:  # pylint: disable=broad-except
                print error
            self.__ok_btn.setDisabled(not is_valid)
        if self.return_value:
            return self.get_values()

    @abstractmethod
    def get_values(self):
        """Returns the values of the dialog fields"""

    @abstractmethod
    def validate(self):
        """Check if the current state of the dialog fields is valid"""

    def validate_and_close(self):
        """Validate the current filepath and close if valid"""
        if not self.validate():
            return
        self._retval = True
        self.window.setModalState(False)
        self.window.getParent().removeChild(self.window)

    def cb_ok(self, args):
        """Callback for click on the OK button"""
        self.validate_and_close()

    def cb_cancel(self, args):
        """Callback for click on the Cancel button"""
        self._retval = False
        self.window.setModalState(False)
        self.window.hide()
        self.window.getParent().removeChild(self.window)
