import arcpy
from arcpy.sa import *


def disk_probabilistic_or_operation(first_disk, second_disk):
    'Probabilistic OR operation accross space-time disks'
    result = Con(IsNull(first_disk), 0, first_disk) + Con(
        IsNull(second_disk), 0,
        second_disk) - (Con(IsNull(first_disk), 0, first_disk) *
                        Con(IsNull(second_disk), 0, second_disk))
    return result


def path_to_raster(input_raster_path):
    return Raster(input_raster_path)


def comprehensive_probability_surface(input_rasters):
    'Performs the CPS operation accross prism space time disks (a list of Raster objects)'
    counter = 0
    for raster in input_rasters:
        if counter == 0:
            next_raster = input_rasters[(counter + 1)]
            comp_surface = disk_probabilistic_or_operation(raster, next_raster)
        elif counter != len(input_rasters) - 1:
            next_raster = input_rasters[(counter + 1)]
            comp_surface = disk_probabilistic_or_operation(
                comp_surface, next_raster)
        else:
            pass
        counter += 1
    return comp_surface


def main():
    return


if __name__ == "__main__":
    main()