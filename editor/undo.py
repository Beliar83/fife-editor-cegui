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

""" Contains handling of undoing undo_actions.

.. module:: undo
    :synopsis: Handling of undoing undo_actions.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
from copy import copy
import six


class UndoError(Exception):

    """Exception that is raised when trying to undo or redo when the list
    was empty"""
    pass


class UndoableAction(six.with_metaclass(ABCMeta, object)):
    """An Action that can be undone"""

    def __init__(self, description):
        self.description = description

    @abstractmethod
    def redo(self):
        """Do or redo the action"""

    @abstractmethod
    def undo(self):
        """Undo the action"""


class UndoManager(object):

    """Manages undoing of undo_actions"""

    def __init__(self, max_undo=50):
        self.max_undo = max_undo
        self.undo_actions = []
        self.redo_actions = []

    @property
    def undo_count(self):
        """Returns the number of undoable actions"""
        return len(self.undo_actions)

    @property
    def redo_count(self):
        """Returns the number of redoable actions"""
        return len(self.redo_actions)

    def add_action(self, action):
        """Adds a single action to the action_list

        Args:

            Action that should be added

        """
        self.redo_actions = []
        if len(self.undo_actions) >= self.max_undo:
            del self.undo_actions[0]
        self.undo_actions.append(action)

    def get_next_undo_action(self):
        """Get the undo action that would be performed with a call to
        :py:meth:`.undo_action`"""
        return self.undo_actions[-1]

    def get_next_redo_action(self):
        """Get the redo action that would be performed with a call to
        :py:meth:`.redo_action`"""
        return self.redo_actions[-1]

    def undo_action(self):
        """Undoes the last added action"""
        try:
            action = self.undo_actions.pop()
            action.undo()
            if len(self.redo_actions) >= self.max_undo:
                del self.redo_actions[0]
            self.redo_actions.append(action)
        except IndexError:
            raise UndoError("Nothing to undo")

    def redo_action(self):
        """Redo the last undone action"""
        try:
            action = self.redo_actions.pop()
            action.redo()
            if len(self.undo_actions) >= self.max_undo:
                del self.undo_actions[0]
            self.undo_actions.append(action)

        except IndexError:
            raise UndoError("Nothing to redo")
