import arcpy
import os

class ToolValidator(object):
    """Class for validating a tool's parameter values and controlling
    the behavior of the tool's dialog."""

    def __init__(self):
        """Setup arcpy and the list of tool parameters."""
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        # default divider value is 1
        self.params[7].value = 1

        prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], "Coordinate Systems/Geographic Coordinate Systems/North America/WGS 1984.prj")
        spatialRef = arcpy.SpatialReference(prjFile)
        self.params[6].value = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"
        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        # address method
        if self.params[0].value:
            self.params[2].enabled = 1
            self.params[3].enabled = 1

            self.params[4].enabled = 0
            self.params[5].enabled = 0
            self.params[6].enabled = 0
            self.params[7].enabled = 0

        # latlon method
        else:
            self.params[2].enabled = 0
            self.params[3].enabled = 0

            self.params[4].enabled = 1
            self.params[5].enabled = 1
            self.params[6].enabled = 1
            self.params[7].enabled = 1

            # list of fields from your input table
            if self.params[1].altered:
                field_list = [str(val) for val in
                              sorted(set(row.name for row in arcpy.ListFields(self.params[1].value)))]
                self.params[4].filter.list = field_list
                self.params[5].filter.list = field_list
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
