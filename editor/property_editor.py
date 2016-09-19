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

""" Contains the property editor

.. module:: object_toolbar
    :synopsis: Contains the property editor

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from __future__ import print_function
import PyCEGUI
import six


class PropertyEditor(object):

    """Class containing the logic for a property editor"""

    WIDGET_HEIGHT = PyCEGUI.UDim(0.05, 0)
    WIDGET_MARGIN = PyCEGUI.UBox(PyCEGUI.UDim(0.005, 0), PyCEGUI.UDim(0.0, 0),
                                 PyCEGUI.UDim(0.005, 0), PyCEGUI.UDim(0.0, 0))
    COLLAPSE_WIDTH = PyCEGUI.UDim(0.0, 10)
    REMOVE_WIDTH = PyCEGUI.UDim(0.0, 10)

    def __init__(self, root, app):
        self.app = app
        size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0),
                             PyCEGUI.UDim(1.0, 0))
        self.properties_box = root.createChild(
            "TaharezLook/GroupBox", "properties_box")
        self.properties_box.setSize(size)
        self.properties_box.setText("Properties")
        self.properties_pane = self.properties_box.createChild(
            "TaharezLook/ScrollablePane", "property_container")
        self.properties_pane.setShowVertScrollbar(True)
        self.properties_pane.setSize(size)
        self.properties_area = self.properties_pane.createChild(
            "VerticalLayoutContainer")
        self.sections = {}
        self.__value_changed_callbacks = []
        self.__list_items = []
        self.property_types = []
        self.remove_callbacks = set()
        self.__enable_add = False
        self.__add_callback = None
        self.add_button = None
        self.__add_text = None

    @property
    def enable_add(self):
        """Sets whether to add an "Add" Button to the property editor"""
        return self.__enable_add

    @enable_add.setter
    def enable_add(self, value):
        """Setter for "enable_add" """
        self.__enable_add = value
        self.update_widgets()

    @property
    def add_callback(self):
        """Sets the function to call when "Add" was clicked"""
        noop = lambda args: None
        return self.__add_callback or noop

    @add_callback.setter
    def add_callback(self, value):
        """Setter for "add_callback" """
        self.__add_callback = value
        self.update_widgets()

    @property
    def add_text(self):
        """The text that will be displayed on the Add button.

        If set to None the default value will be used"""
        return self.__add_text or _("Add")

    @add_text.setter
    def add_text(self, value):
        """Setter for add_text"""
        self.__add_text = value

    def set_size(self, size):
        """Sets the size of the property editor

        Args:

            size: The size of the editor as a PyCEGUI.USize
        """
        self.properties_box.setSize(size)
        self.properties_area.setSize(size)

    def clear_properties(self):
        """Removed all sections and sections"""
        self.sections = {}
        self.__list_items = []
        self.add_button = None
        self.properties_area.destroy()
        self.properties_area = self.properties_pane.createChild(
            "VerticalLayoutContainer")

    def add_section(self, section, update=True, flags=None):
        """Adds a section to the editor.

        Args:

            section: The name of the section to add

            update: Update the widgets after adding the section

            flags: List of flags for this section
        """
        if flags is None:
            flags = set()
        else:
            flags = set(flags)
        if section not in list(self.sections.keys()):
            self.sections[section] = {}
            self.set_section_flags(section, flags)
            self.sections[section]["properties"] = {}
            self.sections[section]["area"] = None
            if update:
                self.update_widgets()
        else:
            error = "Tried to add already present section %s" % (section)
            raise RuntimeError(error)

    def set_section_flags(self, section, flags):
        """Set the flags for a section

        Args:

            section: The name of the section

            flags: List of flags for this section
        """
        if section not in list(self.sections.keys()):
            raise ValueError("The section %s does not exist" % section)
        else:
            self.sections[section]["flags"] = flags

    def add_section_flag(self, section, flag):
        """Add a flag to a section

        Args:

            section: The name of the section

            flag: The flag to add
        """
        if section not in list(self.sections.keys()):
            raise ValueError("The section %s does not exist" % section)
        else:
            self.sections[section]["flags"].add(flag)

    def remove_section_flag(self, section, flag):
        """Remove a flag from a section

        Args:

            section: The name of the section

            flag: The flag to remove
        """
        if section not in list(self.sections.keys()):
            raise ValueError("The section %s does not exist" % section)
        else:
            try:
                self.sections[section]["flags"].remove(flag)
            except KeyError:
                raise ValueError(("The section %s did not have the "
                                  "flag %s set") % (section, flag))

    def set_property(self, section, property_name, property_data):
        """Sets the value of a property

        Args:

            section: The name of the section

            property_name: The name of the property

            property_data: Property dependent information
        """
        if section not in list(self.sections.keys()):
            self.add_section(section, False)
        if property_name not in self.sections[section]["properties"]:
            section_data = self.sections[section]["properties"]
            for property_type in self.property_types:
                if property_type.check_type(property_data):
                    section_data[property_name] = property_type(self, section,
                                                                property_name,
                                                                property_data)
                    break
            else:
                print("Could not find editor for %s" % property_name)
        else:
            property_ = self.sections[section]["properties"][property_name]
            property_.update_data(property_data)

    def add_property_type(self, property_type):
        """Adds a property type to the end of the list.

        Args:

            property_type: The property type to add
        """
        self.property_types.append(property_type)

    def update_widgets(self):
        """Update the editors widgets"""
        area = self.properties_area
        for section in six.iterkeys(self.sections):
            properties = self.sections[section]["properties"]
            flags = self.sections[section]["flags"]
            if self.sections[section]["area"] is not None:
                section_area = self.sections[section]["area"]
            else:
                label_width = PyCEGUI.UDim(1.0, 0)
                section_header = area.createChild("HorizontalLayoutContainer",
                                                  "%s_header" % section)
                self.sections[section]["header"] = section_header
                collapse_label = section_header.createChild(
                    "TaharezLook/Label",
                    "%s_collapse"
                    % section)
                collapse_label.setText("-")
                collapse_label.subscribeEvent(PyCEGUI.Window.EventMouseClick,
                                              (lambda args, section=section:
                                               self.cb_un_collapse_clicked(
                                                   args, section)))
                collapse_label.setWidth(self.COLLAPSE_WIDTH)
                self.sections[section]["collapse_label"] = collapse_label
                label_width -= self.COLLAPSE_WIDTH
                section_label = section_header.createChild("TaharezLook/Label",
                                                           "%s_label"
                                                           % section)
                section_label.setText(section)
                section_label.setHeight(self.WIDGET_HEIGHT)
                section_label.setMargin(self.WIDGET_MARGIN)
                section_label.setProperty("HorzFormatting",
                                          "CentreAligned")

                if "removable" in flags:
                    remove_label = section_header.createChild(
                        "TaharezLook/Label",
                        "%s_remove"
                        % section)
                    remove_label.setText("X")
                    remove_label.setWidth(self.REMOVE_WIDTH)
                    remove_label.subscribeEvent(PyCEGUI.Window.EventMouseClick,
                                                (lambda args, section=section:
                                                 self.cb_remove_clicked(
                                                     args, section)))
                    self.sections[section]["remove_label"] = remove_label
                    label_width -= self.REMOVE_WIDTH
                else:
                    self.sections[section]["remove_label"] = None
                section_label.setWidth(label_width)

                section_area = area.createChild("VerticalLayoutContainer",
                                                "%s_area" % section)
                self.sections[section]["area"] = section_area

            for property_data in six.itervalues(properties):
                if property_data.base_widget is None:
                    property_data.setup_widget(section_area)
                property_data.update_input_widgets()
        if self.enable_add:
            if self.add_button is None:
                add_button = area.createChild("TaharezLook/Button",
                                              "AddProperty")
                add_button.setWidth(PyCEGUI.UDim(1.0, 0))
                self.add_button = add_button
            else:
                add_button = area.getChild("AddProperty")
            area.moveChildToPosition(add_button, area.getChildCount())
            add_button.setText(self.add_text)
            add_button.subscribeEvent(PyCEGUI.ButtonBase.EventMouseClick,
                                      self.add_callback)
        else:
            if self.add_button is not None:
                area.destroyChild(self.add_button)
                self.add_button = None

    def add_value_changed_callback(self, function):
        """Adds a function to be called when a value has changed

        Args:

            function: The function to be added
        """
        self.__value_changed_callbacks.append(function)

    def send_value_changed(self, section, property_name, value):
        """Send a value changed callback.

        Args:

            section: The section the property belongs to.

            property_name: The name of the property which value has changed.

            value: The new value of the property
        """
        for callback in self.__value_changed_callbacks:
            callback(section, property_name, value)

    def add_remove_callback(self, callback):
        """Add a function to be called when a section was removed

        Args:

            callback: The function to be added
        """
        self.remove_callbacks.add(callback)

    def cb_un_collapse_clicked(self, args, section):
        """Called when un_collapse on a section header was clicked

        Args:

            args: PyCEGUI event args

            section: The name of the section
        """
        area = self.properties_area
        try:
            PyCEGUI.Exception.setStdErrEnabled(False)
            area.removeChild("%s_area" % section)
            self.sections[section]["collapse_label"].setText("+")
        except RuntimeError:
            PyCEGUI.Exception.setStdErrEnabled(True)
            header_pos = area.getPositionOfChild("%s_header" % section)
            area.addChildToPosition(self.sections[section]["area"],
                                    header_pos + 1)
            self.sections[section]["collapse_label"].setText("-")
        self.properties_pane.show()

    def cb_remove_clicked(self, args, section):
        """Called when the "X" on the right side of a section header was
        clicked

        Args:

            args: PyCEGUI event args

            section: The name of the section
        """
        section_data = self.sections[section]
        window_manager = PyCEGUI.WindowManager.getSingleton()
        window_manager.destroyWindow(section_data["header"])
        window_manager.destroyWindow(section_data["area"])
        del self.sections[section]
        for callback in self.remove_callbacks:
            callback(section)
