# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoggerFileReader
                                 A QGIS plugin
 Mobikids data logger file reader
                             -------------------
        begin                : 2015-09-07
        copyright            : (C) 2015 by Alkante
        email                : o.bedel@alkante.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LoggerFileReader class from file LoggerFileReader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .loggerFile_reader import LoggerFileReader
    return LoggerFileReader(iface)
