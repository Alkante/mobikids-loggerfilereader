# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoggerFileReader
                                 A QGIS plugin
 Mobikids data logger file reader
                              -------------------
        begin                : 2015-09-07
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Alkante
        email                : o.bedel@alkante.com
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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .loggerFile_reader_dialog import LoggerFileReaderDialog
import os.path
from .dataFileParser import *

class LoggerFileReader:
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
            'LoggerFileReader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LoggerFileReaderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Mobikids Logger File Reader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LoggerFileReader')
        self.toolbar.setObjectName(u'LoggerFileReader')

        # ui actions
        self.dlg.outDataPathButton.clicked.connect(self.outPath)
        self.dlg.inDataPathButton.clicked.connect(self.inDataFile)


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
        return QCoreApplication.translate('LoggerFileReader', message)


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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LoggerFileReader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mobikids file reader'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Mobikids Logger File Reader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            dataFilename = self.dlg.inDataFilePath.text()
            basename = QFileInfo(dataFilename).baseName()
            outDir = self.dlg.outDataPath.text()
            prefix = outDir + '/'+ basename
            # récupération des paramètres d'extraction
            e_magneto = self.dlg.cbx_magneto.checkState()==Qt.Checked
            e_accelero = self.dlg.cbx_accelero.checkState()==Qt.Checked
            e_battery = self.dlg.cbx_battery.checkState()==Qt.Checked
            e_gps_csv = self.dlg.cbx_gps_csv.checkState()==Qt.Checked
            e_gps_kml = self.dlg.cbx_gps_kml.checkState()==Qt.Checked
            e_gps_shp = self.dlg.cbx_gps_shp.checkState()==Qt.Checked
            # gps_csv file is required by shp and kml
            e_gps_csv = e_gps_csv or e_gps_kml or e_gps_shp
            
            params = [e_accelero, e_magneto, e_battery, e_gps_csv];

            dataFileParser = DataFileParser(None,params,'QGIS',1, self.dlg.progressBar)
            dataFileParser.convertFile(dataFilename, prefix)
            if e_gps_csv:
                gpsFileName = prefix + '_gps.csv'
                self.loadToCanvas(gpsFileName, basename, outDir)
            if e_gps_csv and (e_gps_kml or e_gps_shp):
                self.convertToShpKml(basename, outDir, e_gps_shp, e_gps_kml)
            QMessageBox.information(self.dlg, u'Mobikids Logger File Reader', u'Fichier traité')

            pass


    def outPath(self): # by Carson Farmer 2008
      # display file dialog for output shapefile
      self.dlg.outDataPath.clear()
      fileDialog = QFileDialog()
      fileDialog.setConfirmOverwrite(False)
      outName = fileDialog.getExistingDirectory(self.dlg, "Output Directory",".")
      outPath = QFileInfo(outName).absoluteFilePath()
      if outName:
        self.dlg.outDataPath.clear()
        self.dlg.outDataPath.insert(outPath)

    def inDataFile(self): # by Carson Farmer 2008
        # display file dialog for output shapefile
        self.dlg.inDataFilePath.clear()
        fileDialog = QFileDialog()
        fileDialog.setConfirmOverwrite(False)
        outName = fileDialog.getOpenFileName(self.dlg, "Input data file",".", "Mobikids DataLogger File (*.dat)")
        outPath = QFileInfo(outName).absoluteFilePath()
        if outName:
            self.dlg.inDataFilePath.clear()
            self.dlg.inDataFilePath.insert(outPath)

    def loadToCanvas(self, gpsCsvFileName, layerName, outPath):
        uri = "file:///%s?delimiter=%s&crs=epsg:4326&xField=%s&yField=%s" % (gpsCsvFileName,";", "lon", "lat")
        self.vlayer = self.iface.addVectorLayer(uri, layerName, "delimitedtext")

    def convertToShpKml(self, layerName, outPath, e_shp=True, e_kml=True):
        if e_shp:
            outFilename = (outPath+'/'+layerName+'.shp').encode('utf-8')
            error = QgsVectorFileWriter.writeAsVectorFormat(self.vlayer, outFilename, "utf-8", None, "ESRI Shapefile")
        if e_kml:
            outFilename = (outPath+'/'+layerName+'.kml').encode('utf-8')
            error = QgsVectorFileWriter.writeAsVectorFormat(self.vlayer, outFilename, "utf-8", None, "KML")
