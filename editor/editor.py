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
from builtins import object
from fife import fife
from .undo import UndoManager


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
        self.__import_ref_count = {}
        self.undo_manager = UndoManager()

    def reset_data(self):
        """Resets the internal data of the editor instance"""
        self.__import_ref_count = {}

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

        Raises:

            ValueError if there was no map with that identifier
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

        Raises:

            ValueError if there was no map with that identifier
        """
        try:
            return self.__model.getMap(identifier)
        except RuntimeError:
            raise ValueError("A map with the id %s could not be found" % (
                             identifier))

    def get_map_count(self):
        """Returns the number of maps"""
        return self.__model.getMapCount()

    def get_cell_grid(self, grid_type):
        """Returns the cell grid with the given name

        Args:

            grid_type: Name of the cell grid
        """
        return self.__model.getCellGrid(grid_type)

    def create_layer(self, fife_map_id, layer_name, grid_type):
        """Creates a new layer on a map

        Args:

            fife_map_id: The identifier of the map

            layer_name: The identifier of the new layer

            grid_type: A fife.CellGrid or the name of the Grid

        Raises:

            ValueError if the there is already a layer with that name on the
            map or if there was no map with that identifier

        Returns:

            The created layer
        """
        fife_map = self.get_map(fife_map_id)
        if 0:  # Just for IDEs
            assert isinstance(fife_map, fife.Map)
        if fife_map.getLayer(layer_name):
            raise ValueError(
                "The map %s already has a layer named %s" % (
                    fife_map.getId(), layer_name))
        if not isinstance(grid_type, fife.CellGrid):
            grid_type = self.get_cell_grid(grid_type)
        return fife_map.createLayer(layer_name, grid_type)

    def delete_layer(self, fife_map_id, layer):
        """Deletes a layer from a map

        Args:

            fife_map_id: A fife.Map or the identifier of the map

            layer: A fife.Layer or the identifier of the layer

        Raises:

            ValueError if there was no map with that identifier
        """
        fife_map = self.get_map(fife_map_id)
        if 0:  # Just for IDEs
            assert isinstance(fife_map, fife.Map)
        if not isinstance(layer, fife.Layer):
            layer = fife_map.getLayer(layer)
        fife_map.deleteLayer(layer)

    def delete_layers(self, fife_map_id):
        """Deletes all layers from a map

        Args:

            fife_map_id: A fife.Map or the identifier of the map

        Raises:

            ValueError if there was no map with that identifier
        """
        fife_map = self.get_map(fife_map_id)
        if 0:  # Just for IDEs
            assert isinstance(fife_map, fife.Map)
        fife_map.deleteLayers()

    def get_layers(self, map_or_identifier):
        """Returns a list of the layers of a map

        Args:

            map_or_identifier: A fife.Map or the identifier of the map

        Raises:

            ValueError if there was no map with that identifier
        """
        if not isinstance(map_or_identifier, fife.Map):
            map_or_identifier = self.get_map(map_or_identifier)
        return map_or_identifier.getLayers()

    def get_layer(self, map_or_identifier, layer):
        """Get a layer from a map

        Args:

            map_or_identifier: A fife.Map or the identifier of the map

            layer: The identifier of the layer

        Raises:

            ValueError if there was no map with that identifier.

        Returns:

            The layer, if present on the map.
        """
        if not isinstance(map_or_identifier, fife.Map):
            map_or_identifier = self.get_map(map_or_identifier)
        return map_or_identifier.getLayer(layer)

    def get_layer_count(self, fife_map_id):
        """Returns the number of layers on a map

        Args:

            fife_map_id: A fife.Map or the identifier of the map

            layer: The identifier of the layer

        Raises:

            ValueError if there was no map with that identifier
        """
        fife_map = self.get_map(fife_map_id)
        if 0:  # Just for IDEs
            assert isinstance(fife_map, fife.Map)
        return fife_map.getLayerCount()

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

    def create_instance(self, layer_or_layer_data, coords,
                        object_or_object_data, identifier=None):
        """Creates a new instance on the given layer at the given coords using
        the given object.

        Args:

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.

            coords: The coordinates of the new instance.
            fife.ModelCoordinate or fife.ExactModelCoordinate instance or
            a 3 item tuple with number values.

            object_or_object_data: Either a fife.Object instance or a tuple
            with the name and namespace, in that order,
            of the object to use for the instance.

            identifier: The name of the new instance.
        """
        if not isinstance(layer_or_layer_data, fife.Layer):
            layer_or_layer_data = self.get_layer(layer_or_layer_data[1],
                                                 layer_or_layer_data[0])
        try:
            iter(coords)
            coords = fife.ExactModelCoordinate(*coords)
        except TypeError:
            pass
        if not isinstance(object_or_object_data, fife.Object):
            object_or_object_data = self.__model.getObject(
                *object_or_object_data)
        instance = layer_or_layer_data.createInstance(object_or_object_data,
                                                      coords, identifier or "")
        tmp_filename = instance.getObject().getFilename()
        tmp_map_name = layer_or_layer_data.getMap().getId()
        self.increase_refcount(tmp_filename, tmp_map_name)
        return instance

    def add_instance(self, instance, coords, layer_or_layer_data):
        """Adds an instance to a layer

        Args:

            instance: A fife.Instance

            coords: A fife.ExactModelCoordinates instance or a tuple with
            3 values.

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.

        Raises:

            ValueError if there was no map with that identifier.

        """
        if not isinstance(layer_or_layer_data, fife.Layer):
            layer_or_layer_data = self.get_layer(layer_or_layer_data[1],
                                                 layer_or_layer_data[0])
        try:
            iter(coords)
            coords = fife.ExactModelCoordinate(*coords)
        except TypeError:
            pass
        layer_or_layer_data.addInstance(instance, coords)
        tmp_filename = instance.getObject().getFilename()
        tmp_map_name = layer_or_layer_data.getMap().getId()
        self.increase_refcount(tmp_filename, tmp_map_name)

    def delete_instance(self, instance_or_identifier,
                        layer_or_layer_data=None):
        """Deletes an instance

        Args:

            instance_or_identifier: The instance or the name of the instance

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.
            Ignored if instance is an actual instance.

        Raises:

            ValueError if there was no map with that identifier.

        """
        if not isinstance(instance_or_identifier, fife.Instance):
            instance_or_identifier = self.get_instance(instance_or_identifier,
                                                       layer_or_layer_data)
            if not isinstance(layer_or_layer_data, fife.Layer):
                layer_or_layer_data = layer_or_layer_data[0]
                map_or_identifier = layer_or_layer_data[1]
                layer_or_layer_data = self.get_layer(map_or_identifier,
                                                     layer_or_layer_data)
        else:
            tmp_location = instance_or_identifier.getLocation()
            layer_or_layer_data = tmp_location.getLayer()
        filename = instance_or_identifier.getObject().getFilename()
        map_name = layer_or_layer_data.getMap().getId()
        self.decrease_refcount(filename, map_name)
        layer_or_layer_data.deleteInstance(instance_or_identifier)

    def remove_instance(self, instance_or_identifier,
                        layer_or_layer_data=None):
        """Removes an instance

        Args:

            instance_or_identifier: The instance or the name of the instance

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.
            Ignored if instance is an actual instance.

        Returns:

            The removed instance.

        Raises:

            ValueError if there was no map with that identifier.

        """
        if not isinstance(instance_or_identifier, fife.Instance):
            instance_or_identifier = self.get_instance(instance_or_identifier,
                                                       layer_or_layer_data)
            if not isinstance(layer_or_layer_data, fife.Layer):
                layer_or_layer_data = layer_or_layer_data[0]
                map_or_identifier = layer_or_layer_data[1]
                layer_or_layer_data = self.get_layer(map_or_identifier,
                                                     layer_or_layer_data)
        else:
            tmp_location = instance_or_identifier.getLocation()
            layer_or_layer_data = tmp_location.getLayer()
        filename = instance_or_identifier.getObject().getFilename()
        map_name = layer_or_layer_data.getMap().getId()
        self.decrease_refcount(filename, map_name)
        layer_or_layer_data.removeInstance(instance_or_identifier)
        return instance_or_identifier

    def delete_instances_of_map(self, map_or_identifier=None):
        """Deletes all instances of the given layer.

        Returns:

            True if instances could be deleted, False if there is a map with
            instances.

        Raises:

            ValueError if there was no map with that identifier.
        """
        instances = self.get_instances_of_map(map_or_identifier)
        success = True
        for instance in instances:
            if not self.delete_instance(instance):
                success = False
        return success

    def delete_instances_of_layer(self, layer_or_layer_data):
        """Deletes all instances of the given layer.

        Args:

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.

        Returns:

            True if instances could be deleted, False if there is a map with
            instances.

        Raises:

            ValueError if there was no map with that identifier.
        """
        instances = self.get_instances_of_layer(layer_or_layer_data)
        success = True
        for instance in instances:
            if not self.delete_instance(instance):
                success = False
        return success

    def get_instance(self, identifier, layer_or_identifier=None,
                     map_or_identifier=None):
        """Returns an instance from a layer or a map

        Args:

            identifier: The name of the instance

            layer_or_identifier: The layer the instance is on or the name of
            the layer.
            If set to None the whole map will be searched.

            map_or_identifier: The map of the layer or the name of the map.
            Ignored if layer is an layer instance.

        Returns:

            The first instance with the given name on the given layer.

        Raises:

            ValueError if there was no map with that identifier.
        """
        if layer_or_identifier is None:
            layers = self.get_layers(map_or_identifier)
            for layer in layers:
                instance = self.get_instance(identifier, layer)
                if instance is not None:
                    return instance
            return None
        else:
            if not isinstance(layer_or_identifier, fife.Layer):
                layer_or_identifier = self.get_layer(map_or_identifier,
                                                     layer_or_identifier)
            return layer_or_identifier.getInstance(identifier)

    def get_instances_of_layer(self, layer_or_layer_data,
                               instance_identifier=None):
        """Returns a list of the instances of a layer

        Args:

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.

            instance_identifier: If set only return instances with the given
            identifier.

        Raises:

            ValueError if there was no map with that identifier.
        """
        if not isinstance(layer_or_layer_data, fife.Layer):
            layer_or_layer_data = self.get_layer(layer_or_layer_data[1],
                                                 layer_or_layer_data[0])
        if instance_identifier is None:
            return layer_or_layer_data.getInstances()
        else:
            return layer_or_layer_data.getInstances(instance_identifier)

    def get_instances_at(self, coords, layer_or_layer_data=None,
                         use_exact_coordinates=False):
        """Get all instances at the given coords

        Args:

            coords: Either a 3-value tuple, fife.(Exact)ModelCoordinates
            instance or a fife.Location instance.

            layer_or_layer_data: The layer or a tuple with 2 items: The name
            of the layer and the map of the layer as a string or an map
            instance.
            Ignored if coords is a fife.Location instance

            use_exact_coordinates: if True, comparison is done using exact
            coordinates. if not, cell coordinates are used.

        Raises:

            ValueError if there was no map with that identifier.
        """
        try:
            iter(coords)
            coords = fife.ExactModelCoordinate(*coords)
        except TypeError:
            pass
        layer = None
        if not isinstance(coords, fife.Location):
            layer = layer_or_layer_data
            if not isinstance(layer_or_layer_data, fife.Layer):
                layer = self.get_layer(layer_or_layer_data[1],
                                       layer_or_layer_data[0])
            tmp_coords = coords
            coords = fife.Location(layer)
            coords.setExactLayerCoordinates(tmp_coords)
        else:
            layer = coords.getLayer()
        return layer.getInstancesAt(coords)

    def get_instances_of_map(self, map_or_identifier):
        """Returns a list of the instances of a map

        Args:


            map_or_identifier: The map of the layer or the name of the map.
            Ignored if layer is an layer instance.

        Raises:

            ValueError if there was no map with that identifier.
        """
        layers = self.get_layers(map_or_identifier)
        instances = []
        for layer in layers:
            instances.append(self.get_instances_of_layer(layer))
        return instances

    def increase_refcount(self, filename, map_name=None):
        """Increase reference count for a file on a map

        Args:

            filename: The filename the reference counter is for

            Map: The map the reference counter is for
        """
        if map_name not in self.__import_ref_count:
            self.__import_ref_count[map_name] = {}
        ref_count = self.__import_ref_count[map_name]
        if filename in ref_count:
            ref_count[filename] += 1
        else:
            ref_count[filename] = 1

    def decrease_refcount(self, filename, map_name):
        """Decrease reference count for a file on a map

        Args:

            filename: The filename the reference counter is for

            Map: The map the reference counter is for
        """
        if map_name not in self.__import_ref_count:
            return
        ref_count = self.__import_ref_count[map_name]
        if filename in ref_count:
            ref_count[filename] -= 1
            if ref_count[filename] <= 0:
                del ref_count[filename]

    def get_import_list(self, map_name):
        """Returns the import files of the given map

        Args:

            map_name: The name of the map to the the imports for
        """
        if map_name in self.__import_ref_count:
            return iter(self.__import_ref_count[map_name].keys())
        else:
            return []

    def undo(self):
        """Undoes the last done action"""
        self.undo_manager.undo_action()

    def redo(self):
        """Redoes the last undone action"""
        self.undo_manager.redo_action()
