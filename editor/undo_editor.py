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

""" Contains undoable actions for the editor.

.. module:: undo_editor
    :synopsis: Undoable actions for the editor.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

from .undo import UndoableAction


# pylint: disable=abstract-method
class EditorUndoableAction(UndoableAction):

    """Base class for editor actions"""

    def __init__(self, editor, description):
        if False:  # For IDEs
            from .editor import Editor
            self.editor = Editor(None)
        UndoableAction.__init__(self, description)
        self.editor = editor
# pylint: enable=abstract-method


class UndoCreateInstance(EditorUndoableAction):

    """Class for undoing and redoing the creation of instances"""

    def __init__(self, editor, layer_or_layer_data, coords,
                 object_or_object_data, rotation=0, identifier=None):
        EditorUndoableAction.__init__(self, editor, _("Create instance"))
        self.layer_or_layer_data = layer_or_layer_data
        self.coords = coords
        self.object_or_object_data = object_or_object_data
        self.identifier = identifier
        self.rotation = rotation
        self.instance = None

    def redo(self):
        """Calls :py:meth:`.editor.Editor.create_instance` with the variables
        of the action and returns the result."""
        instance = self.editor.create_instance(self.layer_or_layer_data,
                                               self.coords,
                                               self.object_or_object_data,
                                               self.identifier)
        instance.setRotation(self.rotation)
        fife.InstanceVisual.create(instance)

        self.instance = instance
        return instance

    def undo(self):
        """Calls :py:meth:`.editor.Editor.delete_instance` with the variables
        of the action."""
        self.editor.delete_instance(self.instance, self.layer_or_layer_data)
        self.instance = None


class UndoRemoveInstance(EditorUndoableAction):

    """Class for undoing and redoing the removing of instances"""

    def __init__(self, editor, instance):
        EditorUndoableAction.__init__(self, editor, _("Create instance"))
        location = instance.getLocation()
        self.instance = instance
        self.coords = location.getExactLayerCoordinates()
        self.layer = location.getLayer()
        self.object = instance.getObject()
        self.rotation = instance.getRotation()
        self.identifier = instance.getId()

    def redo(self):
        """Calls :py:meth:`.editor.Editor.delete_instance` with the variables
        of the action"""
        self.editor.delete_instance(self.instance)

    def undo(self):
        """Calls :py:meth:`.editor.Editor.delete_instance` with the variables
        of the action."""
        instance = self.editor.create_instance(self.layer, self.coords,
                                               self.object, self.identifier)
        instance.setRotation(self.rotation)
        fife.InstanceVisual.create(instance)
        self.instance = instance
