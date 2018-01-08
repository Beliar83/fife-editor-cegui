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

""" Contains the main file for the fife-rpg editor

.. module:: fife_rpg_editor
    :synopsis: Contains the main file for the fffe-rpg editor

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import next
from builtins import open
import os
import sys
import shutil
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import yaml
# pylint: disable=unused-import
import PyCEGUI  # @UnusedImport # PyCEGUI won't work otherwise (on windows)
import PyCEGUIOpenGLRenderer  # @UnusedImport
# pylint: enable=unused-import

from fife.extensions.fife_settings import Setting
from fife.fife import InstanceRenderer
from fife.fife import MapSaver
from fife.fife import Map as FifeMap
from fife.fife import MapChangeListener

from fife_rpg import RPGApplicationCEGUI
from fife.extensions.serializers import ET
from fife.extensions.serializers.simplexml import (SimpleXMLSerializer,
                                                   InvalidFormat)
from fife.extensions.serializers.xml_loader_tools import root_subfile
from fife_rpg.game_scene import GameSceneView
from fife_rpg import helpers
from fife_rpg import GameMap

from editor.editor_gui import EditorGui
from editor.editor import Editor
from editor.editor_scene import EditorController

BASIC_SETTINGS = """<?xml version='1.0' encoding='UTF-8'?>
<Settings>
    <Module name="FIFE">
        <Setting name="FullScreen" type="bool"> False </Setting>
        <Setting name="PlaySounds" type="bool"> True </Setting>
        <Setting name="RenderBackend" type="str"> OpenGL </Setting>
        <Setting name="ScreenResolution" type="str">1024x768</Setting>
        <Setting name="Lighting" type="int"> 0 </Setting>
    </Module>
</Settings>
"""


class EditorMapChangeListener(MapChangeListener):

    """Listens to changes on maps"""

    def __init__(self, app):
        MapChangeListener.__init__(self)
        self.app = app

    # pylint: disable=arguments-differ
    def onMapChanged(self, fife_map, changed_layers):
        """Called when something on a map was changed

        Args:

            fife_map: The map that was changed

            changed_layers: The layers that where changed
        """
        pass

    def onLayerCreate(self, fife_map, layer):
        """Called when a layer was created.

        Args:

            fife_map: The map where the layer was created.

            layer: The layer that was created
        """
        pass

    def onLayerDelete(self, fife_map, layer):
        """Called when a layer was deleted.

        Args:

            fife_map: The map the layer was deleted from

            layer: The layer that was deleted
        """
        pass
    # pylint: enable=arguments-differ


class EditorApplication(RPGApplicationCEGUI):

    """The application for the editor"""

    def __init__(self, setting):
        """Constructor

        """
        super(EditorApplication, self).__init__(setting)
        self.editor_settings = self.settings.getSettingsFromFile("fife-rpg")
        # For IDES
        if False:
            self.editor_gui = EditorGui(self)

        self.editor_gui = None

        self.changed_maps = []
        self.add_map_load_callback(self.cb_map_loaded)
        self._objects_imported_callbacks = []
        self.selected_object = None
        self.editor = Editor(self.engine)
        self.editor_gui = EditorGui(self)
        self.current_dialog = None

    def setup(self):
        """Actions that should to be done with an active mode"""
        self.editor_gui.create_menu()
        self.editor_gui.create_toolbars()
        self.clear()

    def switch_map(self, map_name):
        """Switches to the given map.

        Args:
            name: The name of the map
        """
        try:
            old_dir = os.getcwd()
            try:
                RPGApplicationCEGUI.switch_map(self, map_name)
            finally:
                    os.chdir(old_dir)
            self.editor_gui.listbox.resetList()
            if self.current_map:
                self.editor_gui.update_layerlist()
        except Exception as error:  # pylint: disable=broad-except
            import tkinter.messagebox
            tkinter.messagebox.showerror("Can't change map",
                                   "The following error was raised when "
                                   "trying to switch the map: %s" % error)
            self.switch_map(None)

    def objects_imported(self):
        """Should be called when an object was imported"""
        for callback in self._objects_imported_callbacks:
            callback()

    def clear(self):
        """Clears all data and restores saved settings"""
        self._maps = {}
        self._current_map = None
        self.changed_maps = []
        self.editor_gui.reset_layerlist()
        self.set_selected_object(None)
        self.editor.delete_maps()
        self.editor.delete_objects()
        self.create_world()

    def close_map(self, map_name=None):
        """Close a map

        Args:

            map_name: Name of the map to close
        """
        if map_name:
            if map_name in self.maps:
                game_map = self.maps[map_name]
            else:
                return
        else:
            if self.current_map:
                game_map = self.current_map
                map_name = game_map.name
            else:
                return
        self.switch_map(None)
        self.editor.delete_map(game_map.fife_map)
        del self._maps[map_name]

    def save_map(self, map_name=None):
        """Save the current state of a map

        Args:

            map_name: Name of the map to save
        """
        self.editor_gui.current_toolbar.deactivate()
        if map_name:
            if map_name in self.maps:
                game_map = self.maps[map_name]
            else:
                return
        else:
            if self.current_map:
                game_map = self.current_map
                map_name = game_map.name
            else:
                return
        if not isinstance(game_map, GameMap):
            return
        fife_map = game_map.fife_map
        filename = fife_map.getFilename()
        if not filename:
            import tkinter.filedialog
            import tkinter.messagebox
            # Based on code from unknown-horizons
            try:
                filename = tkinter.filedialog.asksaveasfilename(
                    filetypes=[("fife map", ".xml",)],
                    title="Save Map")
            except ImportError:
                # tkinter may be missing5555
                filename = ""
        fife_map.setFilename(filename)


        try:
            os.makedirs(os.path.dirname(filename))
        except os.error:
            pass

        old_dir = os.getcwd()
        import_list = [root_subfile(filename, i) for
                       i in self.editor.get_import_list(fife_map.getId())]
        saver = MapSaver()
        saver.save(fife_map, filename, import_list)
        os.chdir(old_dir)
        self.editor_gui.current_toolbar.activate()
        if map_name in self.changed_maps:
            self.changed_maps.remove(map_name)

    def add_objects_imported_callback(self, callback):
        """Adds a callback function which gets called after objects where
        imported.

        Args:
            callback: The function to add
        """
        if callback not in self._objects_imported_callbacks:
            self._objects_imported_callbacks.append(callback)

    def remove_objects_imported_callback(self, callback):
        """Removes a callback function that got called after objects where
        imported.

        Args:
            callback: The function to remove
        """
        if callback in self._objects_imported_callbacks:
            index = self._objects_imported_callbacks.index(callback)
            del self._objects_imported_callbacks[index]

    def _pump(self):
        """
        Application pump.

        Derived classes can specialize this for unique behavior.
        This is called every frame.
        """
        self.editor_gui.update_toolbar_contents()
        if self.world:
            try:
                self.world.pump(0)
            except Exception:  # pylint: disable=broad-except
                pass

    def save_all_maps(self):
        """Save the edited status of all maps"""
        for map_name in self.changed_maps:
            self.save_map(map_name)

    def highlight_selected_object(self):
        """Adds an outline to the currently selected object"""
        if self.selected_object is None:
            return
        game_map = self.current_map
        if game_map:
            renderer = InstanceRenderer.getInstance(game_map.camera)
            renderer.addOutlined(self.selected_object, 255, 255, 0, 1)

    def reset_selected_hightlight(self):
        """Removes the outline to the currently selected object"""
        if self.selected_object is None:
            return
        game_map = self.current_map
        if game_map:
            renderer = InstanceRenderer.getInstance(game_map.camera)
            renderer.removeOutlined(self.selected_object)

    def set_selected_object(self, obj):
        """Sets the selected object of the editor

        Args:

            obj: The new object
        """
        self.reset_selected_hightlight()
        self.selected_object = obj
        self.highlight_selected_object()
        self.editor_gui.update_property_editor()

    def cb_map_loaded(self, game_map):
        """Callback for when a map was loaded"""

        fife_map = game_map.fife_map
        for layer in self.editor.get_layers(fife_map):
            for instance in layer.getInstances():
                filename = instance.getObject().getFilename()
                map_name = fife_map.getId()
                self.editor.increase_refcount(filename, map_name)

    def quit(self):
        """
        Quit the application. Really!
        """
        if self.current_dialog:
            return
        if self.editor_gui.ask_save_changed():
            self.quitRequested = True


if __name__ == '__main__':
    SETTING = Setting(app_name="frpg-editor", settings_file="./settings.xml")
    APP = EditorApplication(SETTING)
    VIEW = GameSceneView(APP)
    CONTROLLER = EditorController(VIEW, APP)
    APP.push_mode(CONTROLLER)
    CONTROLLER.listener.setup_cegui()
    APP.setup()
    APP.run()
