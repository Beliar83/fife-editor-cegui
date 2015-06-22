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
import sys
import shutil
from StringIO import StringIO

import yaml
# pylint: disable=unused-import
import PyCEGUI  # @UnusedImport # PyCEGUI won't work otherwise (on windows)
from PyCEGUIOpenGLRenderer import PyCEGUIOpenGLRenderer  # @UnusedImport
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
from fife_rpg.components import ComponentManager
from fife_rpg.components.agent import Agent
from fife_rpg.actions import ActionManager
from fife_rpg.systems import SystemManager
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.game_scene import GameSceneView
from fife_rpg import helpers
from fife_rpg.map import Map as GameMap
from fife_rpg.entities import RPGEntity

from editor.editor_gui import EditorGui
from editor.editor import Editor
from editor.editor_scene import EditorController
from editor.project_settings import ProjectSettings
from editor.components import Components, AvailableComponents
from editor.systems import Systems, AvailableSystems
from editor.actions import Actions, AvailableActions
from editor.behaviours import Behaviours, AvailableBehaviours

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

        self.current_project_file = ""
        self.project = None
        self.project_source = None
        self.project_dir = None
        self.editor_gui = None

        self.changed_maps = []
        self.project_changed = False
        self.entity_changed = False
        self._project_cleared_callbacks = []
        self.add_map_load_callback(self.cb_map_loaded)
        self.map_entities = None
        self.entities = {}
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

    def edit_project_settings(self, project_dir, project):
        """Show a dialog to edit the settings of a project

        Args:

            project_filepath: Path to the project file

            project: The project to edit
        """
        settings = project.getAllSettings("fife-rpg")
        if os.path.isfile(project_dir):
            project_dir = os.path.dirname(project_dir)
        dialog = ProjectSettings(self,
                                 settings,
                                 project_dir)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        update_settings(project, values)
        self.project_changed = True
        return True

    def convert_fife_project(self, project_filepath):
        """Converts a fife settings file to a fife-rpg project

        Args:
            Project_filepath: Path to the fife settings file
        """
        project = SimpleXMLSerializer(project_filepath)

        bak_file = "%s.bak" % project_filepath
        project.save(bak_file)
        settings = {}
        settings["ProjectName"] = project.get("FIFE", "WindowTitle", "")
        update_settings(project, settings)
        if not self.edit_project_settings(project_filepath, project):
            return None
        project.save()
        return bak_file

    def new_project(self, settings_path, values):
        """Create a mew project and load it

        Args:
            settings_path: The path to the new settings file

            values: The starting values of the project.
        """
        import tkMessageBox
        settings_file = file(settings_path, "w")
        settings_file.write(BASIC_SETTINGS)
        settings_file.close()
        project = SimpleXMLSerializer(settings_path)
        project.load()
        update_settings(project, values)
        project.save()
        comp_file = project.get("fife-rpg", "ComponentsFile")
        act_file = comp_file or project.get("fife-rpg", "ActionsFile")
        syst_file = act_file or project.get("fife-rpg", "SystemsFile")
        beh_file = syst_file or project.get("fife-rpg", "BehavioursFile")
        comb_file = beh_file or project.get("fife-rpg", "CombinedFile")
        if not comb_file:
            dest = os.path.join(os.path.dirname(settings_path),
                                "combined.yaml")
            shutil.copy("combined.yaml.template", dest)
        self.try_load_project(settings_path)
        tkMessageBox.showinfo(_("Project created"),
                              _("Project successfully created"))
        self.editor_gui.enable_menus()
        self.project_changed = False
        self.entity_changed = False

    def switch_map(self, map_name):
        """Switches to the given map.

        Args:
            name: The name of the map
        """
        if self.map_entities:
            self.show_map_entities(self.current_map.name)
            self.map_entities = None
        if not self.project_dir:
            return
        try:
            old_dir = os.getcwd()
            os.chdir(self.project_dir)
            try:
                RPGApplicationCEGUI.switch_map(self, map_name)
            finally:
                os.chdir(old_dir)
            self.editor_gui.listbox.resetList()
            if self.current_map:
                self.editor_gui.update_layerlist()
                if not self.editor_gui.show_agents_check.isSelected():
                    self.hide_map_entities(self.current_map.name)
        except Exception as error:  # pylint: disable=broad-except
            import tkMessageBox
            tkMessageBox.showerror("Can't change map",
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
        self._components = {}
        self._actions = {}
        self._systems = {}
        self._behaviours = {}
        self.changed_maps = []
        self.project_changed = False
        self.entity_changed = False
        self.editor_gui.reset_layerlist()
        self.map_entities = None
        self.set_selected_object(None)
        tmp_settings = self.settings.getSettingsFromFile("fife-rpg").keys()
        for setting in tmp_settings:
            if setting in self.editor_settings:
                self.settings.set("fife-rpg", setting,
                                  self.editor_settings[setting])
            else:
                self.settings.remove("fife-rpg", setting)
        ComponentManager.clear_components()
        ComponentManager.clear_checkers()
        ActionManager.clear_actions()
        ActionManager.clear_commands()
        SystemManager.clear_systems()
        BehaviourManager.clear_behaviours()
        self.editor.delete_objects()
        self.editor.delete_maps()
        if self.project_source is not None:
            self.engine.getVFS().removeSource(self.project_source)
            self.project_source = None
        if self.project_dir is not None:
            sys.path.remove(self.project_dir)
            self.project_dir = None
        self.project = None
        for callback in self._project_cleared_callbacks:
            callback()

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
            self.changed_maps = []
            self.project_changed = False
            self.entity_changed = False
            try:
                old_dir = os.getcwd()
                os.chdir(self.project_dir)
                self.load_maps()
                os.chdir(old_dir)
            except:  # pylint: disable=bare-except
                pass
            return True
        return False

    def load_project_settings(self):
        """Loads the settings file"""
        project_settings = self.project.getAllSettings("fife-rpg")
        del project_settings["ProjectName"]
        for setting, value in project_settings.iteritems():
            self.settings.set("fife-rpg", setting, value)

    def save_map(self, map_name=None):
        """Save the current state of the map

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
        map_entities = game_map.entities.copy()
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.new_map = ""
        game_map.update_entities_fife()
        fife_map = game_map.fife_map
        filename = fife_map.getFilename()
        if not filename:
            maps_path = self.settings.get(
                "fife-rpg", "MapsPath", "maps")
            filename = os.path.join(self.project_dir, maps_path,
                                    "%s.xml" % map_name)
            fife_map.setFilename(filename)
        try:
            os.makedirs(os.path.dirname(filename))
        except os.error:
            pass

        old_dir = os.getcwd()
        os.chdir(self.project_dir)
        import_list = [root_subfile(filename, i) for
                       i in self.editor.get_import_list(fife_map.getId())]
        saver = MapSaver()
        saver.save(fife_map, filename, import_list)
        os.chdir(old_dir)
        for entity in map_entities:
            agent = getattr(entity, Agent.registered_as)
            agent.map = map_name
        game_map.update_entities()
        self.update_agents(game_map)
        self.editor_gui.current_toolbar.activate()
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

    def entity_constructor(self, loader, node):
        """Constructs an Entity from a yaml node

        Args:
            loader: A yaml BaseConstructor

            node: The yaml node

        Returns:
            The created Entity
        """
        entity_dict = loader.construct_mapping(node, deep=True)
        entity = self.world.entity_constructor(loader, node)
        self.entities[entity.identifier] = entity_dict
        return entity

    def parse_entities(self, entities_file):
        """Parse the entities from a file

        Args:

            entities_file: A file object from where the entities are being
            loaded.
        """
        yaml.add_constructor('!Entity', self.entity_constructor,
                             yaml.SafeLoader)

        entities = yaml.safe_load_all(entities_file)
        try:
            while entities.next():
                entities.next()
        except StopIteration:
            pass

    def load_entities(self):
        """Load and store the entities of the current project"""
        if self.project is None:
            return
        entities_file_name = self.project.get("fife-rpg", "EntitiesFile",
                                              "objects/entities.yaml")
        vfs = self.engine.getVFS()
        entities_file = vfs.open(entities_file_name)
        self.parse_entities(entities_file)

    def entity_representer(self, dumper, data):
        """Creates a yaml node representing an entity

        Args:
            dumper: A yaml BaseRepresenter

            data: The Entity

        Returns:
            The created node
        """
        if data.identifier in self.entities:
            old_entity_dict = self.entities[data.identifier]
            template = None
            if "Template" in old_entity_dict:
                template = old_entity_dict["Template"]
        else:
            template = None
        entity_dict = self.world.create_entity_dictionary(data)
        if template is not None:
            components = entity_dict["Components"]
            entity_dict["Template"] = template
            template_dict = {}
            self.world.update_from_template(template_dict, template)
            for component, fields in template_dict.iteritems():
                if component not in components:
                    continue
                for field, value in fields.iteritems():
                    if field not in components[component]:
                        continue
                    if components[component][field] == value:
                        del components[component][field]
                if not components[component]:
                    del components[component]
            entity_dict["Components"] = components
        entity_node = dumper.represent_mapping(u"!Entity", entity_dict)
        return entity_node

    def dump_entities(self, entities_file):
        """Dumps the projects entities to a file

        Args:

            entities_file: A file object to where the entities are written.
        """
        entities = self.world[RPGEntity].entities
        yaml.add_representer(RPGEntity, self.entity_representer,
                             yaml.SafeDumper)
        helpers.dump_entities(entities, entities_file)

    def save_entities(self):
        """Save all entities to the entity file"""
        entities_file_name = self.project.get("fife-rpg", "EntitiesFile",
                                              "objects/entities.yaml")
        old_wd = os.getcwd()
        os.chdir(self.project_dir)
        try:
            entities_file = file(entities_file_name, "w")
            self.dump_entities(entities_file)
            self.entity_changed = False
        finally:
            os.chdir(old_wd)

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

    def reset_world(self, entities_file=None):
        """Create a new world and set its values

        Args:

            entities_file: An optional file object to load entities from
        """
        self.create_world()
        try:
            self.world.read_object_db()
            self.world.import_agent_objects()
            if entities_file is not None:
                self.parse_entities(entities_file)
            else:
                self.load_entities()
        except:  # pylint: disable=bare-except
            pass

    def setup_project(self):
        """Sets up the project"""
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
        self.reset_world()

    def try_load_project(self, file_name):
        """Try to load the specified file as a project

        Args:

            file_name: The file to load
        """
        loaded = self.load_project(file_name)
        if loaded:
            self.current_project_file = file_name
            self.editor_gui.reset_maps_menu()
            old_dir = os.getcwd()
            os.chdir(self.project_dir)
            sys.path.insert(0, self.project_dir)
            try:
                self.setup_project()
            finally:
                os.chdir(old_dir)
            return True
        return False

    def save_project(self):
        """Saves the current project"""
        self.project.save()
        maps = {}
        for game_map in self.maps.itervalues():
            if isinstance(game_map.fife_map, FifeMap):
                fife_map = game_map.fife_map
                filepath = os.path.split(fife_map.getFilename())[-1]
            else:
                filepath = os.path.split(game_map.fife_map)[-1]
            map_name = os.path.splitext(filepath)[0]
            maps[game_map.view_name] = map_name
        save_data = {"Maps": maps}
        maps_path = self.settings.get("fife-rpg", "MapsPath", "maps")
        maps_filename = os.path.join(self.project_dir, maps_path, "maps.yaml")
        maps_file = file(maps_filename, "w")
        yaml.dump(save_data, maps_file, default_flow_style=False)
        maps_file.close()
        combined_filename = self.settings.get("fife-rpg", "CombinedFile", None)
        comp_filename = self.settings.get("fife-rpg", "ComponentsFile", None)
        syst_filename = self.settings.get("fife-rpg", "ActionsFile", None)
        act_filename = self.settings.get("fife-rpg", "SystemsFile", None)
        beh_filename = self.settings.get("fife-rpg", "BehavioursFile", None)
        project_dir = self.project_dir
        if None in (comp_filename, syst_filename, act_filename, beh_filename):
            combined_filename = "combined.yaml"
            combined = {}
        if comp_filename is not None:
            data = {"Components": self._components}
            filename = os.path.join(project_dir, comp_filename)
            stream = file(filename, "w")
            yaml.dump(data, stream, dumper=helpers.FRPGDumper)
            stream.close()
        else:
            combined["Components"] = self._components
        if syst_filename is not None:
            data = {"Systems": self._systems}
            filename = os.path.join(project_dir, syst_filename)
            stream = file(filename, "w")
            yaml.dump(data, stream, dumper=helpers.FRPGDumper)
            stream.close()
        else:
            combined["Systems"] = self._systems
        if act_filename is not None:
            data = {"Actions": self._actions}
            filename = os.path.join(project_dir, act_filename)
            stream = file(filename, "w")
            yaml.dump(data, stream, dumper=helpers.FRPGDumper)
            stream.close()
        else:
            combined["Actions"] = self._actions
        if beh_filename is not None:
            data = {"Behaviours": self._behaviours}
            filename = os.path.join(project_dir, beh_filename)
            stream = file(filename, "w")
            yaml.dump(data, stream, dumper=helpers.FRPGDumper)
            stream.close()
        else:
            combined["Behaviours"] = self._behaviours
        if combined_filename is not None:
            filename = os.path.join(project_dir, combined_filename)
            stream = file(filename, "w")
            yaml.dump(combined, stream, Dumper=helpers.FRPGDumper)
            stream.close()
        self.project_changed = False

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
        self.map_entities = None

    def quit(self):
        """
        Quit the application. Really!
        """
        if self.current_dialog:
            return
        if self.editor_gui.ask_save_changed():
            self.quitRequested = True

    def edit_components(self):
        """Show the dialog to edit components"""
        dialog = Components(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        entities_hidden = self.map_entities is not None
        if entities_hidden:
            self.show_map_entities(self.current_map.name)
        tmp_file = StringIO()
        self.dump_entities(tmp_file)
        for entity in tuple(self.world.entities):
            entity.delete()
        ComponentManager.clear_components()
        ComponentManager.clear_checkers()
        current_items = list(values["current_items"])
        self.project.set("fife-rpg", "Components", current_items)
        self.world.register_mandatory_components()
        self.register_components(current_items)
        tmp_file.seek(0)
        self.reset_world(tmp_file)
        for game_map in self.maps.itervalues():
            game_map.update_entities()
            self.update_agents(game_map)
        if entities_hidden:
            self.hide_map_entities(self.current_map.name)

        self.project_changed = True

    def edit_available_components(self):
        """Show the dialog to edit components"""
        dialog = AvailableComponents(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        components = values["components"]
        self._components = components
        self.project_changed = True

    def edit_systems(self):
        """Show the dialog to edit systems"""
        dialog = Systems(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        SystemManager.clear_systems()
        current_items = list(values["current_items"])
        self.project.set("fife-rpg", "Systems", current_items)
        self.register_systems(current_items)

        self.project_changed = True

    def edit_available_systems(self):
        """Show the dialog to edit systems"""
        dialog = AvailableSystems(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        systems = values["systems"]
        self._systems = systems
        self.project_changed = True

    def edit_actions(self):
        """Show the dialog to edit actions"""
        dialog = Actions(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        ActionManager.clear_actions()
        current_items = list(values["current_items"])
        self.project.set("fife-rpg", "Actions", current_items)
        self.register_actions(current_items)

        self.project_changed = True

    def edit_available_actions(self):
        """Show the dialog to edit actions"""
        dialog = AvailableActions(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        actions = values["actions"]
        self._actions = actions
        self.project_changed = True

    def edit_behaviours(self):
        """Show the dialog to edit behaviours"""
        dialog = Behaviours(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        BehaviourManager.clear_behaviours()
        current_items = list(values["current_items"])
        self.project.set("fife-rpg", "Behaviours", current_items)
        self.register_behaviours(current_items)

        self.project_changed = True

    def edit_available_behaviours(self):
        """Show the dialog to edit behaviours"""
        dialog = AvailableBehaviours(self)
        values = dialog.show_modal(self.editor_gui.editor_window,
                                   self.engine.pump)
        if not dialog.return_value:
            return False
        behaviours = values["behaviours"]
        self._behaviours = behaviours
        self.project_changed = True


def update_settings(project, values):
    """Update the fife-rpg settings of a project

    Args:
        project: The project to update

        values: The new fife-rpg settings
    """
    settings = project.getAllSettings("fife-rpg")
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
