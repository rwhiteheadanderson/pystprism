# -*- coding: utf-8 -*-

import arcpy
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pystprism
from pystprism import prisms
from pystprism import surface
from pystprism import utils
arcpy.env.overwriteOutput = True


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PySTPrisms"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [
            GenerateSTP, GeneratePSTP, CalculateProbabilitySurface,
            SaveTrajectory
        ]


class GenerateSTP(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate Voxel Space-Time Prism"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Input Point Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = arcpy.Parameter(displayName="Timestamp Field",
                                 name="timestamp_field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.parameterDependencies = [param0.name]

        param2 = arcpy.Parameter(
            displayName="Prism Disk Temporal Interval (Seconds)",
            name="disk_interval",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Prism Disk Cell Size (Map Units)",
            name="cell_size",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(displayName="Velocity Multiplier",
                                 name="velocity_multiplier",
                                 datatype="GPDouble",
                                 parameterType="Required",
                                 direction="Input")
        param4.value = 1.5

        param5 = arcpy.Parameter(displayName="Expand Edges Factor",
                                 name="expand_edges_factor",
                                 datatype="GPDouble",
                                 parameterType="Required",
                                 direction="Input")
        param5.value = 1.0

        param6 = arcpy.Parameter(displayName="Output Folder for Prism FGDB",
                                 name="output_workspace",
                                 datatype="DEFolder",
                                 parameterType="Required",
                                 direction="Input")

        params = [param0, param1, param2, param3, param4, param5, param6]

        return params

    def isLicensed(self):
        """Allow the tool to execute, only if the ArcGIS 3D Analyst extension 
        is available."""
        try:
            if arcpy.CheckExtension("Spatial") != "Available":
                raise Exception
        except Exception:
            return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.CreateFileGDB_management(
            parameters[6].value,
            "{0}.gdb".format(parameters[0].value.name + "_STP"))
        arcpy.env.workspace = str(
            parameters[6].value) + os.sep + "{0}.gdb".format(
                parameters[0].value.name + "_STP")
        ppa_rasters = prisms.voxel_potential_path_area(
            parameters[0].value, parameters[1].valueAsText,
            parameters[2].value, parameters[3].value,
            float(parameters[4].value), float(parameters[5].value))
        for output in ppa_rasters:
            output[0].save(parameters[0].value.name + "_" +
                           output[1].strftime('%Y_%m_%d_%H_%M_%S'))
        return


class GeneratePSTP(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate Probabilistic Voxel Space-Time Prism"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Input Point Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = arcpy.Parameter(displayName="Timestamp Field",
                                 name="timestamp_field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.parameterDependencies = [param0.name]

        param2 = arcpy.Parameter(
            displayName="Prism Disk Temporal Interval (Seconds)",
            name="disk_interval",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Prism Disk Cell Size (Map Units)",
            name="cell_size",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(displayName="Velocity Multiplier",
                                 name="velocity_multiplier",
                                 datatype="GPDouble",
                                 parameterType="Required",
                                 direction="Input")
        param4.value = 1.5

        param5 = arcpy.Parameter(displayName="Expand Edges Factor",
                                 name="expand_edges_factor",
                                 datatype="GPDouble",
                                 parameterType="Required",
                                 direction="Input")
        param5.value = 1.0

        param6 = arcpy.Parameter(displayName="Output Folder for Prism FGDB",
                                 name="output_workspace",
                                 datatype="DEFolder",
                                 parameterType="Required",
                                 direction="Input")

        params = [param0, param1, param2, param3, param4, param5, param6]

        return params

    def isLicensed(self):
        """Allow the tool to execute, only if the ArcGIS 3D Analyst extension 
        is available."""
        try:
            if arcpy.CheckExtension("Spatial") != "Available":
                raise Exception
        except Exception:
            return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.CreateFileGDB_management(
            parameters[6].value,
            "{0}.gdb".format(parameters[0].value.name + "_PSTP"))
        arcpy.env.workspace = str(
            parameters[6].value) + os.sep + "{0}.gdb".format(
                parameters[0].value.name + "_PSTP")
        pstp_rasters = prisms.probabilistic_space_time_prism(
            parameters[0].value, parameters[1].valueAsText,
            parameters[2].value, parameters[3].value, parameters[4].value,
            parameters[5].value)
        for output in pstp_rasters:
            output[0].save(parameters[0].value.name + "_" +
                           output[1].strftime('%Y_%m_%d_%H_%M_%S'))
        return


class CalculateProbabilitySurface(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Probability Surface"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(displayName="Input Prism Disk Rasters",
                                 name="in_rasters",
                                 datatype="GPRasterLayer",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)

        param1 = arcpy.Parameter(displayName="Output Geodatabase",
                                 name="out_workspace",
                                 datatype="DEWorkspace",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.list = ["Local Database"]

        param2 = arcpy.Parameter(
            displayName="Output Probability Surface Raster",
            name="out_raster",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Allow the tool to execute, only if the ArcGIS 3D Analyst extension 
        is available."""
        try:
            if arcpy.CheckExtension("Spatial") != "Available":
                raise Exception
        except Exception:
            return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        raster_paths = [item.replace("'", "") for item in parameters[0].valueAsText.split(';')]
        input_rasters = [surface.path_to_raster(item) for item in raster_paths]
        comp_surface = surface.comprehensive_probability_surface(input_rasters)
        comp_surface.save(parameters[1].valueAsText + os.sep +
                          parameters[2].valueAsText)
        return


class SaveTrajectory(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Save Pre-Processed Trajectory"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(displayName="Input Point Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = arcpy.Parameter(displayName="Timestamp Field",
                                 name="timestamp_field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.parameterDependencies = [param0.name]

        param2 = arcpy.Parameter(displayName="Output Geodatabase",
                                 name="out_workspace",
                                 datatype="DEWorkspace",
                                 parameterType="Required",
                                 direction="Input")
        param2.filter.list = ["Local Database"]
        param2.value = arcpy.env.workspace

        param3 = arcpy.Parameter(
            displayName="Output Preprocessed Point Featureclass Name",
            name="out_features",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        traj = utils.Trajectory(parameters[0].valueAsText,
                                parameters[1].valueAsText)
        traj.export_trajectory(parameters[2].valueAsText,
                               parameters[3].valueAsText)
        return
