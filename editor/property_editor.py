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

import PyCEGUI


class PropertyEditor(object):

    """Class containing the logic for a property editor"""

    WIDGET_HEIGHT = PyCEGUI.UDim(0.05, 0)
    WIDGET_MARGIN = PyCEGUI.UDim(0.01, 0)

    def __init__(self, root, app):
        self.app = app
        size = PyCEGUI.USize(PyCEGUI.UDim(1.0, 0),
                             PyCEGUI.UDim(1.0, 0))
        self.properties_box = root.createChild(
            "TaharezLook/GroupBox", "properties_box")
        self.properties_box.setSize(size)
        self.properties_box.setText("Properties")
        self.properties_area = self.properties_box.createChild(
            "TaharezLook/ScrollablePane", "property_container")
        self.properties_area.setSize(size)
        self.sections = {}
        self.__value_changed_callbacks = []
        self.__list_items = []
        self.property_types = []

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
        self.update_widgets()

    def add_section(self, section, update=True):
        """Adds a section to the editor.

        Args:

            section: The name of the section to add

            update: Update the widgets after adding the section
        """
        if section not in self.sections.keys():
            self.sections[section] = {}
            if update:
                self.update_widgets()
        else:
            error = "Tried to add already present section %s" % (section)
            raise RuntimeError(error)

    def add_property(self, section, property_name, property_data):
        """Add a property to the given section

        Args:

            section: The name of the section, to add the property to

            property_name: The name of the property to add

            property_data: Property dependent information
        """
        if section not in self.sections.keys():
            self.add_section(section, False)
        if property_name not in self.sections[section]:
            section_data = self.sections[section]
            for property_type in self.property_types:
                if property_type.check_type(property_data):
                    section_data[property_name] = property_type(self, section,
                                                                property_name,
                                                                property_data)
                    break
            self.update_widgets()
        else:
            error = ("Tried to add already present property %s to section %s"
                     % (property_name, section))
            raise RuntimeError(error)

    def add_property_type(self, property_type):
        """Adds a property type to the end of the list.

        Args:

            property_type: The property type to add
        """
        self.property_types.append(property_type)

    def update_widgets(self):
        """Update the editors widgets"""
        ignored_count = 0
        area = self.properties_area
        while (area.getContentPane().getChildCount() - ignored_count) > 0:
            child = area.getContentPane().getChildAtIdx(ignored_count)
            if child.isAutoWindow():
                ignored_count += 1
                continue
            child.destroy()
        y_pos = PyCEGUI.UDim(0, 0.0)

        for section, properties in self.sections.iteritems():
            section_label = area.createChild("TaharezLook/Label", section)
            section_label.setYPosition(y_pos)
            section_label.setText(section)
            section_label.setWidth(PyCEGUI.UDim(0.99, 0.0))
            section_label.setHeight(self.WIDGET_HEIGHT)
            section_label.setProperty("HorzFormatting", "CentreAligned")
            y_pos += self.WIDGET_HEIGHT
            y_pos += self.WIDGET_MARGIN
            for property_data in properties.itervalues():
                property_data.setup_widget(area, y_pos)
                y_pos += self.WIDGET_HEIGHT
                y_pos += self.WIDGET_MARGIN

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
