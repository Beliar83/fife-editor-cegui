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

""" Contains the objects toolbar

.. module:: object_toolbar
    :synopsis: Contains the objects toolbar

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import next
from past.utils import old_div
from io import StringIO
import os
from queue import Queue, Empty
import _thread

from lxml import etree
import PyCEGUI
from fife import fife

# pylint: disable=unused-import
import PyCEGUIOpenGLRenderer  # @UnusedImport
# pylint: enable=unused-import

from .toolbarpage import ToolbarPage
from .undo_editor import UndoCreateInstance, UndoRemoveInstance


def parse_file(filename):
    """Generator that parse an fife object definition file and yields the
    objects.

        Args:

            filename: The path to the object file.
    """
    root_path = os.path.dirname(filename)
    try:
        tree = etree.parse(filename)
        """:type : etree._ElementTree"""
        root = tree.getroot()
        """:type : etree._Element"""
        assert(root.tag == "assets")
        atlas_def = dict()
        for element in root.findall("atlas"):
            atlas_def.update(parse_atlas(element, root_path))
        for obj in root.findall("object"):
            assert(isinstance(obj, etree._Element))
            yield parse_object(obj, root_path, atlas_def)

    except etree.XMLSyntaxError as error:
        # TODO: Should be obsolete with the fife xml update

        assert False
        doc = file(filename, "r")
        line_no = error.position[0] - 2
        lines = doc.readlines()
        first_doc = StringIO(u"".join(lines[:line_no]))
        tree = etree.parse(first_doc)
        root = tree.getroot()
        proc_instr = root.getprevious()
        file_type = proc_instr.text.split("=")[1].replace('"', '').lower()
        if not file_type == "atlas":
            raise RuntimeError("Unexpected file format '%s'" % (filename))
        atlas_def = parse_atlas(root, root_path)
        second_doc = lines[line_no + 1:]
        second_doc.insert(0, "<namespaces>\n")
        second_doc.append("</namespaces>\n")
        second_doc = StringIO(u"".join(second_doc))
        tree = etree.parse(second_doc)
        object_defs = tree.getroot().findall("object")
        for obj in object_defs:
            yield parse_object(obj, root_path, atlas_def)

def parse_atlas(element, root_path):  # pylint: disable=unused-argument
    """Parse an atlas definition

        Args:

            element: The etree element that contains the definition

            root_path: The path of the object file the element is in

        Returns: A dictionary with images and their positions in an atlas
    """
    atlas_def = {}

    atlas_def["atlas"] = element
    atlas_def["images"] = {}
    images = element.findall("subimage")
    for image in images:
        attribs = image.attrib
        image_name = attribs["id"]
        atlas_def["images"][image_name] = image

    return atlas_def


def parse_object(obj, root_path, atlas_def=None):
    """Parse an object definition

        Args:

            obj: The etree element containing the definition

            root_path: The path of the object file the element is in

            atlas_def: A dictionary with images and their positions in an atlas
    """
    obj_def = {}

    obj_def["object"] = dict(obj.attrib)
    if atlas_def:
        image_sources = atlas_def["images"]
    else:
        image_sources = {}
    if int(obj.attrib["static"]) == 0:
        obj_def["actions"] = parse_actions(obj.findall("action"), root_path)
    elif int(obj.attrib["static"]) == 1:
        images = obj.findall("image")
        dir_defs = obj_def["directions"] = {}
        for image in images:
            attrib = dict(image.attrib)
            source = attrib["source"]
            image_def = attrib
            if source in image_sources:
                image_def.update(image_sources[source].attrib)
                image_def["type"] = "atlas"
                image_def["source"] = atlas_def["atlas"].attrib["source"]
            else:
                image_def["type"] = "image"
            source = os.path.join(root_path, image_def["source"])
            image_def["source"] = os.path.abspath(source)
            direction = int(image_def["direction"])
            dir_defs[direction] = image_def

    else:
        raise RuntimeError(_("Don't know how to handle '%s'") % (obj[0].tag))
    return obj_def


def parse_actions(actions, root_path):
    """Parse action definitions

        Args:

            actions: A list of etree elements containg action definitons

            root_path: The path of the object file the elements are in
    """
    action_dict = {}
    for action in actions:

        animations = parse_animations(action.findall("animation"), root_path)
        action_dict[action.attrib["id"]] = animations

    return action_dict


def parse_animations(animations, root_path):
    """Parse animation definitions

        Args:

            animations: A list of etree elements containg animation definitons

            root_path: The path of the object file the elements are in
    """
    ani_dict = {}

    if "atlas" in animations[0].attrib:
        ani_dict["type"] = "single"
        animation = animations[0]
        ani_dict.update(parse_animation_atlas(animation, root_path))
    else:
        ani_dict["type"] = "multi"
        ani_dict["directions"] = {}
        for animation in animations:
            ani_def = parse_animation(animation, root_path)
            direction = int(ani_def["direction"])
            ani_dict["directions"][direction] = ani_def

    return ani_dict


def parse_animation(animation, root_path):
    """Parse an animation definition

        Args:

            animation: An etree element containing the definiton

            root_path: The path of the object file the element is in
    """
    ani_dict = {}

    if "source" in animation.attrib:
        animation_file = animation.attrib["source"]
        ani_file = os.path.join(root_path, animation_file)
        ani_path = os.path.dirname(ani_file)
        ani_doc = etree.parse(ani_file)
        root = ani_doc.getroot()
        ani_dict["delay"] = root.attrib["delay"]
        ani_dict.update(parse_animation(root, ani_path))
    else:
        frames = []
        for frame in animation.findall("frame"):
            source = os.path.join(root_path, frame.attrib["source"])
            source = os.path.abspath(source)
            frames.append(source)
        ani_dict["direction"] = animation.attrib["id"].split(":")[2]
        ani_dict["frames"] = frames
        ani_dict["x_offset"] = animation.attrib["x_offset"]
        ani_dict["y_offset"] = animation.attrib["y_offset"]

    return ani_dict


def parse_animation_atlas(animation, root_path):
    """Parse an animation definition that uses an atlas

        Args:

            animation: An etree element containing the definiton

            root_path: The path of the object file the element is in
    """
    ani_dict = {}

    ani_dict["atlas"] = {}
    image = os.path.join(root_path, animation.attrib["atlas"])
    ani_dict["atlas"]["image"] = os.path.abspath(image)
    ani_dict["atlas"]["width"] = animation.attrib["width"]
    ani_dict["atlas"]["height"] = animation.attrib["height"]
    ani_dict["directions"] = {}
    for direction in animation.findall("direction"):
        action_dir = int(direction.attrib["dir"])
        dir_data = ani_dict["directions"][action_dir] = {}
        dir_data["delay"] = direction.attrib["delay"]
        dir_data["frames"] = direction.attrib["frames"]

    return ani_dict


class ObjectToolbar(ToolbarPage):

    """A toolbar for displaying and placing static objects on a map"""
    DEFAULT_ALPHA = 0.75
    HIGHLIGHT_ALPHA = 1.0

    def __init__(self, app):

        ToolbarPage.__init__(self, app, "Objects")

        self.namespaces = {}
        self.images = {}
        self.image_directions = {}
        self.selected_object = [None, None]
        self.is_active = False
        self.cur_rotation = 0
        x_adjust = 5
        pos = self.gui.getPosition()
        y_pos = pos.d_y
        x_pos = PyCEGUI.UDim(0, x_adjust)
        width = PyCEGUI.UDim(0.9, 0.0)
        label = self.gui.createChild("TaharezLook/Label",
                                     "ObjectsLabel")
        label.setText(_("Objects"))
        label.setWidth(width)
        label.setXPosition(x_pos)
        label.setProperty("HorzFormatting", "LeftAligned")
        items_panel = self.gui.createChild("TaharezLook/ScrollablePane",
                                           "Items_panel")
        y_pos.d_scale = y_pos.d_scale + 0.045
        items_panel.setXPosition(x_pos)
        items_panel.setYPosition(y_pos)
        size = self.gui.getSize()
        size.d_height.d_scale = size.d_height.d_scale - y_pos.d_scale
        size.d_width.d_offset = size.d_width.d_offset - x_adjust
        items_panel.setSize(size)
        self.items_panel = items_panel
        self.items = None
        self.have_objects_changed = False
        self.app.add_map_switch_callback(self.cb_map_changed)
        self.last_mouse_pos = None
        self.last_instance = None
        mode = self.app.current_mode
        mode.listener.add_callback("mouse_pressed",
                                   self.cb_map_clicked)
        mode.listener.add_callback("mouse_dragged",
                                   self.cb_map_clicked)
        mode.listener.add_callback("mouse_moved",
                                   self.cb_map_moved)
        mode.listener.add_callback("key_pressed",
                                   self.cb_key_pressed)
        self.app.add_project_clear_callback(self.cb_project_closed)
        self.app.add_objects_imported_callback(self.cb_objects_imported)
        self.objects = Queue()
        self.images_lock = _thread.allocate_lock()
        self.namespaces_lock = _thread.allocate_lock()

    def image_clicked(self, args):
        """Called when the user clicked on an image

            Args:

                args: The args of the event
        """
        self.images_lock.acquire()
        identifier = args.window.getName()
        image = self.images[identifier]
        obj_data = image.user_data
        if identifier not in self.images:
            return
        if self.selected_object[0] is not None:
            old_identifier = ".".join(self.selected_object)
            self.images[old_identifier].setAlpha(self.DEFAULT_ALPHA)
        self.images[identifier].setAlpha(self.HIGHLIGHT_ALPHA)
        self.selected_object = obj_data
        self.cur_rotation = self.image_directions[identifier][0]
        self.images_lock.release()

    def update_contents(self):
        """Update the contents of the toolbar page"""
        if self.have_objects_changed and self.is_active:
            _thread.start_new(self.update_objects_threaded, ())
        elif self.is_active:
            self.process_object()
        ToolbarPage.update_contents(self)

    def update_objects_threaded(self):
        """Update the contents of the toolbar page"""
        self.namespaces_lock.acquire()
        self.have_objects_changed = False
        self.namespaces = {}
        model = self.app.engine.getModel()
        namespaces = model.getNamespaces()
        for namespace in namespaces:
            self.namespaces[namespace] = []
            objects = model.getObjects(namespace)
            for fife_object in objects:
                identifier = fife_object.getId()
                if identifier in self.namespaces[namespace]:
                    continue
                if identifier in self.images:
                    continue
                project_dir = self.app.project_source
                object_filename = fife_object.getFilename()
                if project_dir is not None:
                    filename = os.path.join(project_dir, object_filename)
                else:
                    filename = object_filename

                objects = parse_file(filename)
                for obj in objects:
                    identifier = obj["object"]["id"]
                    if identifier in self.namespaces[namespace]:
                        continue
                    if identifier in self.images:
                        continue
                    self.namespaces[namespace].append(identifier)
                    self.objects.put((namespace, obj))
        self.images_lock.acquire()
        for image in self.images.values():
            namespace, image_id = image.user_data
            if image_id not in self.namespaces[namespace]:
                wmgr = PyCEGUI.WindowManager.getSingleton()
                image.getParent().removeChild(image)
                wmgr.destroyWindow(image)
                del self.images[image_id]
        self.images_lock.release()
        self.namespaces_lock.release()

    def process_object(self):
        """Processes the next object in the Queue"""
        try:
            namespace, obj = self.objects.get_nowait()
        except Empty:
            return
        vec2f = PyCEGUI.Vector2f
        sizef = PyCEGUI.Sizef
        cegui_system = PyCEGUI.System.getSingleton()
        renderer = cegui_system.getRenderer()
        image_manager = PyCEGUI.ImageManager.getSingleton()
        obj_def = obj["object"]
        identifier = obj_def["id"]
        name = ".".join([namespace, identifier])
        if name in self.images:
            return
        img_def = {}
        img_def["static"] = obj_def["static"]
        dirs = []
        if int(obj_def["static"]) == 0:
            actions = obj["actions"]
            img_def["actions"] = {}
            actions_dict = img_def["actions"]
            action, action_def = next(iter(actions.items()))
            img_type = action_def["type"]
            if img_type == "single":
                atlas_def = action_def["atlas"]
                fname = atlas_def["image"]
                if renderer.isTextureDefined(name):
                    tex = renderer.getTexture(name)
                else:
                    tex = renderer.createTexture(name, fname, "FIFE")
                tex_size = tex.getSize()
                tex_width = tex_size.d_width
                frame_width = int(atlas_def["width"])
                frame_height = int(atlas_def["height"])
                frames_p_line = old_div(tex_width, frame_width)
                frame_count = 0
            dirs_def = action_def["directions"]
            actions_dict[action] = {}
            dirs = sorted(dirs_def.keys())
            dir_def = dirs_def[dirs[0]]

            if img_type == "multi":
                frame = dir_def["frames"][0]
                if not renderer.isTextureDefined(name):
                    tex = renderer.createTexture(name, frame, "FIFE")
                    pos = vec2f(0, 0)
                    size = sizef(
                        tex.getSize().d_width,
                        tex.getSize().d_height)
                    area = PyCEGUI.Rectf(pos, size)
                    image = image_manager.create("BasicImage", name)
                    image.setTexture(tex)
                    image.setArea(area)
            elif img_type == "single":
                line = old_div(frame_count, frames_p_line)
                col = frame_count % frames_p_line
                pos = vec2f(col * frame_width,
                            line * frame_height)
                size = sizef(frame_width,
                             frame_height)
                area = PyCEGUI.Rectf(pos, size)
                if not image_manager.isDefined(name):
                    image = image_manager.create("BasicImage", name)
                    image.setTexture(tex)
                    image.setArea(area)
                frame_count = frame_count + 1
        elif int(obj_def["static"]) == 1:
            img_def["directions"] = []
            dirs_def = obj["directions"]
            dirs = sorted(dirs_def.keys())
            dir_def = dirs_def[dirs[0]]
            source = dir_def["source"]
            if dir_def["type"] == "atlas":
                tex_name = ".".join([source, "atlas"])

                if not renderer.isTextureDefined(tex_name):
                    tex = renderer.createTexture(tex_name, source, "FIFE")
                else:
                    tex = renderer.getTexture(tex_name)
                pos = vec2f(float(dir_def["xpos"]),
                            float(dir_def["ypos"]))
                size = sizef(float(dir_def["width"]),
                             float(dir_def["height"]))
                area = PyCEGUI.Rectf(pos, size)
                image = image_manager.create("BasicImage", name)
                image.setTexture(tex)
                image.setArea(area)
            elif dir_def["type"] == "image":
                if not renderer.isTextureDefined(name):
                    tex = renderer.createTexture(name, source, "FIFE")
                    pos = vec2f(0, 0)
                    size = sizef(tex.getSize().d_width, tex.getSize().d_height)
                    area = PyCEGUI.Rectf(pos, size)
                    image = image_manager.create("BasicImage", name)
                    image.setTexture(tex)
                    image.setArea(area)
        name = ".".join([namespace, identifier])
        wmgr = PyCEGUI.WindowManager.getSingleton()
        if name not in self.images:
            image = wmgr.createWindow(
                "TaharezLook/StaticImage", name)
            image.setTooltipText(name)
            image.setProperty("Image", name)
            self.items.addChild(image)
            if dirs:
                self.image_directions[name] = dirs
            else:
                self.image_directions[name] = [0]
            image.setAlpha(self.DEFAULT_ALPHA)
            image.user_data = [namespace, identifier]
            image.subscribeEvent(PyCEGUI.Window.EventMouseClick,
                                 self.image_clicked)
            self.images_lock.acquire()
            self.images[name] = image
            self.images_lock.release()

    def activate(self):
        """Called when the page gets activated"""
        self.is_active = True

    def deactivate(self):
        """Called when the page gets deactivated"""
        namespace, name = self.selected_object
        if namespace is not None:
            identifier = ".".join((namespace, name))
            self.images_lock.acquire()
            self.images[identifier].setAlpha(self.DEFAULT_ALPHA)
            self.images_lock.release()
        self.selected_object = [None, None]
        self.clean_mouse_instance()
        self.is_active = False

    def cb_map_changed(self, old_map_name, new_map_name):
        """Called when the map of the app changed

            Args:

                old_map_name: Name of the map that was previously loaded

                new_map_name: Name of the map that was changed to
        """
        self.have_objects_changed = True

    def cb_map_clicked(self, click_point, button):
        """Called when a position on the screen was clicked

        Args:

            click_point: A fife.ScreenPoint with the the position that was
            clicked on the screen

            button: The button that was clicked
        """
        self.clean_mouse_instance()
        if self.app.editor_gui.selected_layer is None or not self.is_active:
            return
        if (button == fife.MouseEvent.MIDDLE or
                button == fife.MouseEvent.UNKNOWN_BUTTON):
            return
        if self.selected_object[0] is None and button == fife.MouseEvent.LEFT:
            return
        layer = self.app.current_map.get_layer(
            self.app.editor_gui.selected_layer)
        location = self.app.screen_coords_to_map_coords(
            click_point, self.app.editor_gui.selected_layer
        )
        world = self.app.world
        for instance in layer.getInstancesAt(location):
            if world.is_identifier_used(instance.getId()):
                continue
            action = UndoRemoveInstance(self.app.editor, instance)
            action.redo()
            self.app.editor.undo_manager.add_action(action)
            self.app.set_selected_object(None)

        map_name = self.app.current_map.name
        if map_name not in self.app.changed_maps:
            self.app.changed_maps.append(map_name)

        if button == fife.MouseEvent.RIGHT:
            return
        coords = location.getLayerCoordinates()
        object_data = list(reversed(self.selected_object))
        action = UndoCreateInstance(self.app.editor, layer, coords,
                                    object_data, self.cur_rotation)
        instance = action.redo()
        self.app.editor.undo_manager.add_action(action)
        self.app.set_selected_object(instance)

    def clean_mouse_instance(self):
        """Removes the instance that was created by mouse movement"""
        if self.last_instance is not None:
            self.app.editor.delete_instance(self.last_instance)
        self.last_instance = None
        self.last_mouse_pos = None

    def cb_map_moved(self, click_point):
        """Called when a the mouse was moved over the map

        Args:

            click_point: A fife.ScreenPoint with the the position the mouse is
            on the screen
        """
        if not self.is_active:
            return
        self.clean_mouse_instance()
        if self.app.editor_gui.selected_layer is None or not self.is_active:
            return
        if self.selected_object[0] is None:
            return
        layer = self.app.current_map.get_layer(
            self.app.editor_gui.selected_layer)
        location = self.app.screen_coords_to_map_coords(
            click_point, self.app.editor_gui.selected_layer
        )
        coords = location.getLayerCoordinates()
        self.last_mouse_pos = location
        object_data = reversed(self.selected_object)
        self.last_instance = self.app.editor.create_instance(layer, coords,
                                                             object_data,
                                                             "__editor_mouse")
        fife.InstanceVisual.create(self.last_instance)
        self.last_instance.setRotation(self.cur_rotation)

    def cb_key_pressed(self, event):
        """Called when a key was pressed"""
        if event.getKey().getValue() == fife.Key.R:
            namespace, name = self.selected_object
            if namespace is not None:
                identifier = ".".join((namespace, name))
                directions = self.image_directions[identifier]
                new_index = directions.index(self.cur_rotation) + 1
                if new_index < len(directions):
                    self.cur_rotation = directions[new_index]
                else:
                    self.cur_rotation = directions[0]
                if self.last_instance is not None:
                    self.last_instance.setRotation(self.cur_rotation)

    def cb_project_closed(self):
        """Called when the current project was closed"""
        self.namespaces = {}
        self.images_lock.acquire()
        for image in self.images:
            PyCEGUI.ImageManager.getSingleton().destroy(image)
        self.images = {}
        self.images_lock.release()
        self.selected_object = [None, None]
        if self.items:
            self.items_panel.destroyChild(self.items)
        self.items = self.items_panel.createChild("VerticalLayoutContainer",
                                                  "Items")

    def cb_objects_imported(self):
        """Called when objects where imported to the project"""
        self.have_objects_changed = True
