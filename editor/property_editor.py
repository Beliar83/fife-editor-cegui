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
    WIDGET_MARGIN = PyCEGUI.UBox(PyCEGUI.UDim(0.005, 0), PyCEGUI.UDim(0.0, 0),
                                 PyCEGUI.UDim(0.005, 0), PyCEGUI.UDim(0.0, 0))

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
        self.properties_pane.setSize(size)
        self.properties_area = self.properties_pane.createChild(
            "VerticalLayoutContainer")
        self.sections = {}
        self.__value_changed_callbacks = []
        self.__list_items = []
        self.property_types = []
        self.section_areas = {}
        self.section_headers = {}
        self.collapse_labels = {}

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
        self.section_areas = {}
        self.__list_items = []
        self.properties_area.destroy()
        self.properties_area = self.properties_pane.createChild(
            "VerticalLayoutContainer")

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

    def set_property(self, section, property_name, property_data):
        """Sets the value of a property

        Args:

            section: The name of the section

            property_name: The name of the property

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
            else:
                print "Could not find editor for %s" % property_name
        else:
            self.sections[section][property_name].update_data(property_data)

    def add_property_type(self, property_type):
        """Adds a property type to the end of the list.

        Args:

            property_type: The property type to add
        """
        self.property_types.append(property_type)

    def update_widgets(self):
        """Update the editors widgets"""
        area = self.properties_area
        for section, properties in self.sections.iteritems():
            if section in self.section_areas:
                section_area = self.section_areas[section]
            else:
                section_header = area.createChild("HorizontalLayoutContainer",
                                                  "%s_header" % section)
                self.section_headers[section] = section_header
                collapse_label = section_header.createChild(
                    "TaharezLook/Label",
                    "%s_collapse"
                    % section)
                collapse_label.setText("-")
                collapse_label.subscribeEvent(PyCEGUI.Window.EventMouseClick,
                                              (lambda args, section=section:
                                               self.cb_un_collapse_clicked(
                                                   args, section)))
                collapse_label.setWidth(PyCEGUI.UDim(0.1, 0))
                self.collapse_labels[section] = collapse_label

                section_label = section_header.createChild("TaharezLook/Label",
                                                           "%s_label"
                                                           % section)
                section_label.setText(section)
                section_label.setWidth(PyCEGUI.UDim(0.98, 0.0))
                section_label.setHeight(self.WIDGET_HEIGHT)
                section_label.setMargin(self.WIDGET_MARGIN)
                section_label.setProperty("HorzFormatting",
                                          "CentreAligned")
                section_area = area.createChild("VerticalLayoutContainer",
                                                "%s_area" % section)
                self.section_areas[section] = section_area

            for property_data in properties.itervalues():
                if property_data.base_widget is None:
                    property_data.setup_widget(section_area)
                property_data.update_input_widgets()

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

    def cb_un_collapse_clicked(self, args, section):
        """Called when un_collapse on a section header was clicked"""
        area = self.properties_area
        try:
            PyCEGUI.Exception.setStdErrEnabled(False)
            area.removeChild("%s_area" % section)
            self.collapse_labels[section].setText("+")
        except RuntimeError:
            PyCEGUI.Exception.setStdErrEnabled(True)
            header_pos = area.getPositionOfChild("%s_header" % section)
            area.addChildToPosition(self.section_areas[section],
                                    header_pos + 1)
            self.collapse_labels[section].setText("-")
        self.properties_pane.show()
