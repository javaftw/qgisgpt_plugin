
import os
import json
from PyQt5.QtCore import QTimer, QEvent, Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer
from qgis.utils import iface

class Utils():

    def __init__(self):
        super().__init__() 

    def create_project_snapshot(self):
        """Creates a JSON snapshot of the current QGIS project state, 
        only if the project is dirty (has unsaved changes)."""
        project = QgsProject.instance()

        # Check if the project is dirty (has unsaved changes)
        if not project.isDirty():
            # Return an empty JSON object if the project is not dirty
            return json.dumps({})

        snapshot = {
            "file_name": project.fileName(),
            "title": project.title(),
            "project_crs": project.crs().authid(),
            "layers": []
        }

        # Get the layer tree root to access visibility information
        layer_tree_root = iface.layerTreeCanvasBridge().rootGroup()

        for layer in project.mapLayers().values():
            layer_tree_layer = layer_tree_root.findLayer(layer.id())
            layer_is_visible = layer_tree_layer.isVisible() if layer_tree_layer else False

            layer_info = {
                "name": layer.name(),
                "type": "Vector" if isinstance(layer, QgsVectorLayer) else "Raster",
                "crs": layer.crs().authid(),
                "visible": layer_is_visible,
                "feature_count": layer.featureCount() if isinstance(layer, QgsVectorLayer) else None,
                "attributes": [field.name() for field in layer.fields()] if isinstance(layer, QgsVectorLayer) else None
            }
            snapshot["layers"].append(layer_info)

        return json.dumps(snapshot, indent=2)
    
    def get_layer_names_for_combobox(self):
        """Returns a list of layer names in the current QGIS project for populating a QComboBox."""
        project = QgsProject.instance()
        layer_names = [layer.name() for layer in project.mapLayers().values()]
        return layer_names