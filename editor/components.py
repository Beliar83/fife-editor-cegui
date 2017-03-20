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

"""Contains classes and functions for the components dialog"""

from importlib import import_module

import PyCEGUI
from fife_rpg.components.base import Base as BaseComponent

from .dialog import Dialog
from .common import clear_text


class Components(Dialog):

    """Class that displays a components dialog"""

    MANDATORY_COMPONENTS = ["Agent", "FifeAgent", "General"]

    def __init__(self, app):
        """Constructor"""
        Dialog.__init__(self, app)
        self.available_list = None
        self.current_list = None
        self.current_items = []
        self.available_items = []
        self.project_components = set()
        self.used_bases = set()
        self.components_in_use = set()
        self.move_left = None
        self.move_right = None

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        font = root.getFont()
        btn_height = font.getFontHeight() + 2
        list_width = PyCEGUI.UDim(0.45, 0)
        list_height = PyCEGUI.UDim(0.99, - (2 * btn_height))
        list_buttons_width = PyCEGUI.UDim(0.1, 0)

        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.55, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.55, 4)))
        self.window.setText(_("Project Settings"))
        lists_container = root.createChild("HorizontalLayoutContainer")
        lists_container.setHeight(list_height)
        available_list = lists_container.createChild("TaharezLook/ItemListbox",
                                                     "AvailableComponents")
        available_list.setWidth(list_width)
        available_list.setHeight(list_height)
        evt_selection_changed = PyCEGUI.ItemListbox.EventSelectionChanged
        available_list.subscribeEvent(evt_selection_changed,
                                      self.cb_list_changed)
        available_list.setMultiSelectEnabled(True)
        self.available_list = available_list

        lists_button_container = lists_container.createChild("VerticalLayout"
                                                             "Container")
        lists_button_container.setWidth(list_buttons_width)
        lists_button_container.setHeight(list_height)
        lists_button_container.setVerticalAlignment(PyCEGUI.VA_CENTRE)
        move_left = lists_button_container.createChild("TaharezLook/Button",
                                                       "MoveLeft")
        move_left.setText("<")
        move_left.setWidth(list_buttons_width)
        move_left.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                 self.cb_move_left_clicked)
        move_left.setEnabled(False)
        self.move_left = move_left

        move_right = lists_button_container.createChild("TaharezLook/Button",
                                                        "MoveRight")
        move_right.setText(">")
        move_right.setWidth(list_buttons_width)
        move_right.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_move_right_clicked)
        move_left.setEnabled(True)
        self.move_right = move_right

        current_list = lists_container.createChild("TaharezLook/ItemListbox",
                                                   "CurrentComponents")
        current_list.setWidth(list_width)
        current_list.setHeight(list_height)
        current_list.subscribeEvent(evt_selection_changed,
                                    self.cb_list_changed)
        current_list.setMultiSelectEnabled(True)
        self.current_list = current_list

        layout = root.createChild("HorizontalLayoutContainer")
        layout.setHorizontalAlignment(PyCEGUI.HA_CENTRE)
        layout.setHeight(PyCEGUI.UDim(0, btn_height))
        ed_available = layout.createChild("TaharezLook/Button",
                                          "EditAvaible")
        ed_available.setText(_("Edit Available components"))
        ed_available.setHeight(PyCEGUI.UDim(0, btn_height))
        text_width = font.getTextExtent(ed_available.getText())
        ed_available.setWidth(PyCEGUI.UDim(0, text_width + 30))
        ed_available.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                    self.cb_edit_available_components_clicked)

        self.project_components = set(self.app.project.get("fife-rpg",
                                                           "Components", []))
        for component in self.MANDATORY_COMPONENTS:
            if component not in self.project_components:
                self.project_components.add(component)
        self.update_lists()

    def update_lists(self):
        """Updates the lists to the current state"""
        self.available_list.resetList()
        self.current_list.resetList()
        self.current_items = []
        self.available_items = []
        self.used_bases = set()
        self.components_in_use = set()
        current_components = set()

        for component in self.project_components:
            component_class = self.app.get_component_data(component)[0]
            for dependency in component_class.dependencies:
                current_components.add(dependency.__name__)
            for base in component_class.__bases__:
                if base is BaseComponent:
                    continue
                self.used_bases.add(base.__name__)
            entities = self.app.world[...]
            try:
                ent_comp = getattr(entities, component)
                if ent_comp:
                    self.components_in_use.add(component)
            except AttributeError:
                pass

        for component in self.project_components.copy():
            if component in self.used_bases:
                self.project_components.remove(component)
                continue
            item = self.current_list.createChild("TaharezLook/ListboxItem")
            text = component
            if component in self.components_in_use:
                text = "[colour='FFFF0000']" + text
            item.setText(text)
            self.current_items.append(item)
            current_components.add(component)

        all_components = set(self.app.components.iterkeys())
        for component in all_components - self.project_components:
            item = self.available_list.createChild("TaharezLook/ListboxItem")
            text = component
            if component in self.used_bases:
                text = "[colour='FF0000FF']" + text
            elif component in current_components:
                text = "[colour='FFC0C0C0']" + text
            item.setText(text)
            self.available_items.append(item)
        self.current_list.performChildWindowLayout()
        self.available_list.performChildWindowLayout()

    def get_values(self):
        """Returns the values of the dialog fields"""
        current_items = set()
        for x in xrange(self.current_list.getItemCount()):
            text = self.current_list.getItemFromIndex(x).getText()
            text = clear_text(text)
            current_items.add(text)
        return {"current_items": current_items}

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        return True

    def cb_move_left_clicked(self, args):
        """Callback for a click on the 'Move Left' button"""
        items = []
        item = self.current_list.getFirstSelectedItem()

        while item is not None:
            items.append(item)
            item = self.current_list.getNextSelectedItem()

        for item in items:
            text = item.getText()
            text = clear_text(text)
            if (text in self.components_in_use or
                text in self.MANDATORY_COMPONENTS):
                continue
            index = self.current_list.getItemIndex(item)
            self.current_list.removeItem(item)
            del self.current_items[index]
            item = self.available_list.createChild("TaharezLook/ListboxItem")
            item.setText(text)
            self.project_components.remove(text)
            self.available_items.append(item)
        self.current_list.performChildWindowLayout()
        self.available_list.performChildWindowLayout()
        self.update_lists()
        self.cb_list_changed(None)

    def cb_move_right_clicked(self, args):
        """Callback for a click on the 'Move Right' button"""
        items = []
        item = self.available_list.getFirstSelectedItem()

        while item is not None:
            items.append(item)
            item = self.available_list.getNextSelectedItem()

        for item in items:
            text = item.getText()
            if text.lower().startswith("[colour"):
                text = text[text.find("]") + 1:]
            if text in self.used_bases:
                continue
            index = self.available_list.getItemIndex(item)
            self.available_list.removeItem(item)
            del self.available_items[index]
            item = self.current_list.createChild("TaharezLook/ListboxItem")
            item.setText(text)
            self.project_components.add(text)
            self.current_items.append(item)
        self.current_list.performChildWindowLayout()
        self.available_list.performChildWindowLayout()
        self.update_lists()
        self.cb_list_changed(None)

    def cb_list_changed(self, args):
        """Called when the selected items of a list were changed"""
        items = []
        item = self.current_list.getFirstSelectedItem()
        has_non_mandatory = False
        while item is not None:
            if item.getText() not in self.MANDATORY_COMPONENTS:
                has_non_mandatory = True
            item = self.current_list.getNextSelectedItem()
        if not has_non_mandatory:
            self.move_left.setEnabled(False)
        else:
            self.move_left.setEnabled(self.current_list.getSelectedCount() > 0)
        self.move_right.setEnabled(self.available_list.getSelectedCount() > 0)

    def cb_edit_available_components_clicked(self, args):
        """Callback for a click on the 'Edit available components' button"""
        self.app.edit_available_components()
        self.app.current_dialog = self
        self.project_components = (self.project_components &
                                   set(self.app.components.keys()))
        self.update_lists()


class AvailableComponents(Dialog):

    """Dialog for editing the available components"""

    def __init__(self, app):
        """Constructor"""
        Dialog.__init__(self, app)
        self.edit_set = None
        self.text_input = None
        self.add_button = None
        self.delete_button = None
        self.items = []
        self.values = dict()
        self.components_in_use = set()

    def setup_dialog(self, root):
        """Sets up the dialog windows

        Args:

            root: The root window to which the windows should be added
        """
        self.components_in_use = set()
        project_components = set(self.app.project.get("fife-rpg", "Components",
                                                      []))
        entities = self.app.world[...]
        for component in project_components:
            try:
                ent_comp = getattr(entities, component)
                if ent_comp:
                    self.components_in_use.add(component)
            except AttributeError:
                pass

        font = root.getFont()
        text_height = font.getFontHeight() + 2
        self.window.setArea(PyCEGUI.UDim(0, 3), PyCEGUI.UDim(0, 4),
                            PyCEGUI.UDim(0.4, 3), PyCEGUI.UDim(0.5, 4))
        self.window.setMinSize(PyCEGUI.USize(PyCEGUI.UDim(0.4, 3),
                                             PyCEGUI.UDim(0.5, 4)))
        self.window.setText(_("Available Components"))

        set_size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0), PyCEGUI.UDim(0.8, 0))
        edit_set = root.createChild("TaharezLook/ItemListbox",
                                    "EditComponents")
        edit_set.setSize(set_size)
        edit_set.subscribeEvent(PyCEGUI.ItemListbox.EventSelectionChanged,
                                self.cb_edit_set_changed)
        edit_set.resetList()
        self.items = []
        self.values = dict()
        for name, path in self.app.components.iteritems():
            text = name
            if name in self.components_in_use:
                text = text = "[colour='FFFF0000']" + text
            item = edit_set.createChild("TaharezLook/ListboxItem")
            item.setText(text)
            self.items.append(item)
            self.values[name] = path
        edit_set.performChildWindowLayout()
        self.edit_set = edit_set
        text_input = root.createChild("TaharezLook/Editbox", "text_input")
        text_input.setHeight(PyCEGUI.UDim(0.0, text_height))
        text_input.setWidth(PyCEGUI.UDim(1.0, 0))
        text_input.subscribeEvent(PyCEGUI.Editbox.EventTextChanged,
                                  self.cb_text_changed)
        self.text_input = text_input

        buttons_layout = root.createChild("HorizontalLayoutContainer",
                                          "buttons_layout")
        buttons_layout.setHorizontalAlignment(PyCEGUI.HA_CENTRE)
        add_button = buttons_layout.createChild("TaharezLook/Button",
                                                "add_button")
        add_button.setText("Add")
        add_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        add_button.setEnabled(False)
        add_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                  self.cb_add_clicked)
        self.add_button = add_button
        delete_button = buttons_layout.createChild("TaharezLook/Button",
                                                   "delete_button")
        delete_button.setText("Delete")
        delete_button.setHeight(PyCEGUI.UDim(0.0, text_height))
        delete_button.setEnabled(False)
        delete_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                     self.cb_delete_clicked)
        self.delete_button = delete_button

    def cb_edit_set_changed(self, args):
        """Called when something in the set was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        self.delete_button.setEnabled(args.window.getSelectedCount() > 0)

    def cb_text_changed(self, args):
        """Called when the editbox was changed

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        text = args.window.getText()
        self.add_button.setEnabled(len(text) > 0 and text not in self.values)

    def cb_add_clicked(self, args):
        """Called when the add button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        module_path = self.text_input.getText()
        path_split = module_path.split(".")
        module_name = ".%s" % path_split[-1]
        base_path = ".".join(path_split[:-1])
        try:
            module = import_module(module_name, base_path)
        except ImportError:
            return
        for member in dir(module):
            component = getattr(module, member)
            try:
                if (issubclass(component, BaseComponent) and
                        component is not BaseComponent):
                    component_name = component.__name__
                    if ("." in component.__module__ and
                            component.__module__ != module_path):
                        continue
                    if component_name not in self.values:
                        self.values[component_name] = module_path
                        item = self.edit_set.createChild("TaharezLook/"
                                                         "ListboxItem")
                        item.setText(component_name)
                        self.items.append(item)
            except TypeError:
                pass
        self.edit_set.performChildWindowLayout()

    def cb_delete_clicked(self, args):
        """Called when the delete button was clicked

        Args:

            args: PyCEGUI.WindowEventArgs
        """
        item = self.edit_set.getFirstSelectedItem()
        text = clear_text(item.getText())
        if text in self.components_in_use:
            return
        del self.values[text]
        self.edit_set.removeItem(item)

    def get_values(self):
        return {"components": self.values.copy()}

    def validate(self):
        """Check if the current state of the dialog fields is valid"""
        return True
