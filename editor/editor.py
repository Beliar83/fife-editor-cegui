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

""" Contains the basic classes and functions for editing FIFE maps.

.. module:: editor
    :synopsis: Contains classes and functions for editing FIFE maps.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife import fife


class Editor(object):
    """Contains methods to create and edit maps"""

    def __init__(self, engine):
        """Constructor"""
        self.__model = engine.getModel()
        if 0:
            self.__model = fife.Model()
        self.__map_loader = fife.MapLoader(engine.getModel(),
                                           engine.getVFS(),
                                           engine.getImageManager(),
                                           engine.getRenderBackend())

    def create_map(self, identifier):
        """Creates a new map.

        Args:

            identifier: The name of the new map

        Returns:

            The created map
        """
        return self.__model.createMap(identifier)

    def load_map(self, filename):
        """Load a map from a file

        Args:

            filename: The path to the map file

        Returns:
            The loaded map
        """
        return self.__map_loader.load(filename)

    def delete_map(self, map_or_identifier):
        """Deletes a specific map.

        Args:

            map_or_identifier: A fife.Map instance or the name of the map
        """
        if not isinstance(map_or_identifier, fife.Map):
            map_or_identifier = self.get_map(map_or_identifier)
        self.__model.deleteMap(map_or_identifier)

    def delete_maps(self):
        """Deletes all maps"""
        self.__model.deleteMaps()

    def get_maps(self):
        """Returns a list of all maps of the editor"""
        return self.__model.getMaps()

    def get_map(self, identifier):
        """Returns the map with the identifier.

        Args:

            identifier: The name of the map
        """
        return self.__model.getMap(identifier)

    def get_map_count(self):
        """Returns the number of maps"""
        return self.__model.getMapCount()

    def get_namespaces(self):
        """Returns a list of all namespaces"""
        return self.__model.getNamespaces()

    def create_object(self, identifier, namespace, parent=None):
        """Creates an object

        Args:

            identifier: The name of the object

            namespace: To what namespace the object should be added

            parent: The parent of the object

        Returns:

            The created object
        """
        return self.__model.createObject(identifier, namespace, parent)

    def import_object(self, filename):
        """Imports an object from an object file

        Args:

            filenam: The object file to load
        """
        self.__map_loader.loadImportFile(filename)

    def import_objects(self, directory):
        """Import objects from all objects files in a directory

        Args:

            directory: The directory to look for object files
        """
        self.__map_loader.loadImportDirectory(directory)

    def delete_object(self, object_or_identifier, namespace=None):
        """Removes an object

        Args:

        oject_or_identifier: The object or the name of the object

        namespace: The namespace in which the object should be searched.

        Returns:

            True if object could be deleted, False if there is a map, that
            uses this object.
        """
        if not isinstance(object_or_identifier, fife.Object):
            object_or_identifier = self.get_object(object_or_identifier,
                                                   namespace)
        return self.__model.deleteObject(object_or_identifier)

    def delete_objects(self):
        """Deletes all objects.

        Returns:

            True if objects could be deleted, False if there is a map with
            instances.
        """
        return self.__model.deleteObjects()

    def get_object(self, identifier, namespace):
        """Returns an object from a namespace

        Args:

            identifier: The name of the object

            namespace: The namespace the object belongs to
        """
        return self.__model.getObject(identifier, namespace)

    def get_objects(self, namespace):
        """Returns a list of the objects of a namespace

        Args:

            namespace: The name of the namespace
        """
        return self.__model.getObjects(namespace)
