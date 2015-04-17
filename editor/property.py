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

""" Contains the property classes

.. module:: property
    :synopsis: Contains the property classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from abc import ABCMeta, abstractmethod
from .list_editor import ListEditor

import PyCEGUI


class BaseProperty(object):

    """Base class for properties"""

    __metaclass__ = ABCMeta

    def __init__(self, editor, section, name, value_data):
        self.editor = editor
        self.section = section
        self.name = name
        self.value_data = value_data

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        raise NotImplementedError("Method \"check_type\" was not overridden.")

    def _create_base_widget(self, root, y_pos):
        """Create the base widget for the editor

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget
        """
        base_text = "/".join((self.section, self.name))
        property_container = root.createChild(
            "HorizontalLayoutContainer", "%s_container" % (base_text))
        property_container.setYPosition(y_pos)
        property_label = property_container.createChild(
            "TaharezLook/Label", "%s_label" % (base_text))
        property_label.setProperty(
            "HorzFormatting", "LeftAligned")
        property_label.setWidth(PyCEGUI.UDim(0.5, 0))
        property_label.setHeight(self.editor.WIDGET_HEIGHT)
        property_label.setText(self.name)
        property_label.setTooltipText(self.name)
        return base_text, property_container

    @abstractmethod
    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """


class ComboProperty(BaseProperty):

    """Class for a combo property"""

    def __init__(self, editor, section, name, value_data):
        BaseProperty.__init__(self, editor, section, name, value_data)
        self.__list_items = []

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 2:
            return False
        try:
            iter(value_data[1])
        except TypeError:
            return False
        value_type = type(value_data[0])
        for value in value_data[1]:
            if type(value) != value_type:
                return False
        return True

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        self.__list_items = []
        base_text, container = self._create_base_widget(root, y_pos)
        possible_values = self.value_data[0]
        start_value = str(self.value_data[1])
        property_input = container.createChild(
            "TaharezLook/Combobox", "%s_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.49, 0))
        property_input.setText(start_value)
        property_input.setTooltipText(start_value)
        property_input.selectListItemWithEditboxText()
        property_input.subscribeEvent(
            PyCEGUI.Combobox.EventListSelectionAccepted,
            self.cb_value_changed)
        for value in possible_values:
            item = PyCEGUI.ListboxTextItem(str(value))
            item.setSelectionBrushImage("TaharezLook/"
                                        "MultiListSelectionBrush")
            property_input.addItem(item)
            self.__list_items.append(item)

    def cb_value_changed(self, args):
        """Called when the value of the widget was changed

        Args:

            args: PyCEGUI event args
        """
        window = args.window
        new_value = unicode(window.getText())
        window.setTooltipText(new_value)
        self.editor.send_value_changed(self.section,
                                       self.name,
                                       new_value)


class ToggleProperty(BaseProperty):

    """Class for toggleable properties"""

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 1:
            return False
        return isinstance(value_data[0], bool)

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        base_text, container = self._create_base_widget(root, y_pos)
        start_value = self.value_data[0]
        property_input = container.createChild(
            "TaharezLook/Checkbox", "%s_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.49, 0))
        property_input.setSelected(start_value)
        property_input.subscribeEvent(
            PyCEGUI.ToggleButton.EventSelectStateChanged,
            self.cb_value_changed)

    def cb_value_changed(self, args):
        """Called when the value of toggle button/checkbox was changed

        Args:

            args: PyCEGUI event args
        """
        self.editor.send_value_changed(self.section,
                                       self.name,
                                       args.window.isSelected())


class PointProperty(BaseProperty):

    """Class for point properties"""

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 1:
            return False
        try:
            return len(value_data[0]) == 2
        except TypeError:
            return False

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        base_text, container = self._create_base_widget(root, y_pos)
        x_pos = unicode(self.value_data[0][0])
        y_pos = unicode(self.value_data[0][1])
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_x_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.245, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText(x_pos)
        property_input.setTooltipText(x_pos)
        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_y_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.245, 0))
        property_input.setYPosition(PyCEGUI.UDim(0.245, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText(y_pos)
        property_input.setTooltipText(y_pos)
        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)

    def cb_value_changed(self, args):
        """Called when the value of a point was changed

        Args:

            args: PyCEGUI event args
        """
        area = self.editor.properties_area
        base_text = "/".join((self.section, self.name))
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
            self.editor.send_value_changed(self.section,
                                           self.name,
                                           pos)
        except ValueError:
            self.editor.update_widgets()


class Point3DProperty(BaseProperty):

    """Class for point3d properties"""

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 1:
            return False
        try:
            return len(value_data[0]) == 3
        except TypeError:
            return False

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        base_text, container = self._create_base_widget(root, y_pos)
        x_pos = unicode(self.value_data[0][0])
        y_pos = unicode(self.value_data[0][1])
        z_pos = unicode(self.value_data[0][2])
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_x_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.163, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText((x_pos))
        property_input.setTooltipText(x_pos)
        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_y_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.163, 0))
        property_input.setYPosition(PyCEGUI.UDim(0.163, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText(y_pos)
        property_input.setTooltipText(y_pos)
        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_z_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.163, 0))
        property_input.setYPosition(PyCEGUI.UDim(0.326, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText(z_pos)
        property_input.setTooltipText(z_pos)
        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)

    def cb_value_changed(self, args):
        """Called when the value of a point was changed

        Args:

            args: PyCEGUI event args
        """
        area = self.editor.properties_area
        base_text = "/".join((self.section, self.name))
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
            self.editor.send_value_changed(self.section,
                                           self.name,
                                           pos)
        except ValueError:
            self.editor.update_widgets()


class TextProperty(BaseProperty):

    """Class for a text property"""

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 1:
            return False
        return isinstance(value_data[0], basestring)

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        base_text, container = self._create_base_widget(root, y_pos)
        start_value = str(self.value_data[0])
        property_input = container.createChild(
            "TaharezLook/Editbox", "%s_input" % (base_text))
        property_input.setWidth(PyCEGUI.UDim(0.49, 0))
        property_input.setHeight(self.editor.WIDGET_HEIGHT)
        property_input.setText(start_value)
        property_input.setTooltipText(start_value)

        property_input.subscribeEvent(
            PyCEGUI.Editbox.EventTextAccepted,
            self.cb_value_changed)

    def cb_value_changed(self, args):
        """Called when the text value of a widget was changed

        Args:

            args: PyCEGUI event args
        """
        window = args.window
        new_value = unicode(window.getText())
        window.setTooltipText(new_value)
        self.editor.send_value_changed(self.section, self.name, new_value)


class ListProperty(BaseProperty):

    """Class for a list property"""

    @classmethod
    def check_type(cls, value_data):
        """Checks if the value_data is of the type this class is for

        Args:

            value_data: The value_data to check

        Returns:
            True if the property can handle the type, False if not
        """
        if len(value_data) != 1:
            return False
        return isinstance(value_data[0], list)

    def setup_widget(self, root, y_pos):
        """Sets up the widget for this property

        Args:

            root: The root widget to which to add the widget to

            y_pos: The vertical position of the widget

        """
        base_text, container = self._create_base_widget(root, y_pos)
        property_edit = container.createChild(
            "TaharezLook/Editbox", "%s_edit" % (base_text))
        property_edit.setWidth(PyCEGUI.UDim(0.49, 0))
        property_edit.setHeight(self.editor.WIDGET_HEIGHT)
        property_edit.setText("(list)")
        property_edit.setTooltipText("(list)")
        property_edit.setReadOnly(True)

        property_edit.subscribeEvent(
            PyCEGUI.Editbox.EventMouseClick,
            self.cb_mouse_clicked)

    def cb_mouse_clicked(self, args):
        """Called when the text value of a widget was changed

        Args:

            args: PyCEGUI event args
        """
        dialog = ListEditor(self.editor.app, self.value_data[0])
        dialog.show_modal(self.editor.app.editor_gui.editor_window,
                          self.editor.app.engine.pump)
        if not dialog.return_value:
            return
        values = dialog.get_values()
        self.editor.send_value_changed(self.section, self.name,
                                       values["items"])
