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

""" Module for creating and handling the editor GUI

.. module:: editor_gui
    :synopsis: Creating and handling the editor menu

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import print_function

from future import standard_library
from future.utils import iteritems
standard_library.install_aliases()
from builtins import str
from builtins import object
import os
import PyCEGUI
import yaml

from fife.fife import Rect
from fife.fife import InstanceRenderer
from fife.extensions.serializers.simplexml import (SimpleXMLSerializer,
                                                   InvalidFormat)
from fife.extensions.serializers import ET
from fife_rpg import GameMap
from fife_rpg.components import ComponentManager
from fife_rpg.components.agent import Agent
from fife_rpg.components.general import General
from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.behaviours.base import Base as BaseBehaviour

from .edit_map import MapOptions
from .edit_layer import LayerOptions
from .edit_camera import CameraOptions
from .object_toolbar import ObjectToolbar
from .basic_toolbar import BasicToolbar
from .property_editor import PropertyEditor
from . import properties

class EditorGui(object):

    """Creates and handles the editor GUI"""

    def __init__(self, app):
        if False:  # Only for IDEs
            from fife_editor import EditorApplication
            from .editor import Editor
            self.app = EditorApplication(None)
            self.editor = Editor(None)
            self.editor_window = PyCEGUI.DefaultWindow()
            self.main_container = PyCEGUI.VerticalLayoutContainer()
            self.menubar = PyCEGUI.Menubar()
            self.toolbar = PyCEGUI.TabControl()
            self.menubar = PyCEGUI.Menubar()
            self.file_menu = PyCEGUI.MenuItem()
            self.view_menu = PyCEGUI.MenuItem()
            self.edit_menu = PyCEGUI.MenuItem()
        self.menubar = None
        self.file_menu = None
        self.file_close = None
        self.file_save = None
        self.save_maps = None
        self.edit_menu = None
        self.view_menu = None
        self.view_maps_menu = None
        self.save_maps_popup = None
        self.save_popup = None
        self.file_import = None
        self.import_popup = None
        self.edit_add = None
        self.add_popup = None

        self.app = app
        self.editor = app.editor

        import tkinter
        self.window = tkinter.Tk()
        self.window.wm_withdraw()
        self.window.attributes("-topmost", 1)

        cegui_system = PyCEGUI.System.getSingleton()
        cegui_system.getDefaultGUIContext().setDefaultTooltipType(
            "TaharezLook/Tooltip")
        self.load_data()
        window_manager = PyCEGUI.WindowManager.getSingleton()
        self.editor_window = window_manager.loadLayoutFromFile(
            "editor_window.layout")
        self.main_container = self.editor_window.getChild("MainContainer")
        middle_container = self.main_container.getChild("MiddleContainer")
        self.toolbar = middle_container.getChild("Toolbar")
        self.toolbar.subscribeEvent(PyCEGUI.TabControl.EventSelectionChanged,
                                    self.cb_tb_page_changed)
        self.cur_toolbar_index = 0
        right_area = middle_container.getChild("RightArea")
        right_area_container = right_area.createChild(
            "VerticalLayoutContainer",
            "right_area_container")
        layer_box = right_area_container.createChild("TaharezLook/GroupBox",
                                                     "layer_box")
        layer_box.setText("Layers")
        layer_box.setHeight(PyCEGUI.UDim(0.275, 0.0))
        layer_box.setWidth(PyCEGUI.UDim(1.0, 0.0))
        layer_box_layout = layer_box.createChild("VerticalLayoutContainer",
                                                 "layer_box_layout")

        self.listbox = layer_box_layout.createChild("TaharezLook/ItemListbox",
                                                    "Listbox")

        self.listbox.setHeight(PyCEGUI.UDim(0.79, 0.0))
        self.listbox.setWidth(PyCEGUI.UDim(0.99, 0.0))
        self.listbox.subscribeEvent(PyCEGUI.ItemListbox.EventSelectionChanged,
                                    self.cb_layer_box_changed)
        self.listbox.subscribeEvent(
            PyCEGUI.ItemListBase.EventListContentsChanged,
            self.cb_layer_box_changed)

        layer_edit_layout = layer_box_layout.createChild("HorizontalLayout"
                                                         "Container",
                                                         "layer_edit_layout")
        layer_edit_layout.setHeight(PyCEGUI.UDim(0.15, 0.0))
        layer_edit_layout.setWidth(PyCEGUI.UDim(0.99, 0.0))
        add_layer_button = layer_edit_layout.createChild("TaharezLook/Button",
                                                         "add_layer")
        add_layer_button.setWidth(PyCEGUI.UDim(0.25, 0.0))
        add_layer_button.setText("+")
        add_layer_button.setEnabled(False)
        add_layer_button.subscribeEvent(PyCEGUI.PushButton.EventClicked,
                                        self.cb_add_layer_activated)
        self.add_layer_button = add_layer_button
        delete_layer_button = layer_edit_layout.createChild("TaharezLook"
                                                            "/Button",
                                                            "delete_layer")
        delete_layer_button.setWidth(PyCEGUI.UDim(0.25, 0.0))
        delete_layer_button.setText("-")
        delete_layer_button.setEnabled(False)
        delete_layer_button.subscribeEvent(PyCEGUI.PushButton.EventClicked,
                                           self.cb_delete_layer_activated)
        self.delete_layer_button = delete_layer_button
        edit_layer_button = layer_edit_layout.createChild("TaharezLook/Button",
                                                          "edit_layer")
        edit_layer_button.setWidth(PyCEGUI.UDim(0.5, 0.0))
        edit_layer_button.setText(_("Options"))
        edit_layer_button.setEnabled(False)
        edit_layer_button.subscribeEvent(PyCEGUI.PushButton.EventClicked,
                                         self.cb_edit_layer_activated)

        self.edit_layer_button = edit_layer_button
        property_editor_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0),
                                             PyCEGUI.UDim(0.68, 0))
        self.property_editor = PropertyEditor(right_area_container, self.app)
        self.property_editor.set_size(property_editor_size)
        self.property_editor.add_property_type(properties.PointProperty)
        self.property_editor.add_property_type(properties.Point3DProperty)
        self.property_editor.add_property_type(properties.ComboProperty)
        self.property_editor.add_property_type(properties.ToggleProperty)
        self.property_editor.add_property_type(properties.TextProperty)
        self.property_editor.add_property_type(properties.ListProperty)
        self.property_editor.add_property_type(properties.SetProperty)
        self.property_editor.add_property_type(properties.DictProperty)
        self.property_editor.add_property_type(properties.NumberProperty)
        self.property_editor.add_value_changed_callback(self.cb_value_changed)

        self.previous_object = None

        cegui_system.getDefaultGUIContext().setRootWindow(
            self.editor_window)
        self.toolbars = {}
        self.main_container.layout()
        self.app.add_map_switch_callback(self.cb_map_switched)

    @property
    def selected_layer(self):
        """Returns the currently selected layer"""
        selected = self.listbox.getFirstSelectedItem()
        if selected is not None:
            return selected.getText()
        return None

    @property
    def current_toolbar(self):
        """Returns the currently active toolbar"""
        cur_tab = self.toolbar.getTabContentsAtIndex(self.cur_toolbar_index)
        return self.toolbars[cur_tab.getText()]

    def load_data(self):  # pylint: disable=no-self-use
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
        self.menubar.subscribeEvent(PyCEGUI.Window.EventDeactivated,
                                    self.cb_menu_leave)
        # File Menu
        self.file_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "File")
        self.file_menu.setText(_("File"))
        self.file_menu.setVerticalAlignment(
            PyCEGUI.VerticalAlignment.VA_CENTRE)
        file_popup = self.file_menu.createChild("TaharezLook/PopupMenu",
                                                "FilePopup")
        file_new = file_popup.createChild("TaharezLook/MenuItem", "FileNew")
        file_new.setText(_("New"))
        file_new_popup = file_new.createChild("TaharezLook/PopupMenu",
                                                "FileNewPopup")

        file_new_map =  file_new_popup.createChild("TaharezLook/MenuItem",
                                                   "FileNewMap")
        file_new_map.setText(_("New Map"))
        file_new_map.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                      self.cb_add_map)
        file_new_map.setAutoPopupTimeout(0.5)
        file_open = file_popup.createChild("TaharezLook/MenuItem", "FileOpen")
        file_open.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_open)
        file_open.setText(_("Open"))
        file_open.setAutoPopupTimeout(0.5)
        file_import = file_popup.createChild(
            "TaharezLook/MenuItem", "FileImport")
        file_import.setText(_("Import") + "  ")
        file_import.setEnabled(False)
        file_import.setAutoPopupTimeout(0.5)
        self.file_import = file_import
        import_popup = file_import.createChild("TaharezLook/PopupMenu",
                                               "ImportPopup")
        self.import_popup = import_popup
        import_objects = import_popup.createChild("TaharezLook/MenuItem",
                                                  "FileImportObjects")
        import_objects.setText(_("Objects"))
        import_objects.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                      self.cb_import_objects)
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
        save_all.setAutoPopupTimeout(0.5)
        self.file_save = file_save
        save_maps = save_popup.createChild("TaharezLook/MenuItem",
                                           "FileSaveMaps")
        save_maps.setText(_("Maps") + "  ")
        save_maps.setAutoPopupTimeout(0.5)
        save_maps.setEnabled(False)
        self.save_maps = save_maps
        save_maps_popup = save_maps.createChild("TaharezLook/PopupMenu",
                                                "SaveMapsPopup")
        self.save_maps_popup = save_maps_popup
        file_close = file_popup.createChild(
            "TaharezLook/MenuItem", "FileClose")
        file_close.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_close)
        file_close.setText(_("Close Map"))
        file_close.setEnabled(False)
        file_close.setAutoPopupTimeout(0.5)
        self.file_close = file_close
        file_quit = file_popup.createChild("TaharezLook/MenuItem", "FileQuit")
        file_quit.setText(_("Quit"))
        file_quit.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_quit)
        file_quit.setAutoPopupTimeout(0.5)

        # Edit Menu

        self.edit_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "Edit")
        self.edit_menu.setText(_("Edit"))
        edit_popup = self.edit_menu.createChild("TaharezLook/PopupMenu",
                                                "EditPopup")
        edit_add = edit_popup.createChild("TaharezLook/MenuItem",
                                          "Edit/Add")
        edit_add.setText(_("Add") + "  ")
        edit_add.setAutoPopupTimeout(0.5)
        add_popup = edit_add.createChild("TaharezLook/PopupMenu",
                                         "Edit/AddPopup")
        self.add_popup = add_popup
        add_map = add_popup.createChild("TaharezLook/MenuItem",
                                        "Edit/Add/Map")
        add_map.setText(_("Map"))
        add_map.setAutoPopupTimeout(0.5)
        add_map.subscribeEvent(PyCEGUI.MenuItem.EventClicked, self.cb_add_map)

        self.edit_add = edit_add
        self.edit_add.setEnabled(False)



        # View Menu
        self.view_menu = self.menubar.createChild("TaharezLook/MenuItem",
                                                  "View")
        self.view_menu.setText(_("View"))
        view_popup = self.view_menu.createChild("TaharezLook/PopupMenu",
                                                "ViewPopup")
        view_maps = view_popup.createChild("TaharezLook/MenuItem", "ViewMaps")
        view_maps.setText(_("Maps") + "  ")
        self.view_maps_menu = view_maps.createChild("TaharezLook/PopupMenu",
                                                    "ViewMapsMenu")
        view_maps.setAutoPopupTimeout(0.5)

    def reset_layerlist(self):
        """Resets the layerlist to be empty"""
        self.listbox.resetList()

    def update_layerlist(self):
        """Update the layerlist to the layers of the current map"""
        layers = self.app.editor.get_layers(self.app.current_map.fife_map)
        for layer in layers:
            layer_name = layer.getId()
            item = self.listbox.createChild(
                "TaharezLook/CheckListboxItem",
                "layer_%s" % layer_name)
            checkbox = item.getChild(0)
            checkbox.setSelected(True)
            # pylint:disable=cell-var-from-loop
            checkbox.subscribeEvent(
                PyCEGUI.ToggleButton.EventSelectStateChanged,
                lambda args, layer=layer_name:
                    self.cb_layer_checkbox_changed(args, layer))
            # pylint:enable=cell-var-from-loop
            item.setText(layer_name)
        self.listbox.performChildWindowLayout()

    def create_toolbars(self):
        """Creates the editors toolbars"""
        new_toolbar = BasicToolbar(self.app)
        if new_toolbar.name in self.toolbars:
            raise RuntimeError("Toolbar with name %s already exists" %
                               (new_toolbar.name))
        self.toolbar.setTabHeight(PyCEGUI.UDim(0, -1))
        self.toolbars[new_toolbar.name] = new_toolbar
        gui = new_toolbar.gui
        self.toolbar.addTab(gui)
        new_toolbar = ObjectToolbar(self.app)
        if new_toolbar.name in self.toolbars:
            raise RuntimeError("Toolbar with name %s already exists" %
                               (new_toolbar.name))
        self.toolbar.setTabHeight(PyCEGUI.UDim(0, -1))
        self.toolbars[new_toolbar.name] = new_toolbar
        gui = new_toolbar.gui
        self.toolbar.addTab(gui)
        self.toolbar.setSelectedTabAtIndex(0)

    def update_toolbar_contents(self):
        """Updates the contents of the toolbars"""
        for toolbar in self.toolbars.values():
            toolbar.update_contents()

    def update_property_editor(self):
        """Update the properties editor"""
        unremovable_components = (General.registered_as, )

        property_editor = self.property_editor
        if not self.app.selected_object == self.previous_object:
            property_editor.clear_properties()
        self.previous_object = self.app.selected_object
        if self.app.selected_object is None:
            return
        identifier = self.app.selected_object.getId()
        world = self.app.world
        property_editor.set_property(
            "Instance", "Identifier",
            [identifier])
        property_editor.set_property(
            "Instance", "CostId",
            [str(self.app.selected_object.getCostId())])
        property_editor.set_property(
            "Instance", "Cost",
            [self.app.selected_object.getCost()])
        property_editor.set_property(
            "Instance", "Blocking",
            [self.app.selected_object.isBlocking()])
        property_editor.set_property(
            "Instance", "Rotation",
            [self.app.selected_object.getRotation()])
        visual = self.app.selected_object.get2dGfxVisual()
        property_editor.set_property(
            "Instance", "StackPosition",
            [str(visual.getStackPosition())])
        property_editor.enable_add = False
        property_editor.add_callback = None
        property_editor.update_widgets()

    def reset_maps_menu(self):
        """Recreate the view->maps menu"""
        menu = self.view_maps_menu
        menu.resetList()
        item = menu.createChild("TaharezLook/MenuItem", "NoMap")
        item.setUserData(None)
        item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                            self.cb_map_switch_clicked)
        if self.app.current_map is None:
            item.setText("+" + _("No Map"))
        else:
            item.setText("   " + _("No Map"))
        self.save_maps_popup.resetList()
        item = self.save_maps_popup.createChild("TaharezLook/MenuItem",
                                                "All")
        item.setText(_("All"))
        item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                            self.cb_save_maps_all)
        for identifier, game_map in self.app.maps.items():
            map_name = game_map.view_name
            item = menu.createChild("TaharezLook/MenuItem", map_name)
            item.setUserData(identifier)
            item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                self.cb_map_switch_clicked)
            if (self.app.current_map is not None and
                    self.app.current_map.name == map_name):
                item.setText("+" + map_name)
            else:
                item.setText("   " + map_name)
            item = self.save_maps_popup.createChild("TaharezLook/MenuItem",
                                                    identifier)
            item.setText(map_name)
            item.setUserData(identifier)
            item.subscribeEvent(PyCEGUI.MenuItem.EventClicked,
                                self.cb_save_map)

    def cb_tb_page_changed(self, args):
        """Called then the toolbar page gets changed"""
        old_tab = self.toolbar.getTabContentsAtIndex(self.cur_toolbar_index)
        old_toolbar = self.toolbars[old_tab.getText()]
        old_toolbar.deactivate()
        index = self.toolbar.getSelectedTabIndex()
        new_tab = self.toolbar.getTabContentsAtIndex(index)
        new_toolbar = self.toolbars[new_tab.getText()]
        new_toolbar.activate()
        self.cur_toolbar_index = index

    def cb_layer_checkbox_changed(self, args, layer_name):
        """Called when a layer checkbox state was changed

        Args:
            layer_name: Name of the layer the checkbox is for
        """
        layer = self.app.current_map.fife_map.getLayer(layer_name)
        is_selected = args.window.isSelected()
        layer.setInstancesVisible(is_selected)

    def cb_quit(self, args):
        """Callback when quit was clicked in the file menu"""
        self.app.quit()

    def ask_save_changed(self):
        """Ask to save changed files.

        Returns:
            True if no dialog was cancelled. False if a dialog was cancelled
        """
        import tkinter.messagebox
        if self.app.changed_maps:
            message = _("One or more maps have changed. Save ALL maps?")
            answer = tkinter.messagebox.askyesnocancel("Save?", message)
            if answer is True:
                self.app.save_all_maps()
            elif answer is False:
                for changed_map in self.app.changed_maps:
                    message = _("The map {map_name} has changed. "
                                "Save?").format(map_name=changed_map)
                    answer = tkinter.messagebox.askyesnocancel("Save?",
                                                         message)
                    if answer is True:
                        self.app.save_map(changed_map)
                    elif answer is None:
                        return False
            elif answer is None:
                return False
        return True

    def cb_close(self, args):
        """Callback when close was clicked in the file menu"""
        if self.app.current_map is None:
            return
        if self.app.current_map.name in self.app.changed_maps:
            import tkinter.filedialog
            import tkinter.messagebox
            message = _("The map {map_name} has changed. "
                        "Save?").format(map_name=self.app.current_map.name)
            answer = tkinter.messagebox.askyesnocancel("Save?",
                                                       message)
            if answer is None:
                return
            if answer is True:
                self.app.save_map()
        self.app.close_map()
        self.reset_maps_menu()

    def save_all(self):
        """Save all maps"""
        self.app.save_all_maps()

    def cb_save_all(self, args):
        """Callback when save->all was clicked in the file menu"""
        self.save_all()
        self.save_popup.closePopupMenu()

    def cb_save_maps_all(self, args):
        """Callback when save->maps->all was clicked in the file menu"""
        self.app.save_all_maps()
        self.save_popup.closePopupMenu()
        self.save_maps_popup.closePopupMenu()

    def cb_save_map(self, args):
        """Callback when save->maps->map_name was clicked in the file menu"""
        map_name = args.window.getUserData()
        self.app.save_map(map_name)
        self.save_popup.closePopupMenu()
        self.save_maps_popup.closePopupMenu()

    def enable_map_menus(self):
        self.file_save.setEnabled(True)
        self.file_close.setEnabled(True)
        self.save_maps.setEnabled(True)
        self.file_import.setEnabled(True)

    def disable_map_menus(self):
        self.file_save.setEnabled(False)
        self.file_close.setEnabled(False)
        self.save_maps.setEnabled(False)
        self.file_import.setEnabled(False)

    def enable_all_menus(self):
        """Enable the menus for loaded maps"""
        self.enable_map_menus()

    def cb_open(self, args):
        """Callback when open was clicked in the file menu"""
        import tkinter.filedialog
        import tkinter.messagebox
        # Based on code from unknown-horizons
        try:
            selected_file = tkinter.filedialog.askopenfilename(
                filetypes=[(_("fife map file"), ".xml",)],
                title=_("Open file"))
        except ImportError:
            # tkinter may be missing5555
            selected_file = ""
        if selected_file:
            tree = ET.parse(selected_file)
            if tree.getroot().tag == "map":
                filename = os.path.relpath(selected_file, os.getcwd())
                fife_map = self.app.editor.load_map(filename)
                for cam in fife_map.getCameras():
                    if cam.getLocationRef().getMap().getId() == fife_map.getId():
                        game_map = GameMap(fife_map, fife_map.getId(),
                                           cam.getId(), dict(), self.app)
                        self.app.add_map(fife_map.getId(), game_map)
                        self.app.switch_map(game_map.name)
                        self.reset_maps_menu()
                        return

    def cb_map_switch_clicked(self, args):
        """Callback when a map from the menu was clicked"""
        self.view_maps_menu.closePopupMenu()
        self.app.switch_map(args.window.getUserData())
        self.reset_maps_menu()

    def cb_import_objects(self, args):
        """Callback when objects was clicked in the file->import menu"""
        self.import_popup.closePopupMenu()
        import tkinter.filedialog

        # Based on code from unknown-horizons
        try:
            selected_file = tkinter.filedialog.askopenfilename(
                filetypes=[("fife object definition", ".xml",)],
                title="import objects")
        except ImportError:
            # tkinter may be missing
            selected_file = ""

        if selected_file:
            selected_file = os.path.relpath(selected_file,
                                            os.getcwd())

            self.editor.import_object(selected_file)
            self.app.objects_imported()

    def show_layer_dialog(self, layer=None):
        """Show the dialog to edit the settings of a layer

        Args:

            layer: Optional argument to fill the fields with the values
            of an existing layer.
        """
        grid_types = ["square", "hexagonal"]
        dialog = LayerOptions(self.app, grid_types, layer)
        values = dialog.show_modal(self.editor_window, self.app.engine.pump)
        if not dialog.return_value:
            return None
        return values

    def create_layer(self, map_name):
        """Show the layer dialog and create a new layer on the given map
        with the values entered into it.

        Args:
            map_name: The identifier of the map where the layer should be
            added to

        Raises:

            ValueError if the there is already a layer with that name on the
            map or if there was no map with that identifier

        Returns:

            The created layer

        """
        values = self.show_layer_dialog()
        if not values:
            return None
        layer_name = values["LayerName"]
        cell_grid = values["GridType"]
        layer = self.editor.create_layer(map_name, layer_name, cell_grid)
        return layer

    def cb_add_map(self, args):
        """Callback when Map was clicked in the edit->Add menu"""
        import tkinter.messagebox

        self.add_popup.closePopupMenu()
        dialog = MapOptions(self.app)
        values = dialog.show_modal(self.editor_window,
                                   self.app.engine.pump)
        if not dialog.return_value:
            return
        map_id = values["MapId"]
        map_name = values["MapName"]
        fife_map = None
        try:
            fife_map = self.editor.create_map(map_id)
        except RuntimeError as error:
            tkinter.messagebox.showerror("Could not create map",
                                   "Creation of the map failed with the "
                                   "following FIFE Error: %s" % str(error))
            return
        layer = self.create_layer(map_id)

        if layer is None:
            self.editor.delete_map(fife_map)
            return

        resolution = self.app.settings.get("FIFE", "ScreenResolution",
                                           "1024x768")
        width, height = [int(s) for s in resolution.lower().split("x")]
        viewport = Rect(0, 0, width, height)

        camera_name = self.app.settings.get(
            "fife-rpg", "Camera", "main")
        camera = fife_map.addCamera(camera_name, layer, viewport)

        dialog = CameraOptions(self.app, camera)
        values = dialog.show_modal(self.editor_window,
                                   self.app.engine.pump)
        if not dialog.return_value:
            self.editor.delete_map(fife_map)
            return
        camera.setId(values["CameraName"])
        camera.setViewPort(values["ViewPort"])
        camera.setRotation(values["Rotation"])
        camera.setTilt(values["Tilt"])
        cid = values["CellImageDimensions"]
        camera.setCellImageDimensions(cid.x, cid.y)
        renderer = InstanceRenderer.getInstance(camera)
        renderer.activateAllLayers(fife_map)
        game_map = GameMap(fife_map, map_name, camera_name, {}, self.app)

        self.app.add_map(map_id, game_map)
        self.app.changed_maps.append(map_id)
        self.reset_maps_menu()

    def cb_value_changed(self, section, property_name, value):
        """Called when the value of a properties changed

        Args:

            section: The section of the properties

            property_name: The name of the properties

            value: The new value of the properties
        """
        identifier = self.app.selected_object.getId()
        world = self.app.world
        if section != "Instance":
            return
        is_valid = True
        if property_name == "Identifier":
            value = value
            self.app.selected_object.setId(value)
        elif property_name == "CostId":
            cur_cost = self.app.selected_object.getCost()
            try:
                value = value
                self.app.selected_object.setCost(value, cur_cost)
            except UnicodeEncodeError:
                print("The CostId has to be an ascii value")
                is_valid = False
        elif property_name == "Cost":
            cur_cost_id = self.app.selected_object.getCostId()
            try:
                self.app.selected_object.setCost(cur_cost_id,
                                                 float(value))
            except ValueError as error:
                print(error.message)
                is_valid = False
        elif property_name == "Blocking":
            self.app.selected_object.setBlocking(value)
        elif property_name == "Rotation":
            try:
                self.app.selected_object.setRotation(int(value))
            except ValueError as error:
                print(error.message)
                is_valid = False
        elif property_name == "StackPosition":
            try:
                visual = self.app.selected_object.get2dGfxVisual()
                visual.setStackPosition(int(value))
            except ValueError as error:
                print(error.message)
                is_valid = False
        if is_valid:
            map_name = self.app.current_map.name
            if map_name not in self.app.changed_maps:
                self.app.changed_maps.append(map_name)
        self.update_property_editor()

    def cb_layer_box_changed(self, args):
        """Called when something at the layerbox was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        is_selected = args.window.getSelectedCount() > 0

        self.delete_layer_button.setEnabled(is_selected)
        self.edit_layer_button.setEnabled(is_selected)

    def cb_add_layer_activated(self, args):
        """Called when the + Button in the layer box was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        try:
            current_map = self.app.current_map
            layer = self.create_layer(current_map.fife_map.getId())
            renderer = InstanceRenderer.getInstance(current_map.camera)
            renderer.addActiveLayer(layer)
        except ValueError:
            import tkinter.messagebox
            tkinter.messagebox.showerror("Error",
                                   "There is already a layer with that name.")
            return
        self.reset_layerlist()
        self.update_layerlist()

    def cb_delete_layer_activated(self, args):
        """Called when the - Button in the layer box was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        map_id = self.app.current_map.fife_map.getId()
        if self.editor.get_layer_count(map_id) <= 1:
            import tkinter.messagebox
            tkinter.messagebox.showerror(_("Error"),
                                   _("Cannot delete the last layer"))
            return
        self.editor.delete_layer(map_id,
                                 self.selected_layer)
        self.reset_layerlist()
        self.update_layerlist()

    def cb_edit_layer_activated(self, args):
        """Called when the Edit Button in the layer box was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        layer = self.editor.get_layer(self.app.current_map.fife_map.getId(),
                                      self.selected_layer)
        values = self.show_layer_dialog(layer)
        if not values:
            return None
        layer_name = values["LayerName"]
        cell_grid = self.editor.get_cell_grid(values["GridType"])
        layer.setId(layer_name)
        layer.setCellGrid(cell_grid)
        self.reset_layerlist()
        self.update_layerlist()

    def cb_map_switched(self, old_map, new_map_name):
        """Called when the app switched to another map.

        Args:

          old_map: The map that was active before the switch

          new_map_name: The name of the new_map
        """
        self.add_layer_button.setEnabled(new_map_name is not None)
        if new_map_name is not None:
            self.enable_map_menus()
        else:
            self.disable_map_menus()

    def cb_menu_leave(self, args):
        """Calld when the menubar loses input focus"""
        item = self.menubar.getPopupMenuItem()
        if item is not None:
            item.closePopupMenu()

    def cb_add_popup_order_changed(self, args):
        """Called when the order of the add popupmenu was changed"""
        if self.add_comp_event is None:
            return
        self.add_comp_event.disconnect()
        self.add_comp_event = None
        self.close_add_component_menu()
