import arcpy
from arcpy.sa import *
import datetime
import os
import numpy as np
from .utils import Trajectory


def voxel_potential_path_area(in_features, timestamp_field, disk_interval,
                              cell_size, velocity_multiplier,
                              expand_edges_factor):
    '''Generates the classical voxel space-time prism from in_trajectory. This
    prism result is returned as an ordered list of arcpy raster objects. Each
    raster represents one space time disk. All timings are recorded in seconds.
    This function does not account for stationary activity time, and assumes
    the object was in-motion from departure to arrival. This function requires
    a spatial analyst license.
    '''
    # First, prepare a Trajectory object from the input dataset
    in_trajectory = Trajectory(in_features, timestamp_field)
    # Ensure the user's disk interval is smaller than the minimum time elapsed
    if disk_interval > in_trajectory.minimum_disk_interval:
        raise ValueError(
            'Disk interval %f > shortest interval in trajectory of %f' %
            (disk_interval, in_trajectory.minimum_disk_interval))
    # Prepare the analysis extent to cover more area using the expand_edges_factor
    arcpy.env.extent = arcpy.Extent(
        (in_trajectory.extent.XMin -
         (in_trajectory.extent.width * expand_edges_factor)),
        (in_trajectory.extent.YMin -
         (in_trajectory.extent.height * expand_edges_factor)),
        (in_trajectory.extent.XMax +
         (in_trajectory.extent.width * expand_edges_factor)),
        (in_trajectory.extent.YMax +
         (in_trajectory.extent.height * expand_edges_factor)))
    ppa_rasters = []
    for fix in in_trajectory.fixes:
        if in_trajectory.fixes.index(fix) != \
                    in_trajectory.fixes.index(in_trajectory.fixes[-1]):
            # if not the last fix in the trajectory, then...
            # determine how many disks constitue this current prism
            disk_count = int(round(fix['elapsed_time'] / disk_interval, 0))
            # get a layer representing point x_i
            result = arcpy.MakeFeatureLayer_management(
                in_trajectory.in_features, "x_i",
                '"' + str(in_trajectory.oid_field_name) + '"' + ' = ' +
                str(fix['OID']))
            x_i_layer = result.getOutput(0)
            # get a layer representing point x_j
            result = arcpy.MakeFeatureLayer_management(
                in_trajectory.in_features, "x_j",
                '"' + str(in_trajectory.oid_field_name) + '"' + ' = ' +
                str(in_trajectory.fixes[in_trajectory.fixes.index(fix) +
                                        1]['OID']))
            x_j_layer = result.getOutput(0)
            # "Speed" from x_i to x_j
            s_i_j = fix['velocity']
            # Time at first anchor (time at origin fix)
            t_i = 0.0
            # Time at second anchor (time at destination fix)
            t_j = t_i + fix['elapsed_time']
            distances_from_x_i = EucDistance(x_i_layer, cell_size=cell_size)
            distances_from_x_j = EucDistance(x_j_layer, cell_size=cell_size)
            for disk_number in range(disk_count):
                t = float((disk_number + 1) * disk_interval)
                f_i_accessible_distance = (t -
                                           t_i) * s_i_j * velocity_multiplier
                f_j_accessible_distance = (t_j -
                                           t) * s_i_j * velocity_multiplier
                f_i_cone = LessThanEqual(distances_from_x_i,
                                         f_i_accessible_distance)
                f_j_cone = LessThanEqual(distances_from_x_j,
                                         f_j_accessible_distance)
                Z_i_j_disk = BooleanAnd(f_i_cone, f_j_cone)

                # Disks are bundled with their start time as a datetime object
                # This 'start time' for the disk is synonymous with the minimum
                # z-axis value for voxels in the disk.

                disk_z_minimum = fix['timestamp'] + datetime.timedelta(
                    seconds=(t - disk_interval))
                out_tuple = (Z_i_j_disk, disk_z_minimum)
                ppa_rasters.append(out_tuple)

        else:
            pass
    return ppa_rasters


def probabilistic_space_time_prism(in_features, timestamp_field, disk_interval,
                                   cell_size, velocity_multiplier,
                                   expand_edges_factor):
    '''Generates the PSTP voxel space-time prisms from in_trajectory. This
    pstp result is returned as an ordered list of arcpy raster objects. Each
    raster represents one space time disk. All timings are recorded in seconds.
    This function does not account for stationary activity time, and assumes
    the object was in-motion from departure to arrival. This function requires
    a spatial analyst license.
    '''
    # First, prepare a Trajectory object from the input dataset
    in_trajectory = Trajectory(in_features, timestamp_field)
    # Ensure the user's disk interval is smaller than the minimum time elapsed
    if disk_interval > in_trajectory.minimum_disk_interval:
        raise ValueError(
            'Disk interval {0} is > shortest interval in trajectory of {1}'.
            format(disk_interval, in_trajectory.minimum_disk_interval))
    # Prepare the analysis extent to cover more area using the expand_edges_factor
    arcpy.env.extent = arcpy.Extent(
        (in_trajectory.extent.XMin -
         (in_trajectory.extent.width * expand_edges_factor)),
        (in_trajectory.extent.YMin -
         (in_trajectory.extent.height * expand_edges_factor)),
        (in_trajectory.extent.XMax +
         (in_trajectory.extent.width * expand_edges_factor)),
        (in_trajectory.extent.YMax +
         (in_trajectory.extent.height * expand_edges_factor)))
    pstp_rasters = []
    for fix in in_trajectory.fixes:
        if in_trajectory.fixes.index(fix) != in_trajectory.fixes.index(
                in_trajectory.fixes[-1]) or (in_trajectory.fixes.index(
                    fix) == in_trajectory.fixes.index(in_trajectory.fixes[-1])
                                             and fix['elapsed_time'] != 0):
            # if not the last fix in the trajectory, then...
            # determine how many disks constitue this current prism
            disk_count = int(round(fix['elapsed_time'] / disk_interval, 0))
            # get a layer representing point x_i
            result = arcpy.MakeFeatureLayer_management(
                in_trajectory.in_features, "x_i",
                '"' + str(in_trajectory.oid_field_name) + '"' + ' = ' +
                str(fix['OID']))
            x_i_layer = result.getOutput(0)
            # get a layer representing point x_j
            result = arcpy.MakeFeatureLayer_management(
                in_trajectory.in_features, "x_j",
                '"' + str(in_trajectory.oid_field_name) + '"' + ' = ' +
                str(in_trajectory.fixes[in_trajectory.fixes.index(fix) +
                                        1]['OID']))
            x_j_layer = result.getOutput(0)
            # "Speed" from x_i to x_j
            s_i_j = fix['velocity']
            # Time at first anchor (time at origin fix)
            t_i = 0.0
            # Time at second anchor (time at destination fix)
            t_j = t_i + fix['elapsed_time']
            distances_from_x_i = EucDistance(x_i_layer, cell_size=cell_size)
            distances_from_x_j = EucDistance(x_j_layer, cell_size=cell_size)
            '''The main idea below is to obtain a set of point locations
            representing the disk centers for the K disks to be produced. Each
            disk center is obtained by moving proportionally along a line
            created from x_i and x_j (this is a straight-line space-time
            path), capturing disk center points along the way. These disk
            centers are leveraged to obtain euclidean distances during IDW
            steps.
            '''
            # Build a Polyline geometry object from x_i and x_j fix information
            disk_centers = []
            try:
                line_array = arcpy.Array([
                    fix['geometry'].firstPoint,
                    in_trajectory.fixes[in_trajectory.fixes.index(fix) +
                                        1]['geometry'].firstPoint
                ])
                line_i_j = arcpy.Polyline(line_array,
                                          in_trajectory.spatial_reference)
                for disk_number in range(disk_count):
                    t = float(disk_number * disk_interval)
                    progress_factor = t / (t_j - disk_interval)
                    progress_distance = line_i_j.length * progress_factor
                    disk_center_point = line_i_j.positionAlongLine(
                        progress_distance)
                    disk_centers.append(disk_center_point)
            except Exception as e:
                print(e)
                pass
            result = arcpy.CopyFeatures_management(disk_centers, "centers")
            centers_fc = result.getOutput(0)
            centers_oid = arcpy.Describe(centers_fc).OIDFieldName
            for disk_number in range(disk_count):
                # t is the amount of seconds passed since t_i as a float value.
                t = float((disk_number + 1) * disk_interval)
                f_i_accessible_distance = (t -
                                           t_i) * s_i_j * velocity_multiplier
                f_j_accessible_distance = (t_j -
                                           t) * s_i_j * velocity_multiplier
                f_i_cone = LessThanEqual(distances_from_x_i,
                                         f_i_accessible_distance)
                f_j_cone = LessThanEqual(distances_from_x_j,
                                         f_j_accessible_distance)
                Z_i_j_disk = BooleanAnd(f_i_cone, f_j_cone)
                # We have the disk boundaries, next we apply IDW
                # Create a layer for the disk center point
                result = arcpy.MakeFeatureLayer_management(
                    centers_fc, "k_center", '"' + str(centers_oid) + '"' +
                    ' = ' + str(disk_number + 1))
                k_center_layer = result.getOutput(0)
                # Get a EucDistance surface radiating out from this point
                k_distances = EucDistance(k_center_layer, cell_size=cell_size)
                # Use multiplication to isolate disk distance values
                disk_distances = Times(k_distances, Z_i_j_disk)
                disk_idw = (1.0 / disk_distances)
                if disk_idw.mean is not None:

                    disk_array = arcpy.RasterToNumPyArray(disk_idw,
                                                          nodata_to_value=0)
                    out_disk_idw = disk_idw / float(disk_array.sum())

                    # Disks are bundled with their start time as a datetime object
                    # This 'start time' for the disk is synonymous with the minimum
                    # z-axis value for voxels in the disk.

                    disk_z_minimum = fix['timestamp'] + datetime.timedelta(
                        seconds=(t - disk_interval))
                    out_tuple = (Con(IsNull(out_disk_idw), 0,
                                     out_disk_idw), disk_z_minimum)
                    pstp_rasters.append(out_tuple)
        else:
            pass
    return pstp_rasters


def main():
    return


if __name__ == "__main__":
    main()