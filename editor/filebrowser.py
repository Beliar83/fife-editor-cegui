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

"""Contains classes and functions for a filebrowser"""

import os

import PyCEGUI


class FileBrowser(object):
    """Class that displays a filebrowser"""

    def __init__(self, engine, directory=None, extension_filter=None):
        """Constructor

        Args:

            engine: A fife engine object

            directory: The starting directory of the filebrowser

            extension_filter: A list of file extension to show. None means
                              all extensions
        """
        self.engine = engine
        self.directory = directory or os.getcwd()
        self.extension_filter = extension_filter or ()
        self._selected_file = None
        self._retval = None
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.window = window_manager.loadLayoutFromFile("filebrowser.layout")
        self.window.hide()
        #self.window.setAlwaysOnTop(True)
        main = self.window.getChild("Main")
        self.current_directory_widget = main.getChild("CurrentDirectory")
        top = main.getChild("Top")
        self.dir_list_widget = top.getChild("DirList")
        self.file_list_widget = top.getChild("FileList")
        self.filepath = main.getChild("FilePath")

        self.setup_windows()
        self.current_directory = ""

    @property
    def selected_file(self):
        """The file that was selected"""
        return self._selected_file

    @property
    def return_value(self):
        """The value of the clicked button.

        None if the dialog is still active

        True if OK was clicked

        False if Cancel was clicked
        """
        return self._retval

    def setup_windows(self):
        """Sets up the windows"""
        main = self.window.getChild("Main")
        self.dir_list_widget.subscribeEvent(
                                          PyCEGUI.Listbox.EventSelectionChanged,
                                          self.cb_directory_selected)
        self.file_list_widget.subscribeEvent(
                                          PyCEGUI.Listbox.EventSelectionChanged,
                                          self.cb_file_selected)

        # TODO events for the filepath
        self.filepath.subscribeEvent(PyCEGUI.Editbox.EventTextAccepted,
                                     self.cb_filepath_accepted)

        bottom = main.getChild("Bottom")
        okay = bottom.getChild("OK")
        okay.setText(_("OK"))
        okay.subscribeEvent(PyCEGUI.ButtonBase.EventActivated, self.cb_ok)
        cancel = bottom.getChild("Cancel")
        cancel.setText(_("Cancel"))
        cancel.subscribeEvent(PyCEGUI.ButtonBase.EventActivated, self.cb_cancel)

    def select_directory(self, path):
        """Update the filebrowser to she contents of a directory

        Args:

            path: The path to the directory
        """
        if not os.path.isdir(path):
            raise ValueError("%s is not a valid directory." % (path))
        self.current_directory = path
        self.current_directory_widget.setText(path)
        self.engine.pump()
        contents = os.listdir(path)
        dir_list = []
        if os.path.abspath(os.path.join(path, "..")) != path:
            dir_list.append("..")
        file_list = []
        for content in contents:
            if os.path.isdir(os.path.join(path, content)):
                dir_list.append(content)
            elif os.path.isfile(os.path.join(path, content)):
                extension = os.path.splitext(content)[1][1:]
                if (len(self.extension_filter) == 0 or
                    extension in self.extension_filter):
                    file_list.append(content)
        dir_list = sorted(dir_list, key=lambda s: s.lower())
        file_list = sorted(file_list, key=lambda s: s.lower())
        self.dir_list_widget.resetList()
        self.file_list_widget.resetList()
        self.dir_list_widget.addItem(PyCEGUI.ListboxTextItem(_("Populating"
                                                               " contents")))
        self.file_list_widget.addItem(PyCEGUI.ListboxTextItem(_("Populating"
                                                                " contents")))

        self.engine.pump()
        self.dir_list_widget.resetList()
        for directory in dir_list:
            item = PyCEGUI.ListboxTextItem(directory)
            self.dir_list_widget.addItem(item)
        self.engine.pump()
        self.file_list_widget.resetList()
        for filename in file_list:
            item = PyCEGUI.ListboxTextItem(filename)
            item.setSelectionBrushImage("TaharezLook/ListboxSelectionBrush")
            self.file_list_widget.addItem(item)

    def show(self, window):
        """Show the dialog

        Args:

            window: The window that the dialog is displayed on
        """
        self._retval = None
        window.addChild(self.window)
        self.window.show()
        self.window.setModalState(True)
        self.select_directory(os.getcwd())

    def validate_and_close(self):
        """Validate the current filepath and close if valid"""
        if not os.path.exists(self._selected_file):
            return
        self._retval = True
        self.window.setModalState(False)
        self.window.hide()
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

    def cb_directory_selected(self, args):
        """Callback for directory selection"""
        if self.dir_list_widget.getSelectedCount() == 0:
            return
        item = self.dir_list_widget.getFirstSelectedItem()
        new_path = os.path.join(self.current_directory, item.getText())
        self.select_directory(os.path.abspath(new_path))

    def cb_file_selected(self, args):
        """Callback for file selection"""
        if self.file_list_widget.getSelectedCount() == 0:
            self._selected_file = ""
            self.filepath.setText("")
        item = self.file_list_widget.getFirstSelectedItem()
        self._selected_file = os.path.join(self.current_directory,
                                           item.getText())
        self.filepath.setText(self._selected_file)

    def cb_filepath_accepted(self, args):
        """Callback for when the enter/return/tab key was pressed in the
        filepath editbox
        """
        self.validate_and_close()
