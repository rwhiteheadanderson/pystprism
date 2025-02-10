import arcpy


class Trajectory(object):
    """Represents the trajectory of a moving object as a series of timestamped
    point locations. Trajectories serve as the input for space-time prism
    generating functions. Essentially, a Trajectory is just an ordered set of
    dictionaries - each dictionary represents one fix (space-time anchor) in 
    the input trajectory. The Trajectory class currently only supports 
    point geodatabase feature classes as input. These inputs are expected 
    to carry a field reflecting timestamp informtation for each available 
    point location. The timestamp field must be Date type. Inputs are assumed 
    to subscribe to a projected coordinate system. All distances are recorded 
    in the map units of this projected coordinate system. Instantiating a 
    Trajectory object calculates and stores all of the time-delta and velocity 
    values as necessary for space-time prism calculation. All timings are recorded 
    in seconds.
    """

    def __init__(self, in_features, timestamp_field):
        """
        Args:
            in_features: A reference to the source feature class used to
                instantiate the trajectory.
            timestamp_field: A reference to the field reflecting timestamp
                values for input fixes in the trajectory.
        """
        self.in_features = in_features
        self.timestamp_field_name = timestamp_field
        self.extent = arcpy.Describe(in_features).extent
        self.oid_field_name = arcpy.Describe(in_features).OIDFieldName
        self.spatial_reference = arcpy.Describe(in_features).spatialReference
        self.fixes = []
        with arcpy.da.SearchCursor(
            in_features, ["OID@", "SHAPE@", timestamp_field]
        ) as cursor:
            for row in cursor:
                self.fixes.append(
                    {"OID": row[0], "geometry": row[1], "timestamp": row[2]}
                )
        self.fixes.sort(key=lambda x: x["timestamp"])
        for feature in self.fixes:
            if self.fixes.index(feature) == len(self.fixes) - 1:
                # this is the last fix in the trajectory, indexing starts at 0
                feature["distance"] = 0
                feature["elapsed_time"] = 0
                feature["velocity"] = 0
            else:
                """Suppose we have two sequential fixes, A and B... All of the
                information calculated here is associated with A. The last fix
                in the trajectory will have 0's for all these calculations...
                """
                # distance is the distance from A to B in map units
                feature["distance"] = feature["geometry"].distanceTo(
                    self.fixes[self.fixes.index(feature) + 1]["geometry"]
                )
                # elapsed_time is the seconds elapsed between A to B
                feature["elapsed_time"] = (
                    self.fixes[self.fixes.index(feature) + 1]["timestamp"]
                    - feature["timestamp"]
                ).total_seconds()
                # velocity is the distance/time of travel from A to B
                feature["velocity"] = feature["distance"] / feature["elapsed_time"]
        self.duration = (
            self.fixes[-1]["timestamp"] - self.fixes[0]["timestamp"]
        ).total_seconds()
        self.count = len(self.fixes)
        self.minimum_disk_interval = min(
            fix["elapsed_time"] for fix in self.fixes if fix["elapsed_time"] != 0
        )
        return

    def export_trajectory(self, output_workspace, output_name):
        "Exports the trajectory as a geodatabase point feature class"
        arcpy.CreateFeatureclass_management(
            output_workspace,
            output_name,
            geometry_type="POINT",
            spatial_reference=self.spatial_reference,
        )
        arcpy.AddField_management(output_workspace + "\\" + output_name, "id", "LONG")
        arcpy.AddField_management(
            output_workspace + "\\" + output_name, "timestamp", "DATE"
        )
        for item in ["distance", "elapsed_time", "velocity"]:
            arcpy.AddField_management(
                output_workspace + "\\" + output_name, item, "DOUBLE"
            )
        with arcpy.da.InsertCursor(
            output_workspace + "\\" + output_name,
            ["id", "SHAPE@", "timestamp", "distance", "elapsed_time", "velocity"],
        ) as cursor:
            for item in self.fixes:
                row = [
                    item["OID"],
                    item["geometry"],
                    item["timestamp"],
                    item["distance"],
                    item["elapsed_time"],
                    item["velocity"],
                ]
                cursor.insertRow(row)
        return


def main():
    return


if __name__ == "__main__":
    main()
