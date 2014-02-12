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

import PyCEGUI
from fife import fife
from fife.extensions.fife_settings import Setting
from fife_rpg import RPGApplicationCEGUI

class EditorApplication(RPGApplicationCEGUI):


    def __init__(self, setting):
        #For IDES
        if False:
            self.editor_window = PyCEGUI.DefaultWindow()
            self.main_container = PyCEGUI.VerticalLayoutContainer()
            self.menubar = PyCEGUI.Menubar()
            self.file_menu = PyCEGUI.MenuItem()
        RPGApplicationCEGUI.__init__(self, setting)

        self.__loadData()
        self.editor_window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
                                                                    "editor_window.layout")
        self.main_container = self.editor_window.getChild("MainContainer")
        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(self.editor_window)
        self.create_menu()


    def __loadData(self):
        """Load gui datafiles"""
        PyCEGUI.ImageManager.getSingleton().loadImageset("WindowsLook.imageset")
        PyCEGUI.SchemeManager.getSingleton().createFromFile("WindowsLook.scheme")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-10.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-12.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-14.font")


    def create_menu(self):
        self.menubar = self.main_container.getChild("Menu")
        self.file_menu = self.menubar.createChild("WindowsLook/MenuItem", "File")
        self.file_menu.setText(_("File"))
        self.file_menu.setVerticalAlignment(PyCEGUI.VerticalAlignment.VA_CENTRE)
        file_popup = self.file_menu.createChild("WindowsLook/PopupMenu", "FilePopup")
        file_new = file_popup.createChild("WindowsLook/MenuItem", "FileNew")
        file_new.setText(_("New"))
        file_open = file_popup.createChild("WindowsLook/MenuItem", "FileOpen")
        file_open.setText(_("Open"))
        file_quit = file_popup.createChild("WindowsLook/MenuItem", "FileQuit")
        file_quit.setText(_("Quit"))
        file_quit.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_quit)

    def cb_quit(self, args):
        self.quit()

if __name__ == '__main__':
    setting = Setting(app_name="frpg-editor", settings_file="./settings.xml")
    app = EditorApplication(setting)
    app.run()
