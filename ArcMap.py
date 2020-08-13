import arcpy
import os
from datetime import datetime
import pandas as pd

# address(1) or latlon(0)
is_address_method = arcpy.GetParameter(0)
# specify the input file
input_sheet = arcpy.GetParameterAsText(1)

CityName = arcpy.GetParameterAsText(2)
StateName = arcpy.GetParameterAsText(3)

input_x_coord = arcpy.GetParameterAsText(4)
input_y_coord = arcpy.GetParameterAsText(5)

spRef = arcpy.GetParameter(6)

divider = arcpy.GetParameter(7)

num_fields = 0
num_added_fields = 0

my_sheet_name = ""

if ".csv" in input_sheet:
    without_sheet = input_sheet
    arcpy.AddMessage(without_sheet)
    df = pd.read_csv(without_sheet, error_bad_lines=False)  # Read csv file as a DataFrame

elif ".xlsx" in input_sheet:  # it's an xls file, therefore need to parse out the sheet name from ArcMap input
    without_sheet = os.path.normpath(input_sheet).rsplit("\\", 1)[0]
    my_sheet_name = os.path.normpath(input_sheet).rsplit("\\", 1)[1][:-1]
    df = pd.read_excel(without_sheet, sheetname=my_sheet_name)  # Read Excel file as a DataFrame

else:  # it's an xls file, therefore need to parse out the sheet name from ArcMap input
    without_sheet = os.path.normpath(input_sheet).rsplit("\\", 1)[0]
    my_sheet_name = os.path.normpath(input_sheet).rsplit("\\", 1)[1][1:-2]
    df = pd.read_excel(without_sheet, sheetname=my_sheet_name)  # Read Excel file as a DataFrame

num_fields = len(df.columns)
input_file = os.path.normpath(os.path.basename(without_sheet))

# # Find the columns where each value is null
# empty_cols = [col for col in df.columns if df[col].isnull().all()]
# # Drop these columns from the dataframe
# df.drop(empty_cols, axis=1, inplace=True)
#
# # drop empty columns, more part of data cleaning
# df.dropna(how='all', inplace=True)
#
# df.reset_index(drop=True)

# if 'Unnamed: 1' in df.columns:
#     df.rename(columns=df.iloc[0], inplace=True)
#     df.drop(0, inplace=True)
#     df.reset_index(drop=True)

# add "FIPS" to the list of fields, as this is what the final column should be after the process
original_columns = list(df.columns)
original_columns.append("FIPS")

arcpy.env.workspace = "D:/ArcGIS/Default.gdb"
# output_directory = "D:/ArcGIS"
output_directory = os.path.dirname(input_sheet)
arcpy.env.overwriteOutput = True

# name of the table to copy inputs into
input_table = "address"
# name of the layer that will be joined with the Census boundary data.
# In case of Address method, this will be the Geocoding_Result
# In case of LatLon method, this will XY event layer (result of importing XY data)
to_join = "to_join"


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


arcpy.AddMessage("Starting importing sheet to gdb %s" % get_current_time())
if ".csv" in input_sheet:
    arcpy.CopyRows_management(without_sheet, input_table)
    # arcpy.TableToTable_conversion(without_sheet, arcpy.env.workspace, input_table)
else:
    arcpy.ExcelToTable_conversion(without_sheet, input_table, my_sheet_name)

arcpy.AddMessage("Finished import to gdb.")

del df

field_names = [f.name for f in arcpy.ListFields(input_table)]
arcpy.AddMessage(field_names)

fields_to_delete = ["Join_Count", "TARGET_FID"]

if is_address_method:
    # set city field if doesn't exist
    if len(arcpy.ListFields(input_table, "City")) > 0:
        arcpy.AddMessage("City field exists")
    else:
        arcpy.AddMessage("City field doesn't exist, adding City field...")
        arcpy.AddField_management(input_table, "City", "TEXT")
        expression = '"' + CityName + '"'
        arcpy.CalculateField_management(input_table, "City", expression, "VB")
        num_added_fields += 1

    # set state field if doesn't exist
    if len(arcpy.ListFields(input_table, "State")) > 0:
        arcpy.AddMessage("State field exists")
    else:
        arcpy.AddMessage("State field doesn't exist, adding State field...")
        arcpy.AddField_management(input_table, "State", "TEXT")
        expression = '"' + StateName + '"'
        arcpy.CalculateField_management(input_table, "State", expression, "VB")
        num_added_fields += 1

    # remove the processed address from the list of original columns
    try:
        original_columns.remove("myaddress")
    except ValueError:
        arcpy.AddError("{0} has no 'myaddress' column".format(without_sheet))

    address_locator = "D:/ArcGIS/streetmap_na/data/Street_Addresses_US"
    address_fields = "Street myaddress;City City;State State;ZIP <None>"
    # address_fields = "'Single Line Input' Location"

    arcpy.AddMessage("Starting geocoding at %s" % get_current_time())
    arcpy.GeocodeAddresses_geocoding(input_table, address_locator, address_fields, to_join)
    arcpy.AddMessage("Geocoding finished.")


# XY coords case: first designate the database, a name for the layer of XY events, and the name of columns with XY data
# Then, add new fields that will be deleted later in case we need to do something funny like divide by 1000 or something
# Calculate the values of this new field, which in many cases I guess will just be the same as the original XY columns
# Finally, create the XY layer using our "custom" XY fields
else:
    original_x_coord_name = input_x_coord.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")
    original_y_coord_name = input_y_coord.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")

    added_x_coord_name = "my_x"
    added_y_coord_name = "my_y"

    arcpy.AddMessage("Starting adding my XY fields at %s" % get_current_time())

    arcpy.AddField_management(input_table, added_x_coord_name, "FLOAT")
    arcpy.AddField_management(input_table, added_y_coord_name, "FLOAT")

    expression_x = "validateCoord(!" + original_x_coord_name + "!)"
    expression_y = "validateCoord(!" + original_y_coord_name + "!)"
    code_block = """
def validateCoord(input):
    try:
        number = float(input)
        if number != 0 and number != -1:
          return number""" + "/" + str(divider) + """
        else:
          return None
    except:
        return None"""

    arcpy.CalculateField_management(input_table, added_x_coord_name, expression_x, "PYTHON", code_block)
    arcpy.CalculateField_management(input_table, added_y_coord_name, expression_y, "PYTHON", code_block)

    arcpy.MakeXYEventLayer_management(input_table, added_x_coord_name, added_y_coord_name, to_join, spRef)

    # also need to delete added coordinate fields
    fields_to_delete.extend([added_x_coord_name, added_y_coord_name])

# add Census Boundaries as layer
joining_layer = "D:/ArcGIS/Boundaries/USA Census Tract Boundaries.lyr"
arcpy.MakeFeatureLayer_management(in_features=joining_layer, out_layer="Census_Boundaries")
arcpy.AddMessage("Added census tract boundaries layer.")

# join the address/latlon location data with Census Boundaries layer which will attach FIPS info to each point
arcpy.AddMessage("Starting spatial join at %s" % get_current_time())
arcpy.SpatialJoin_analysis(target_features=to_join, join_features="Census_Boundaries",
                           out_feature_class="joined", match_option="CLOSEST")
arcpy.AddMessage("Spatial join finished.")

field_names = [f.name for f in arcpy.ListFields("joined")]

arcpy.AddMessage(field_names)

arcpy.DeleteField_management("joined", fields_to_delete)

if my_sheet_name:
    final_file_name = input_file[:input_file.rfind('.')] + " (" + my_sheet_name + ")"
else:
    final_file_name = input_file[:input_file.rfind('.')]

output_file_name = output_directory + "/%s_geo_MT.csv" % final_file_name
arcpy.AddMessage("Starting table to csv conversion at %s" % get_current_time())
arcpy.TableToTable_conversion("joined", output_directory, "%s_geo_MT.csv" % final_file_name)
arcpy.AddMessage("csv output to %s at %s" % (output_file_name, get_current_time()))

# rewrite the column header to match originals in case replaced whitespace with "_" or something
df = pd.read_csv(output_file_name)  # Read Excel file as a DataFrame

# sometimes ArcMap makes extra fields that look like fieldname+"_X" or "_Y", so we have to throw those away as well
current_columns = list(df.columns)
for field in current_columns:
    if field + "_X" in current_columns:
        to_drop = [field + "_X", field + "_Y"]
        arcpy.AddMessage("Dropping " + ' '.join(to_drop))
        df.drop(to_drop, axis=1, inplace=True)


# delete all new columns created in the XY coordinate process
if not is_address_method:
    # drop the first column, which holds the "OBJECTID", an artefact of exporting an ArcMap table
    df.drop(df.columns[0], axis=1, inplace=True)

    if len(list(df.columns)) != len(original_columns):
        original_columns.insert(len(original_columns) - 1, "newcol")
    arcpy.AddMessage(list(df.columns))
    arcpy.AddMessage(original_columns)
    df.columns = original_columns

    if "newcol" in df.columns:
        arcpy.AddMessage("dropping newcol")
        df.drop(["newcol"], axis=1, inplace=True)

else:
    # after_columns = 37
    #
    # for field in current_columns:
    #     if field + "_X" in current_columns:
    #         to_drop = [field + "_X", field + "_Y"]
    #         arcpy.AddMessage("Dropping " + ' '.join(to_drop))
    #         df.drop(to_drop, axis=1, inplace=True)
    #         after_columns -= 1
    #
    # columns_to_drop = list(range(0, after_columns))
    # # columns_to_drop.extend(range(after_columns + num_fields - 1, after_columns + num_fields + num_added_fields))
    # # arcpy.AddMessage(columns_to_drop)
    # # arcpy.AddMessage(df.columns[columns_to_drop])
    # df.drop(df.columns[columns_to_drop], axis=1, inplace=True)
    # # df.drop(['City', 'State', 'City_1', 'State_1'], axis=1, inplace=True)
    # final_col = df.columns.get_loc("myaddress")
    # df.drop(df.columns[[final_col, final_col+1, final_col+2, final_col+3]], axis=1, inplace=True)

    last_extra_col = df.columns.get_loc("ARC_ZIP")
    df.drop(df.columns[list(range(0, last_extra_col+1))], axis=1, inplace=True)
    first_column = df.columns.get_loc("myaddress")
    df.drop(df.columns[list(range(first_column, len(df.columns)-1))], axis=1, inplace=True)

    arcpy.AddMessage(list(df.columns))
    arcpy.AddMessage(original_columns)

    # after adjusting the columns, we copy the column names over from the original sheet because ArcMap messes the
    # original names up
    df.columns = original_columns

# Write DateFrame back as final csv file
df.to_csv(output_file_name, index=False)
