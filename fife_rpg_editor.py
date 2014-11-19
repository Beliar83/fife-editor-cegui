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

import os
import yaml
import PyCEGUI

from fife.extensions.fife_settings import Setting
from fife.fife import MapSaver
from fife_rpg import RPGApplicationCEGUI
from fife.extensions.serializers import ET
from fife.extensions.serializers.simplexml import (SimpleXMLSerializer,
                                                   InvalidFormat)
from fife.extensions.serializers.xml_loader_tools import root_subfile
from fife_rpg.components import ComponentManager
from fife_rpg.components.agent import Agent
from fife_rpg.actions import ActionManager
from fife_rpg.systems import SystemManager
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.game_scene import GameSceneView
from fife_rpg.helpers import DoublePointYaml, DoublePoint3DYaml
from fife_rpg.map import Map as GameMap
# pylint: disable=unused-import
from PyCEGUIOpenGLRenderer import PyCEGUIOpenGLRenderer  # @UnusedImport
# pylint: enable=unused-import

from editor.object_toolbar import ObjectToolbar
from editor.basic_toolbar import BasicToolbar
from editor.editor_scene import EditorController
from editor.property_editor import PropertyEditor
from editor.project_settings import ProjectSettings
from editor.new_project import NewProject


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


class EditorApplication(RPGApplicationCEGUI):

    """The application for the editor"""

    def __init__(self, setting):
        """Constructor

        """
        super(EditorApplication, self).__init__(setting)
        # For IDES
        if False:
            self.editor_window = PyCEGUI.DefaultWindow()
            self.main_container = PyCEGUI.VerticalLayoutContainer()
            self.menubar = PyCEGUI.Menubar()
            self.file_menu = PyCEGUI.MenuItem()
            self.view_menu = PyCEGUI.MenuItem()
            self.toolbar = PyCEGUI.TabControl()
        cegui_system = PyCEGUI.System.getSingleton()
        cegui_system.getDefaultGUIContext().setDefaultTooltipType(
            "TaharezLook/Tooltip")

        self.current_project_file = ""
        self.project = None
        self.project_source = None
        self.project_dir = None
        self.file_close = None
        self.file_save = None
        self.file_p_settings = None
        self.view_maps_menu = None
        self.save_maps_popup = None
        self.save_popup = None

        self.__loadData()
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.editor_window = window_manager.loadLayoutFromFile(
            "editor_window.layout")
        self.main_container = self.editor_window.getChild("MainContainer")
        middle_container = self.main_container.getChild("MiddleContainer")
        self.toolbar = middle_container.getChild("Toolbar")
        self.toolbar.subscribeEvent(PyCEGUI.TabControl.EventSelectionChanged,
                                    self.cb_tb_page_changed)
        self.old_toolbar_index = 0
        right_area = middle_container.getChild("RightArea")
        right_area_container = right_area.createChild(
            "VerticalLayoutContainer",
            "right_area_container")
        layer_box = right_area_container.createChild("TaharezLook/GroupBox",
                                                     "layer_box")
        layer_box.setText("Layers")
        layer_box.setHeight(PyCEGUI.UDim(0.175, 0.0))
        layer_box.setWidth(PyCEGUI.UDim(1.0, 0.0))

        self.listbox = layer_box.createChild("TaharezLook/Listbox", "Listbox")
        self.listbox.setHeight(PyCEGUI.UDim(0.99, 0.0))
        self.listbox.setWidth(PyCEGUI.UDim(0.99, 0.0))
        self.listbox.setMultiselectEnabled(True)
        self.listbox.subscribeEvent(PyCEGUI.Listbox.EventSelectionChanged,
                                    self.cb_layer_selection_changed)
        self.show_agents_check = right_area_container.createChild("TaharezLook"
                                                                  "/Checkbox",
                                                                  "show_agents"
                                                                  )
        self.show_agents_check.setText(_("Show Entities"))
        self.show_agents_check.setSelected(True)
        self.show_agents_check.subscribeEvent(
            PyCEGUI.ToggleButton.EventSelectStateChanged,
            self.cb_show_agent_selection_changed
        )
        property_editor_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0),
                                             PyCEGUI.UDim(0.780, 0))
        self.property_editor = PropertyEditor(right_area_container)
        self.property_editor.set_size(property_editor_size)
        self.property_editor.add_value_changed_callback(self.cb_value_changed)

        cegui_system.getDefaultGUIContext().setRootWindow(
            self.editor_window)
        self.toolbars = {}
        self.main_container.layout()
        self.selected_object = None
        self.import_ref_count = {}
        self.changed_maps = []
        self._project_cleared_callbacks = []
        self.add_map_load_callback(self.cb_map_loaded)
        self.map_entities = None

    def __loadData(self):  # pylint: disable=no-self-use, invalid-name
        """Load gui datafiles"""
        PyCEGUI.ImageManager.getSingleton().loadImageset(
            "TaharezLook.imageset")
        PyCEGUI.SchemeManager.getSingleton().createFromFile(
            "TaharezLook.scheme")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-10.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-12.font")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-14.font")

    def setup(self):
        """Actions that should to be done with an active mode"""
        self.create_menu()
        self.create_toolbars()
        self.clear()

    def create_menu(self):
        """Create the menu items"""
        self.menubar = self.main_container.getChild("Menu")
        # File Menu
        self.file_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "File")
        self.file_menu.setText(_("File"))
        self.file_menu.setVerticalAlignment(
            PyCEGUI.VerticalAlignment.VA_CENTRE)
        file_popup = self.file_menu.createChild("TaharezLook/PopupMenu",
                                                "FilePopup")
        file_new = file_popup.createChild("TaharezLook/MenuItem", "FileNew")
        file_new.setText(_("New Project"))
        file_new.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_new)
        file_open = file_popup.createChild("TaharezLook/MenuItem", "FileOpen")
        file_open.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_open)
        file_open.setText(_("Open Project"))
        file_save = file_popup.createChild("TaharezLook/MenuItem", "FileSave")
        file_save.setText(_("Save") + "  ")
        file_save.setEnabled(False)
        file_save.setAutoPopupTimeout(0.5)
        save_popup = file_save.createChild("TaharezLook/PopupMenu",
                                           "SavePopup")
        self.save_popup = save_popup
        save_all = save_popup.createChild("TaharezLook/MenuItem",
                                          "FileSaveAll")
        save_all.setText(_("All"))
        save_all.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                self.cb_save_all)
        self.file_save = file_save
        save_project = save_popup.createChild("TaharezLook/MenuItem",
                                              "FileSaveProject")
        save_project.setText(_("Project"))
        save_project.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                    self.cb_save_project)
        save_maps = save_popup.createChild("TaharezLook/MenuItem",
                                           "FileSaveMaps")
        save_maps.setText(_("Maps") + "  ")
        save_maps.setAutoPopupTimeout(0.5)
        save_maps_popup = save_maps.createChild("TaharezLook/PopupMenu",
                                                "SaveMapsPopup")
        self.save_maps_popup = save_maps_popup
        file_close = file_popup.createChild(
            "TaharezLook/MenuItem", "FileClose")
        file_close.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_close)
        file_close.setText(_("Close Project"))
        file_close.setEnabled(False)
        self.file_close = file_close
        file_p_settings = file_popup.createChild(
            "TaharezLook/MenuItem", "FilePSettings")
        file_p_settings.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                       self.cb_project_settings)
        file_p_settings.setText(_("Project settings"))
        file_p_settings.setEnabled(False)
        self.file_p_settings = file_p_settings
        file_quit = file_popup.createChild("TaharezLook/MenuItem", "FileQuit")
        file_quit.setText(_("Quit"))
        file_quit.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_quit)
        # View Menu
        self.view_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "View")
        self.view_menu.setText(_("View"))
        view_popup = self.view_menu.createChild("TaharezLook/PopupMenu",
                                                "FilePopup")
        view_maps = view_popup.createChild("TaharezLook/MenuItem", "ViewMaps")
        view_maps.setText(_("Maps") + "  ")
        self.view_maps_menu = view_maps.createChild("TaharezLook/PopupMenu",
                                                    "ViewMapsMenu")
        view_maps.setAutoPopupTimeout(0.5)

    def create_toolbars(self):
        """Creates the editors toolbars"""
        new_toolbar = BasicToolbar(self)
        if new_toolbar.name in self.toolbars:
            raise RuntimeError("Toolbar with name %s already exists" %
                               (new_toolbar.name))
        self.toolbar.setTabHeight(PyCEGUI.UDim(0, -1))
        self.toolbars[new_toolbar.name] = new_toolbar
        gui = new_toolbar.gui
        self.toolbar.addTab(gui)
        new_toolbar = ObjectToolbar(self)
        if new_toolbar.name in self.toolbars:
            raise RuntimeError("Toolbar with name %s already exists" %
                               (new_toolbar.name))
        self.toolbar.setTabHeight(PyCEGUI.UDim(0, -1))
        self.toolbars[new_toolbar.name] = new_toolbar
        gui = new_toolbar.gui
        self.toolbar.addTab(gui)
        self.toolbar.setSelectedTabAtIndex(0)

    def clear(self):
        """Clears all data and restores saved settings"""
        self._maps = {}
        self._current_map = None
        self._components = {}
        self._actions = {}
        self._systems = {}
        self._behaviours = {}
        self.changed_maps = []
        self.listbox.resetList()
        self.map_entities = None
        ComponentManager.clear_components()
        ComponentManager.clear_checkers()
        ActionManager.clear_actions()
        ActionManager.clear_commands()
        SystemManager.clear_systems()
        BehaviourManager.clear_behaviours()
        model = self.engine.getModel()
        model.deleteObjects()
        model.deleteMaps()
        if self.project_source is not None:
            self.engine.getVFS().removeSource(self.project_source)
            self.project_source = None
        self.project_dir = None
        self.project = None
        self.file_save.setEnabled(False)
        self.file_close.setEnabled(False)
        self.file_p_settings.setEnabled(False)
        self.reset_maps_menu()
        for callback in self._project_cleared_callbacks:
            callback()
        self.view_maps_menu.closePopupMenu()
        self.save_popup.closePopupMenu()
        self.save_maps_popup.closePopupMenu()

    def load_project(self, filepath):
        """Tries to load a project

        Args:

            filepath: The path to the project file.

        Returns: True of the project was loaded. False if not."""
        try:
            self.clear()
        except Exception as error:  # pylint: disable=broad-except
            print error
        settings = SimpleXMLSerializer()
        try:
            settings.load(filepath)
        except (InvalidFormat, ET.ParseError):
            return False
        if "fife-rpg" in settings.getModuleNameList():
            self.project = settings
            project_dir = str(os.path.normpath(os.path.split(filepath)[0]))
            self.engine.getVFS().addNewSource(project_dir)
            self.project_source = project_dir
            self.project_dir = project_dir
            self.load_project_settings()
            self.import_ref_count = {}
            self.changed_maps = []
            try:
                old_dir = os.getcwd()
                os.chdir(self.project_dir)
                self.load_maps()
                os.chdir(old_dir)
            except:  # pylint: disable=bare-except
                pass
            self.file_close.setEnabled(True)
            self.file_save.setEnabled(True)
            self.file_p_settings.setEnabled(True)
            return True
        return False

    def reset_maps_menu(self):
        """Recreate the view->maps menu"""
        menu = self.view_maps_menu
        menu.resetList()
        item = menu.createChild("TaharezLook/MenuItem", "NoMap")
        item.setUserData(None)
        item.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_map_switch)
        if self.current_map is None:
            item.setText("+" + _("No Map"))
        else:
            item.setText("   " + _("No Map"))
        self.save_maps_popup.resetList()
        item = self.save_maps_popup.createChild("TaharezLook/MenuItem",
                                                "All")
        item.setText(_("All"))
        item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                            self.cb_save_maps_all)
        for game_map in self.maps.iterkeys():
            item = menu.createChild("TaharezLook/MenuItem", game_map)
            item.setUserData(game_map)
            item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                self.cb_map_switch)
            if (self.current_map is not None and
                    self.current_map.name is game_map):
                item.setText("+" + game_map)
            else:
                item.setText("   " + game_map)
            item = self.save_maps_popup.createChild("TaharezLook/MenuItem",
                                                    game_map)
            item.setText(game_map)
            item.setUserData(game_map)
            item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                self.cb_save_map)

    def load_project_settings(self):
        """Loads the settings file"""
        project_settings = self.project.getAllSettings("fife-rpg")
        del project_settings["ProjectName"]
        for setting, value in project_settings.iteritems():
            self.settings.set("fife-rpg", setting, value)

    def increase_refcount(self, filename, map_name=None):
        """Increase reference count for a file on a map

        Args:

            filename: The filename the reference counter is for

            Map: The map the reference counter is for
        """
        map_name = map_name or self.current_map.name
        if map_name not in self.import_ref_count:
            self.import_ref_count[map_name] = {}
        ref_count = self.import_ref_count[map_name]
        if filename in ref_count:
            ref_count[filename] += 1
        else:
            ref_count[filename] = 1

    def decrease_refcount(self, filename, map_name=None):
        """Decrease reference count for a file on a map

        Args:

            filename: The filename the reference counter is for

            Map: The map the reference counter is for
        """
        map_name = map_name or self.current_map.name
        ref_count = self.import_ref_count[map_name]
        if filename in ref_count:
            ref_count[filename] -= 1
            if ref_count[filename] <= 0:
                del ref_count[filename]

    def save_map(self, map_name=None):
        """Save the current state of the map

        Args:

            map_name: Name of the map to save
        """
        old_tab = self.toolbar.getTabContentsAtIndex(self.old_toolbar_index)
        toolbar = self.toolbars[old_tab.getText()]
        toolbar.deactivate()
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
        map_entities = game_map.entities.copy()
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.new_map = ""
        game_map.update_entities_fife()
        fife_map = game_map.fife_map
        filename = fife_map.getFilename()
        old_dir = os.getcwd()
        os.chdir(self.project_dir)
        import_list = [root_subfile(filename, i) for
                       i in self.import_ref_count[map_name].iterkeys()]
        saver = MapSaver()
        saver.save(fife_map, filename, import_list)
        os.chdir(old_dir)
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.map = map_name
        game_map.update_entities()
        self.update_agents(game_map)
        toolbar.activate()
        if map_name in self.changed_maps:
            self.changed_maps.remove(map_name)

    def add_project_clear_callback(self, callback):
        """Adds a callback function which gets called after the 'clear' method
        was called.

        Args:
            callback: The function to add
        """
        if callback not in self._project_cleared_callbacks:
            self._project_cleared_callbacks.append(callback)

    def remove_project_clear_callback(self, callback):
        """Removes a callback function that got called after the 'clear'
        method was called.

        Args:
            callback: The function to remove
        """
        if callback in self._project_cleared_callbacks:
            index = self._project_cleared_callbacks.index(callback)
            del self._project_cleared_callbacks[index]

    def _pump(self):
        """
        Application pump.

        Derived classes can specialize this for unique behavior.
        This is called every frame.
        """
        for toolbar in self.toolbars.itervalues():
            toolbar.update_contents()

    def cb_quit(self, args):
        """Callback when quit was clicked in the file menu"""
        self.quit()

    def cb_close(self, args):
        """Callback when close was clicked in the file menu"""
        # TODO: Ask to save project/files
        self.clear()

    def cb_new(self, args):
        """Callback when new was clicked in the file menu"""
        import Tkinter
        import tkMessageBox
        window = Tkinter.Tk()
        window.wm_withdraw()
        dialog = NewProject(self)
        values = dialog.show_modal(self.editor_window, self.engine.pump)
        if not dialog.return_value:
            return
        new_project_path = values["ProjectPath"]
        settings_path = os.path.join(new_project_path, "settings-dist.xml")
        if (os.path.exists(settings_path)
                or os.path.exists(os.path.join(new_project_path,
                                               "settings.xml"))):
            answer = tkMessageBox.askyesno(
                _("Project file exists"),
                _("There is already a settings.xml or settings-dist.xml file. "
                  "If you create a new project the settings-dist.xml will "
                  "be overwritten. If you want to convert a project open it "
                  "instead. Continue with creating a new project?"))
            if not answer:
                return
            os.remove(settings_path)
        settings_file = file(settings_path, "w")
        settings_file.write(BASIC_SETTINGS)
        settings_file.close()
        project = SimpleXMLSerializer(settings_path)
        project.load()
        settings = {}
        update_settings(project, settings, values)
        project.save()
        self.try_load_project(settings_path)
        tkMessageBox.showinfo(_("Project created"),
                              _("Project successfully created"))

    def save_all_maps(self):
        """Save the edited status of all maps"""
        for map_name in self.changed_maps:
            self.save_map(map_name)

    def cb_save_all(self, args):
        """Callback when save->all was clicked in the file menu"""
        self.project.save()
        self.save_all_maps()
        self.save_popup.closePopupMenu()

    def cb_save_project(self, args):
        """Callback when save->project was clicked in the file menu"""
        self.project.save()
        self.save_popup.closePopupMenu()

    def cb_save_maps_all(self, args):
        """Callback when save->maps->all was clicked in the file menu"""
        self.save_all_maps()
        self.save_popup.closePopupMenu()
        self.save_maps_popup.closePopupMenu()

    def cb_save_map(self, args):
        """Callback when save->maps->map_name was clicked in the file menu"""
        map_name = args.window.getUserData()
        self.save_map(map_name)
        self.save_popup.closePopupMenu()
        self.save_maps_popup.closePopupMenu()

    def try_load_project(self, file_name):
        """Try to load the specified file as a project

        Args:

            file_name: The file to load
        """
        loaded = self.load_project(file_name)
        if loaded:
            self.current_project_file = file_name
            self.reset_maps_menu()
            old_dir = os.getcwd()
            os.chdir(self.project_dir)
            try:
                try:
                    self.load_combined()
                except:  # pylint: disable=bare-except
                    self.load_combined("combined.yaml")
                try:
                    self.register_components()
                except ValueError:
                    pass
                try:
                    self.register_actions()
                except ValueError:
                    pass
                try:
                    self.register_systems()
                except ValueError:
                    pass
                try:
                    self.register_behaviours()
                except ValueError:
                    pass
                self.create_world()
                try:
                    self.world.read_object_db()
                    self.world.import_agent_objects()
                    self.world.load_and_create_entities()
                except:  # pylint: disable=bare-except
                    pass
            finally:
                os.chdir(old_dir)
            return True
        return False

    def cb_open(self, args):
        """Callback when open was clicked in the file menu"""
        import Tkinter
        import tkMessageBox
        import tkFileDialog
        window = Tkinter.Tk()
        window.wm_withdraw()

        # Based on code from unknown-horizons
        try:
            selected_file = tkFileDialog.askopenfilename(
                filetypes=[("fife-rpg project", ".xml",)],
                title="Open project")
        except ImportError:
            # tkinter may be missing
            selected_file = ""

        if selected_file:
            loaded = self.try_load_project(selected_file)
            if not loaded:
                project = SimpleXMLSerializer(selected_file)
                try:
                    project.load()
                except (InvalidFormat, ET.ParseError):
                    print _("%s is not a valid fife or fife-rpg project" %
                            selected_file)
                    return
                answer = tkMessageBox.askyesno(
                    _("Convert project"),
                    _("%s is not a fife-rpg project. Convert it? " %
                      selected_file))
                if not answer:
                    return
                bak_file = "%s.bak" % selected_file
                project.save(bak_file)
                settings = {}
                settings["ProjectName"] = project.get("FIFE", "WindowTitle",
                                                      "")
                dialog = ProjectSettings(self,
                                         settings,
                                         os.path.dirname(selected_file)
                                         )
                values = dialog.show_modal(self.editor_window,
                                           self.engine.pump)
                if not dialog.return_value:
                    return
                update_settings(project, settings, values)
                project.save()
                if not self.try_load_project(selected_file):
                    tkMessageBox.showerror("Load Error",
                                           "There was a problem loading the "
                                           "converted project. Reverting. "
                                           "Converted file will be stored as "
                                           "original_file.converted")
                    conv_file = "%s.converted" % selected_file
                    if os.path.exists(conv_file):
                        os.remove(conv_file)
                    os.rename(selected_file, conv_file)
                    os.rename(bak_file, selected_file)
                    return
            tkMessageBox.showinfo(_("Project loaded"),
                                  _("Project successfully loaded"))

    def cb_project_settings(self, args):
        """Callback when project settings was clicked in the file menu"""
        settings = self.project.getAllSettings("fife-rpg")
        dialog = ProjectSettings(self,
                                 settings,
                                 self.project_dir
                                 )
        values = dialog.show_modal(self.editor_window, self.engine.pump)
        if not dialog.return_value:
            return
        update_settings(self.project, settings, values)

    def cb_map_switch(self, args):
        """Callback when a map from the menu was clicked"""
        self.view_maps_menu.closePopupMenu()
        if self.map_entities:
            self.show_map_entities(self.current_map.name)
            self.map_entities = None
        if not self.project_dir:
            return
        try:
            old_dir = os.getcwd()
            os.chdir(self.project_dir)
            try:
                self.switch_map(args.window.getUserData())
            finally:
                os.chdir(old_dir)
            self.listbox.resetList()
            if self.current_map:
                layers = self.current_map.fife_map.getLayers()
                for layer in layers:
                    item = PyCEGUI.ListboxTextItem(layer.getId())
                    item.setSelectionBrushImage("TaharezLook/"
                                                "MultiListSelectionBrush")
                    self.listbox.addItem(item)
                    item.setSelected(True)
                if not self.show_agents_check.isSelected():
                    self.hide_map_entities(self.current_map.name)
        except Exception as error:
            print error
            raise
        self.reset_maps_menu()

    def cb_tb_page_changed(self, args):
        """Called then the toolbar page gets changed"""
        old_tab = self.toolbar.getTabContentsAtIndex(self.old_toolbar_index)
        old_toolbar = self.toolbars[old_tab.getText()]
        old_toolbar.deactivate()
        index = self.toolbar.getSelectedTabIndex()
        new_tab = self.toolbar.getTabContentsAtIndex(index)
        new_toolbar = self.toolbars[new_tab.getText()]
        new_toolbar.activate()
        self.old_toolbar_index = index

    def cb_layer_selection_changed(self, args):
        """Called when the layer selection in the listbox changed"""
        layers = self.current_map.fife_map.getLayers()
        for layer in layers:
            listitem = self.listbox.findItemWithText(layer.getId(), None)
            is_selected = listitem.isSelected()
            layer.setInstancesVisible(is_selected)

    def update_property_editor(self):
        """Update the property editor"""
        property_editor = self.property_editor
        property_editor.clear_properties()
        identifier = self.selected_object.getId()
        world = self.world
        components = ComponentManager.get_components()
        if world.is_identifier_used(identifier):
            entity = world.get_entity(identifier)
            for comp_name, component in components.iteritems():
                com_data = getattr(entity, comp_name)
                if com_data:
                    for field in component.saveable_fields:
                        value = getattr(com_data, field)
                        if isinstance(value, DoublePointYaml):
                            pos = (value.x, value.y)
                            property_editor.add_property(
                                comp_name, field,
                                ("point", pos))
                        elif isinstance(value, DoublePoint3DYaml):
                            pos = (value.x, value.y, value.z)
                            property_editor.add_property(
                                comp_name, field,
                                ("point3d", pos))
                        else:
                            str_val = yaml.dump(value).split('\n')[0]
                            property_editor.add_property(
                                comp_name, field,
                                ("text", str_val))
        else:
            property_editor.add_property(
                "Instance", "Identifier",
                ("text", identifier))
            property_editor.add_property(
                "Instance", "CostId",
                ("text", self.selected_object.getCostId()))
            property_editor.add_property(
                "Instance", "Cost",
                ("text", self.selected_object.getCost()))
            property_editor.add_property(
                "Instance", "Blocking",
                ("check", self.selected_object.isBlocking()))
            property_editor.add_property(
                "Instance", "Rotation",
                ("text", self.selected_object.getRotation()))
            visual = self.selected_object.get2dGfxVisual()
            property_editor.add_property(
                "Instance", "StackPosition",
                ("text",  visual.getStackPosition()))

    def set_selected_object(self, obj):
        """Sets the selected object of the editor

        Args:

            obj: The new object
        """
        self.selected_object = obj
        self.update_property_editor()

    def cb_value_changed(self, section, property_name, value):
        """Called when the value of a property changed

        Args:

            section: The section of the property

            property_name: The name of the property

            value: The new value of the property
        """
        identifier = self.selected_object.getId()
        world = self.world
        if world.is_identifier_used(identifier):
            entity = world.get_entity(identifier)
            com_data = getattr(entity, section)
            try:
                if isinstance(value, basestring):
                    value = yaml.load(value)
                setattr(com_data, property_name, value)
                self.update_agents(self.current_map)
            except (ValueError, yaml.parser.ParserError):
                pass
        else:
            if section != "Instance":
                return
            if property_name == "Identifier":
                self.selected_object.setId(value)
            elif property_name == "CostId":
                cur_cost = self.selected_object.getCost()
                try:
                    value = value.encode()
                    self.selected_object.setCost(value, cur_cost)
                except UnicodeEncodeError:
                    print "The CostId has to be an ascii value"
            elif property_name == "Cost":
                cur_cost_id = self.selected_object.getCostId()
                try:
                    self.selected_object.setCost(cur_cost_id, float(value))
                except ValueError:
                    pass
            elif property_name == "Blocking":
                self.selected_object.setBlocking(value)
            elif property_name == "Rotation":
                try:
                    self.selected_object.setRotation(int(value))
                except ValueError:
                    pass
            elif property_name == "StackPosition":
                try:
                    visual = self.selected_object.get2dGfxVisual()
                    visual.setStackPosition(int(value))
                except ValueError:
                    pass
        self.update_property_editor()

    def cb_map_loaded(self, game_map):
        """Callback for when a map was loaded"""

        fife_map = game_map.fife_map
        for layer in fife_map.getLayers():
            for instance in layer.getInstances():
                filename = instance.getObject().getFilename()
                map_name = game_map.name
                self.increase_refcount(filename, map_name)

    def hide_map_entities(self, map_name):
        """Hides the entities of all maps

        Args:

            map_name: The name of the map
        """
        game_map = self.maps[map_name]
        is_map_instance = isinstance(game_map, GameMap)
        if not is_map_instance:
            return
        map_entities = game_map.entities.copy()
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.new_map = ""
        self.map_entities = map_entities
        game_map.update_entities_fife()

    def show_map_entities(self, map_name):
        """Unhide the entities of the given map

        Args:

            map_name: The name of the map
        """
        game_map = self.maps[map_name]
        is_map_instance = isinstance(game_map, GameMap)
        if not is_map_instance:
            return
        map_entities = self.map_entities
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.map = map_name
        game_map.update_entities()
        self.update_agents(game_map)

    def cb_show_agent_selection_changed(self, args):
        """Called when the "Show Entities" checkbox was changed"""
        if self.current_map is None:
            return
        if self.show_agents_check.isSelected():
            self.show_map_entities(self.current_map.name)
        else:
            self.hide_map_entities(self.current_map.name)


def update_settings(project, settings, values):
    """Update the fife-rpg settings of a project

    Args:
        project: The project to update

        settings: The old fife-rpg settings

        values: The new fife-rpg settings
    """
    for key, value in values.iteritems():
        project.set("fife-rpg", key, value)

    ignore_keys = "Actions", "Behaviours", "Systems", "Components"
    deleted_keys = [x for x in settings.keys() if
                    x not in values.keys() and x not in ignore_keys]
    for key in deleted_keys:
        project.remove("fife-rpg", key)


if __name__ == '__main__':
    SETTING = Setting(app_name="frpg-editor", settings_file="./settings.xml")
    APP = EditorApplication(SETTING)
    VIEW = GameSceneView(APP)
    CONTROLLER = EditorController(VIEW, APP)
    APP.push_mode(CONTROLLER)
    CONTROLLER.listener.setup_cegui()
    APP.setup()
    APP.run()
