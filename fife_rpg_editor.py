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

import os

import PyCEGUI
from fife.extensions.fife_settings import Setting
from fife_rpg import RPGApplicationCEGUI
from fife.extensions.serializers.simplexml import SimpleXMLSerializer

from editor.filebrowser import FileBrowser


class EditorApplication(RPGApplicationCEGUI):
    """The application for the editor"""

    def __init__(self, setting):
        """Constructor

        """
        #For IDES
        if False:
            self.editor_window = PyCEGUI.DefaultWindow()
            self.main_container = PyCEGUI.VerticalLayoutContainer()
            self.menubar = PyCEGUI.Menubar()
            self.file_menu = PyCEGUI.MenuItem()
        RPGApplicationCEGUI.__init__(self, setting)

        self.current_project_file = ""
        self.project = None
        self.project_source = None

        self.__loadData()
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.editor_window = window_manager.loadLayoutFromFile(
            "editor_window.layout")
        self.main_container = self.editor_window.getChild("MainContainer")
        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(
            self.editor_window)
        self.create_menu()
        self.create_world()
        self.filebrowser = FileBrowser(self.engine)

    def __loadData(self):
        """Load gui datafiles"""
        PyCEGUI.ImageManager.getSingleton().loadImageset(
            "TaharezLook.imageset")
        PyCEGUI.SchemeManager.getSingleton().createFromFile(
            "TaharezLook.scheme")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-10.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-12.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-14.font")

    def create_menu(self):
        """Create the menu items"""
        self.menubar = self.main_container.getChild("Menu")
        self.file_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "File")
        self.file_menu.setText(_("File"))
        self.file_menu.setVerticalAlignment(
            PyCEGUI.VerticalAlignment.VA_CENTRE)
        file_popup = self.file_menu.createChild("TaharezLook/PopupMenu",
                                                "FilePopup")
        file_new = file_popup.createChild("TaharezLook/MenuItem", "FileNew")
        file_new.setText(_("New Project"))
        file_open = file_popup.createChild("TaharezLook/MenuItem", "FileOpen")
        file_open.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_open)
        file_open.setText(_("Open Project"))
        file_open = file_popup.createChild("TaharezLook/MenuItem", "FileClose")
        file_open.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_close)
        file_open.setText(_("Close Project"))
        file_quit = file_popup.createChild("TaharezLook/MenuItem", "FileQuit")
        file_quit.setText(_("Quit"))
        file_quit.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_quit)

    def clear(self):
        """Clears all data and restores saved settings"""
        self.__maps = {}
        self.__current_map = None
        self.__components = {}
        self.__actions = {}
        self.__systems = {}
        self.__behaviours = {}
        self.world.clear()
        model = self.engine.getModel()
        model.deleteObjects()
        model.deleteMaps()
        if self.project_source is not None:
            self.engine.getVFS().removeSource(self.project_source)
            self.project_source = None
        self.project_dir = None
        self.project = None

    def load_project(self, filepath):
        """Tries to load a project

        Args:

            filepath: The path to the project file.

        Returns: True of the project was loaded. False if not."""
        self.clear()
        settings = SimpleXMLSerializer()
        settings.load(filepath)
        if "fife-rpg" in settings.getModuleNameList():
            self.project = settings
            project_dir = str(os.path.split(filepath)[0])
            self.project_source = self.engine.getVFS().addNewSource(project_dir)
            self.load_maps()
            return True
        return False

    def load_map(self, name):
        """Load the map with the given name

        Args:
            name: The name of the map to load
        """
        maps_path = self.project.get(
            "fife-rpg", "MapsPath", "maps")
        camera = self.project.get(
            "fife-rpg", "Camera", "main")
        self.settings.set(
            "fife-rpg", "MapsPath", maps_path)
        self.settings.set(
            "fife-rpg", "Camera", camera)
        try:
            RPGApplicationCEGUI.load_map(self, name)
        except Exception as e:
            print e.message

    def load_maps(self):
        """Load the names of the available maps from a map file."""
        maps_path = self.project.get(
            "fife-rpg", "MapsPath", "maps")
        self.settings.set(
            "fife-rpg", "MapsPath", maps_path)
        RPGApplicationCEGUI.load_maps(self)

    def cb_quit(self, args):
        """Callback when quit was clicked in the file menu"""
        self.quit()

    def cb_close(self, args):
        """Callback when cllose was clicked in the file menu"""
        self.clear()

    def cb_open(self, args):
        """Callback when open was clicked in the file menu"""
        self.filebrowser.extension_filter = ["xml", ]
        self.filebrowser.show(self.editor_window)
        while self.filebrowser.return_value is None:
            self.engine.pump()
        if self.filebrowser.return_value:
            self.current_project_file = self.filebrowser.selected_file
            if self.load_project(self.current_project_file):
                maps = self.maps
                if len(maps) > 0:
                    self.load_map(maps.keys()[0])
            else:
                # TODO: Offer to convert to fife-rpg project
                print "%s is not a valid fife-rpg project"
        print "project loaded"

if __name__ == '__main__':
    setting = Setting(app_name="frpg-editor", settings_file="./settings.xml")
    app = EditorApplication(setting)
    app.run()
