# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Attribute
                                 A QGIS plugin
 attribute
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-12
        git sha              : $Format:%H$
        copyright            : (C) 2024 by ksc
        email                : ---
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject
from qgis.core import QgsLayerTreeLayer, QgsMapLayerType   
from qgis.core import QgsExpression, QgsFeatureRequest,QgsFeatureIterator


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Attribute_dialog import AttributeDialog
import os.path


class Attribute:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Attribute_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Attributefinder')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Attribute', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Attribute/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'AttributeFinder'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Attributefinder'),
                action)
            self.iface.removeToolBarIcon(action)


    def check_lineedit_text(self):
    # Get the text from the QLineEdit
        lineedit_text = self.dlg.lineEdit.text()

    # Get the selected values from the ComboBoxes
        selected_value1 = self.dlg.comboBox.currentText()
        selected_value2 = self.dlg.comboBox2.currentText()

    # Get the layer based on the attribute values for the first GeoPackage
        layer1 = self.get_layer_by_attribute_values("市町村名", selected_value1, "大字名", selected_value2, "字界(玉名市).gpkg")

    # Get the layer based on the attribute values for the second GeoPackage
        layer2 = self.get_layer_by_attribute_values("市町村名", selected_value1, "大字名", selected_value2, "地籍(玉名市).gpkg")

    # Check if either layer has the specified column
        column_to_check = "地番"  # Replace with the actual column name

        if not lineedit_text:
        # Zoom based on dropdown values when the line edit is empty
            if layer1:
                self.zoom_to_features(layer1, "市町村名", selected_value1, "大字名", selected_value2)
            elif layer2:
                self.zoom_to_features(layer2, "市町村名", selected_value1, "大字名", selected_value2)
        else:
        # Check line edit box data with the specified column in the attribute table
            if layer1 and column_to_check in layer1.fields().names():
                self.check_and_zoom(layer1, column_to_check, lineedit_text, "市町村名", selected_value1, "大字名", selected_value2)
            elif layer2 and column_to_check in layer2.fields().names():
                self.check_and_zoom(layer2, column_to_check, lineedit_text, "市町村名", selected_value1, "大字名", selected_value2)
            else:
                self.show_message("Column {} does not exist in the attribute tables of both GeoPackages.".format(column_to_check))


    def check_and_zoom(self, layer, column_to_check, lineedit_text, *args):
        # Check line edit box data with the specified column in the attribute table
        if self.check_lineedit_data(layer, column_to_check, lineedit_text):
            # Zoom based on line edit box data and both dropdown values
            self.zoom_to_features(layer, column_to_check, lineedit_text, *args)
        else:
            # Handle the case where the line edit box data does not match the specified column
            self.show_message("Line edit box data does not match the specified column.")        

    def show_message(self, message):
        # Display a message using QMessageBox
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def check_lineedit_data(self, layer, column_to_check, lineedit_text):
        # Check if line edit box data matches a certain column in the attribute table
        if column_to_check in layer.fields().names():
            expr = QgsExpression("{} = '{}'".format(column_to_check, lineedit_text))
            request = QgsFeatureRequest(expr)
            features = layer.getFeatures(request)
            return any(features)
        else:
            self.show_message("Column {} does not exist in the layer's attribute table.".format(column_to_check))
            return False

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start == False
            self.dlg = AttributeDialog()

        # To zoom to the selected position click search
        self.dlg.pushButton.clicked.connect(self.check_lineedit_text)
        
        # Get the root of the layer tree
        root = QgsProject.instance().layerTreeRoot()

        # Get a list of all layers in the project
        layers = root.children()

        # Clear the existing items in the ComboBoxes
        self.dlg.comboBox.clear()
        self.dlg.comboBox2.clear()

        # Column names
        column_name1 = '市町村名'
        column_name2 = '大字名'

        # Populate the ComboBoxes with data from the specified columns
        for layer_tree_layer in layers:
            if isinstance(layer_tree_layer, QgsLayerTreeLayer):
                layer = layer_tree_layer.layer()

                # Ensure that the layer is a vector layer
                if layer and layer.type() == QgsMapLayerType.VectorLayer:
                    # Access attribute data from the specified columns
                    unique_values1 = set(feature[column_name1] for feature in layer.getFeatures())
                    unique_values2 = set(feature[column_name2] for feature in layer.getFeatures())

                    # Add the unique values to the ComboBoxes
                    self.dlg.comboBox.addItems(sorted(unique_values1))  # Sorting for better readability
                    self.dlg.comboBox2.addItems(sorted(unique_values2))  # Sorting for better readability

        # Show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def zoom_to_location(self):
        lineedit_text = self.dlg.lineEdit.text()
        selected_value1 = self.dlg.comboBox.currentText()
        selected_value2 = self.dlg.comboBox2.currentText()

        layer = self.get_layer_by_attribute_values("市町村名", selected_value1, "大字名", selected_value2)

        if layer:
            self.check_lineedit_text(layer, lineedit_text, selected_value1, selected_value2)

    # Get the layers
    def get_layer_by_attribute_values(self, column_name1, value1, column_name2, value2, gpkg_filename):
        root = QgsProject.instance().layerTreeRoot()

        for layer_tree in root.children():
            if isinstance(layer_tree, QgsLayerTreeLayer):
                layer = layer_tree.layer()

                if layer:
                    if layer.dataProvider().dataSourceUri().find(gpkg_filename) != -1:
                        expr = QgsExpression("{} = '{}' AND {} = '{}'".format(column_name1, value1, column_name2, value2))
                        request = QgsFeatureRequest(expr)
                        features = layer.getFeatures(request)

                        if features:
                            return layer

        return None

    # Zoom to the selected layer
    def zoom_to_features(self, layer, *args):
        # Zoom to the features with the selected attribute values
        expr = QgsExpression(" AND ".join("{} = '{}'".format(column, value) for column, value in zip(args[::2], args[1::2])))
        request = QgsFeatureRequest(expr)
        features = layer.getFeatures(request)
        for feature in features:
            bbox = feature.geometry().boundingBox()
            self.iface.mapCanvas().setExtent(bbox)
            self.iface.mapCanvas().refresh()
            break