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

    def __init__(self, root):
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
            self.sections[section][property_name] = property_data
            self.update_widgets()
        else:
            error = ("Tried to add already present property %s to section %s"
                     % (property_name, section))
            raise RuntimeError(error)

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
            for property_name, property_data in properties.iteritems():
                self.__create_property_widget(property_name, section,
                                              property_data, area, y_pos)
                y_pos += self.WIDGET_HEIGHT
                y_pos += self.WIDGET_MARGIN

    def __create_property_widget(self, property_name, section, property_data,
                                 container, y_pos):
        """Create a property widget from the data

        Args:

            property_data: The data of the property

            section: The name of the properties section

            container: The container to which the widget shoud be added

            y_pos: The vertical position of the widget
        """
        base_text = "/".join((section, property_name))
        property_container = container.createChild(
            "HorizontalLayoutContainer", "%s_container" % (base_text))
        property_container.setYPosition(y_pos)
        property_label = property_container.createChild(
            "TaharezLook/Label", "%s_label" % (base_text))
        property_label.setProperty(
            "HorzFormatting", "LeftAligned")
        property_label.setWidth(PyCEGUI.UDim(0.5, 0))
        property_label.setHeight(self.WIDGET_HEIGHT)
        property_label.setText(property_name)
        property_label.setTooltipText(property_name)
        property_type = property_data[0].lower()
        if property_type == "text":
            start_value = str(property_data[1])
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.49, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText(start_value)
            property_input.setTooltipText(start_value)

            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_text_value_changed(section, property_name,
                                                        args))
        elif property_type == "combo":
            possible_values = property_data[1]
            start_value = str(property_data[2])
            property_input = property_container.createChild(
                "TaharezLook/Combobox", "%s_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.49, 0))
            property_input.setText(start_value)
            property_input.setTooltipText(start_value)
            property_input.selectListItemWithEditboxText()
            property_input.subscribeEvent(
                PyCEGUI.Combobox.EventListSelectionAccepted,
                lambda args: self.cb_text_value_changed(section, property_name,
                                                        args))
            for value in possible_values:
                item = PyCEGUI.ListboxTextItem(str(value))
                item.setSelectionBrushImage("TaharezLook/"
                                            "MultiListSelectionBrush")
                property_input.addItem(item)
                self.__list_items.append(item)
        elif property_type == "check":
            start_value = property_data[1]
            property_input = property_container.createChild(
                "TaharezLook/Checkbox", "%s_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.49, 0))
            property_input.setSelected(start_value)
            property_input.subscribeEvent(
                PyCEGUI.ToggleButton.EventSelectStateChanged,
                lambda args: self.cb_toggle_value_changed(section,
                                                          property_name,
                                                          args))
        elif property_type == "point":
            x_pos = unicode(property_data[1][0])
            y_pos = unicode(property_data[1][1])
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_x_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.245, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText(x_pos)
            property_input.setTooltipText(x_pos)
            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_point_value_changed(section,
                                                         property_name,
                                                         args))
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_y_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.245, 0))
            property_input.setYPosition(PyCEGUI.UDim(0.245, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText(y_pos)
            property_input.setTooltipText(y_pos)
            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_point_value_changed(section,
                                                         property_name,
                                                         args))
        elif property_type == "point3d":
            x_pos = unicode(property_data[1][0])
            y_pos = unicode(property_data[1][1])
            z_pos = unicode(property_data[1][2])
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_x_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.163, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText((x_pos))
            property_input.setTooltipText(x_pos)
            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_point3d_value_changed(section,
                                                           property_name,
                                                           args))
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_y_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.163, 0))
            property_input.setYPosition(PyCEGUI.UDim(0.163, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText(y_pos)
            property_input.setTooltipText(y_pos)
            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_point3d_value_changed(section,
                                                           property_name,
                                                           args))
            property_input = property_container.createChild(
                "TaharezLook/Editbox", "%s_z_input" % (base_text))
            property_input.setWidth(PyCEGUI.UDim(0.163, 0))
            property_input.setYPosition(PyCEGUI.UDim(0.326, 0))
            property_input.setHeight(self.WIDGET_HEIGHT)
            property_input.setText(z_pos)
            property_input.setTooltipText(z_pos)
            property_input.subscribeEvent(
                PyCEGUI.Editbox.EventTextAccepted,
                lambda args: self.cb_point3d_value_changed(section,
                                                           property_name,
                                                           args))
        else:
            raise RuntimeError("Don't know the property type %s"
                               % (property_type))

    def cb_text_value_changed(self, section, property_name, args):
        """Called when the text value of a widget was changed

        Args:

            section: The section the edit box belongs to

            property: The property the editbox belongs to

            args: PyCEGUI event args
        """
        window = args.window
        new_value = unicode(window.getText())
        window.setTooltipText(new_value)
        self.__send_value_changed(section,
                                  property_name,
                                  new_value)

    def cb_toggle_value_changed(self, section, property_name, args):
        """Called when the value of toggle button/checkbox was changed

        Args:

            section: The section the edit box belongs to

            property: The property the editbox belongs to

            args: PyCEGUI event args
        """
        self.__send_value_changed(section,
                                  property_name,
                                  args.window.isSelected())

    def cb_point_value_changed(self, section, property_name, args):
        """Called when the value of a point was changed

        Args:

            section: The section the edit box belongs to

            property: The property the editbox belongs to

            args: PyCEGUI event args
        """
        area = self.properties_area
        base_text = "/".join((section, property_name))
        property_container = area.getChildRecursive("%s_container" %
                                                    (base_text))
        x_pos_edit = property_container.getChildRecursive("%s_x_input" %
                                                          (base_text))
        y_pos_edit = property_container.getChildRecursive("%s_y_input" %
                                                          (base_text))
        try:
            x_pos = float(x_pos_edit.getText())
            y_pos = float(y_pos_edit.getText())
            pos = (x_pos, y_pos)
            self.__send_value_changed(section,
                                      property_name,
                                      pos)
        except ValueError:
            self.update_widgets()

    def cb_point3d_value_changed(self, section, property_name, args):
        """Called when the value of a point3d was changed

        Args:

            section: The section the edit box belongs to

            property: The property the editbox belongs to

            args: PyCEGUI event args
        """
        area = self.properties_area
        base_text = "/".join((section, property_name))
        property_container = area.getChildRecursive("%s_container" %
                                                    (base_text))
        x_pos_edit = property_container.getChildRecursive("%s_x_input" %
                                                          (base_text))
        y_pos_edit = property_container.getChildRecursive("%s_y_input" %
                                                          (base_text))
        z_pos_edit = property_container.getChildRecursive("%s_z_input" %
                                                          (base_text))
        try:
            x_pos = float(x_pos_edit.getText())
            y_pos = float(y_pos_edit.getText())
            z_pos = float(z_pos_edit.getText())
            pos = (x_pos, y_pos, z_pos)
            self.__send_value_changed(section,
                                      property_name,
                                      pos)
        except ValueError:
            self.update_widgets()

    def add_value_changed_callback(self, function):
        """Adds a function to be called when a value has changed

        Args:

            function: The function to be added
        """
        self.__value_changed_callbacks.append(function)

    def __send_value_changed(self, section, property_name, value):
        """Send a value changed callback.

        Args:

            section: The section the property belongs to.

            property_name: The name of the property which value has changed.

            value: The new value of the property
        """
        for callback in self.__value_changed_callbacks:
            callback(section, property_name, value)
