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

""" Contains the game scene and listener for the editor

.. module:: editor_scene
    :synopsis: Contains the game scene and listener for the editor

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife
from fife_rpg.game_scene import GameSceneListener, GameSceneController


class EditorListener(GameSceneListener, fife.IKeyListener):

    """The Listener for the editor controller"""

    DRAG_SPEED = 0.2

    def __init__(self, engine, gamecontroller=None):
        GameSceneListener.__init__(self, engine, gamecontroller)
        fife.IKeyListener.__init__(self)
        self.callbacks = {}
        self.callbacks["mouse_pressed"] = []
        self.callbacks["mouse_dragged"] = []
        self.callbacks["mouse_moved"] = []
        self.middle_container = None
        self.old_mouse_pos = None

    def activate(self):
        """Makes the listener receive events"""
        GameSceneListener.activate(self)
        self.eventmanager.addKeyListener(self)

    def deactivate(self):
        """Makes the listener receive events"""
        GameSceneListener.deactivate(self)
        self.eventmanager.removeKeyListener(self)

    def setup_cegui(self):
        """Sets up cegui events for the listener"""
        main_container = self.gamecontroller.application.main_container
        self.middle_container = main_container.getChild("MiddleContainer"
                                                        "/MiddleArea")

    def add_callback(self, cb_type, cb_func, cb_kwargs=None):
        """Adds a function to call when a event with the type is called

        Args:

            cb_type: Type of the callback (Example 'mouse_pressed')

            cb_func: Callable that will be called when the event occurred

            cb_kwargs:func: Function that returns kwargs for the callback
        """
        if cb_type not in self.callbacks.keys():
            raise RuntimeError("%s is not a valid callback type" % (cb_type))
        self.callbacks[cb_type].append({"func": cb_func, "kwargs": cb_kwargs})

    def mousePressed(self, event):  # pylint: disable=W0221
        self.middle_container.activate()
        for callback_data in self.callbacks["mouse_pressed"]:
            func = callback_data["func"]
            click_point = fife.ScreenPoint(event.getX(), event.getY())
            func(click_point, event.getButton())

        self.old_mouse_pos = fife.DoublePoint(event.getX(), event.getY())

    def mouseDragged(self, event):  # pylint: disable=C0103,W0221
        """Called when the mouse is moved while a button is being pressed.

        Args:
            event: The mouse event
        """
        self.middle_container.activate()
        application = self.gamecontroller.application
        for callback_data in self.callbacks["mouse_dragged"]:
            func = callback_data["func"]
            click_point = fife.ScreenPoint(event.getX(), event.getY())
            func(click_point, event.getButton())
        if event.getButton() == fife.MouseEvent.MIDDLE:
            current_map = application.current_map
            if self.old_mouse_pos is None or current_map is None:
                return
            cursor = application.engine.getCursor()
            cursor.setPosition(int(self.old_mouse_pos.getX()),
                               int(self.old_mouse_pos.getY()))
            cur_mouse_pos = fife.DoublePoint(event.getX(), event.getY())
            offset = cur_mouse_pos - self.old_mouse_pos
            offset *= self.DRAG_SPEED
            offset.rotate(current_map.camera.getRotation())
            current_map.move_camera_by((offset.getX(), offset.getY()))

    def mouseMoved(self, event):  # pylint: disable=C0103,W0221
        """Called when the mouse was moved.

        Args:
            event: The mouse event
        """
        for callback_data in self.callbacks["mouse_moved"]:
            func = callback_data["func"]
            click_point = fife.ScreenPoint(event.getX(), event.getY())
            func(click_point)
        GameSceneListener.mouseMoved(self, event)

    def keyPressed(self, event):  # pylint: disable=C0103,W0221
        """Called when a key was pressed

        Args:

            event: The key event
        """
        if event.getKey().getValue() == fife.Key.SPACE:
            application = self.gamecontroller.application
            if application.current_map is None:
                return
            application.current_map.move_camera_to((0, 0))

    def keyReleased(self, event):  # pylint: disable=C0103,W0221
        """Called when a key was released

        Args:

            event: The key event
        """
        pass


class EditorController(GameSceneController):

    """The controller for the editor"""

    def __init__(self, view, application, outliner=None, listener=None):
        listener = listener or EditorListener(application.engine, self)
        GameSceneController.__init__(self, view, application,
                                     outliner, listener)
