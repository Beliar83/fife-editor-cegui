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
import PyCEGUI


class EditorListener(GameSceneListener):

    """The Listener for the editor controller"""

    def __init__(self, engine, gamecontroller=None):
        GameSceneListener.__init__(self, engine, gamecontroller)
        self.callbacks = {}
        self.callbacks["mouse_pressed"] = []
        self.callbacks["mouse_dragged"] = []
        self.middle_container = None
        self.old_mouse_pos = None

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
        application = self.gamecontroller.application
        for callback_data in self.callbacks["mouse_pressed"]:
            func = callback_data["func"]
            kwargs = callback_data["kwargs"]
            if kwargs is None:
                raise RuntimeError("The callback needs keywords args,"
                                   "but they are not set")
            kwargs = kwargs()
            if "layer" not in kwargs.keys() or kwargs["layer"] is None:
                continue
            layer = kwargs["layer"]
            scr_point = application.screen_coords_to_map_coords(
                fife.ScreenPoint(event.getX(), event.getY()), layer
            )
            func(scr_point, event.getButton())

        self.old_mouse_pos = fife.DoublePoint(event.getX(), event.getY())

    def mouseDragged(self, event):  # pylint: disable=C0103,W0221
        """Called when the mouse is moved while a button is being pressed.

        Args:
            event: The mouse event
        """
        application = self.gamecontroller.application
        for callback_data in self.callbacks["mouse_dragged"]:
            func = callback_data["func"]
            kwargs = callback_data["kwargs"]
            if kwargs is None:
                raise RuntimeError("The callback needs keywords args,"
                                   "but they are not set")
            kwargs = kwargs()
            if "layer" not in kwargs.keys() or kwargs["layer"] is None:
                continue
            layer = kwargs["layer"]
            scr_point = application.screen_coords_to_map_coords(
                fife.ScreenPoint(event.getX(), event.getY()), layer
            )
            func(scr_point, event.getButton())
        if event.getButton() == fife.MouseEvent.MIDDLE:
            current_map = application.current_map
            if self.old_mouse_pos is None or current_map is None:
                return
            cur_mouse_pos = fife.DoublePoint(event.getX(), event.getY())
            offset = cur_mouse_pos - self.old_mouse_pos
            offset /= 2
            offset.rotate(current_map.camera.getRotation())
            self.old_mouse_pos = cur_mouse_pos
            print offset.getX()
            print offset.getY()
            current_map.move_camera((offset.getX(), offset.getY()))

    def mouseMoved(self, event):  # pylint: disable=C0103,W0221
        """Called when the mouse was moved.

        Args:
            event: The mouse event
        """
        GameSceneListener.mouseMoved(self, event)
        x_pos, y_pos = event.getX(), event.getY()
        vec = PyCEGUI.Vector2f(x_pos, y_pos)
        if (self.middle_container is None or
                not self.middle_container.isHit(vec)):
            pass


class EditorController(GameSceneController):

    """The controller for the editor"""

    def __init__(self, view, application, outliner=None, listener=None):
        listener = listener or EditorListener(application.engine, self)
        listener.is_outlined = True
        GameSceneController.__init__(self, view, application,
                                     outliner, listener)
        # self.outliner.outline_data = (173, 255, 47, 2)
