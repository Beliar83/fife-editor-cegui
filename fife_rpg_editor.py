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
from fife_rpg import RPGApplicationCEGUI
from fife.extensions.serializers.simplexml import SimpleXMLSerializer
from fife_rpg.components import ComponentManager
from fife_rpg.actions import ActionManager
from fife_rpg.systems import SystemManager
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.game_scene import GameSceneView
from fife_rpg.helpers import DoublePointYaml, DoublePoint3DYaml
# pylint: disable=unused-import
from PyCEGUIOpenGLRenderer import PyCEGUIOpenGLRenderer  # @UnusedImport
# pylint: enable=unused-import

from editor.object_toolbar import ObjectToolbar
from editor.basic_toolbar import BasicToolbar
from editor.editor_scene import EditorController
from editor.property_editor import PropertyEditor
from editor.messagebox import MessageBox


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
        self.view_maps_menu = None

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
        property_editor_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0),
                                             PyCEGUI.UDim(0.825, 0))
        self.property_editor = PropertyEditor(right_area_container)
        self.property_editor.set_size(property_editor_size)
        self.property_editor.add_value_changed_callback(self.cb_value_changed)

        cegui_system.getDefaultGUIContext().setRootWindow(
            self.editor_window)
        self.toolbars = {}
        self.main_container.layout()
        self.selected_object = None

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
        file_close = file_popup.createChild(
            "TaharezLook/MenuItem", "FileClose")
        file_close.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_close)
        file_close.setText(_("Close Project"))
        file_close.setEnabled(False)
        self.file_close = file_close
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
        view_maps.setText(_("Maps"))
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
        self.file_close.setEnabled(False)
        self.reset_maps_menu()

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
        settings.load(filepath)
        if "fife-rpg" in settings.getModuleNameList():
            self.project = settings
            project_dir = str(os.path.split(filepath)[0])
            self.engine.getVFS().addNewSource(project_dir)
            self.project_source = project_dir
            self.load_project_settings()
            try:
                self.load_maps()
            except:  # pylint: disable=bare-except
                pass
            self.file_close.setEnabled(True)
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
        """Callback when cllose was clicked in the file menu"""
        # TODO: Ask to save project/files
        self.clear()

    def cb_new(self, args):
        """Callback when new was clicked in the file menu"""
        message = "Creating a new project is not yet implemented"
        message_box = MessageBox("Not Implemented", message,
                                 MessageBox.BUTTONS.OK)
        message_box.show(self.editor_window)
        while message_box.return_value is None:
            self.engine.pump()

    def cb_open(self, args):
        """Callback when open was clicked in the file menu"""
        # Based on code from unknown-horizons
        try:
            import Tkinter
            import tkFileDialog
            window = Tkinter.Tk()
            window.wm_withdraw()
            selected_file = tkFileDialog.askopenfilename(
                filetypes=[("fife-rpg project", ".xml",)],
                title="Open project")
        except ImportError:
            # tkinter may be missing
            selected_file = ""

        if selected_file:
            self.current_project_file = selected_file
            if self.load_project(self.current_project_file):
                self.reset_maps_menu()
                try:
                    self.load_combined()
                except:  # pylint: disable=bare-except
                    self.load_combined("combined.yaml")
                self.register_components()
                self.register_actions()
                self.register_systems()
                self.register_behaviours()
                self.create_world()
                try:
                    self.world.read_object_db()
                    self.world.import_agent_objects()
                    self.world.load_and_create_entities()
                except:  # pylint: disable=bare-except
                    pass
            else:
                # TODO: Offer to convert to fife-rpg project
                print _("%s is not a valid fife-rpg project")
        print _("project loaded")

    def cb_map_switch(self, args):
        """Callback when a map from the menu was clicked"""
        try:
            self.switch_map(args.window.getUserData())
            self.listbox.resetList()
            layers = self.current_map.fife_map.getLayers()
            for layer in layers:
                item = PyCEGUI.ListboxTextItem(layer.getId())
                item.setSelectionBrushImage("TaharezLook/"
                                            "MultiListSelectionBrush")
                self.listbox.addItem(item)
                item.setSelected(True)

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

if __name__ == '__main__':
    SETTING = Setting(app_name="frpg-editor", settings_file="./settings.xml")
    APP = EditorApplication(SETTING)
    VIEW = GameSceneView(APP)
    CONTROLLER = EditorController(VIEW, APP)
    APP.push_mode(CONTROLLER)
    CONTROLLER.listener.setup_cegui()
    APP.setup()
    APP.run()
