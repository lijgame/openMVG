#!/usr/bin/python
#! -*- encoding: utf-8 -*-

# This file is part of OpenMVG (Open Multiple View Geometry) C++ library.

# Python implementation of the bash script written by Romuald Perrot
# Created by @vins31
# Modified by Pierre Moulon
#
# this script is for easy use of OpenMVG
#
# usage : python openmvg.py image_dir
#
# image_dir is the input directory where images are located
# output_dir is where the project must be saved
#
# if output_dir is not present script will create it
#

# Indicate the openMVG binary directory
import sys
import subprocess
import os
OPENMVG_SFM_BIN = r"build/Linux-x86_64-Release"
if os.name == 'nt':
    OPENMVG_SFM_BIN = r"src\out\build\x64-Release\Windows-AMD64-RelWithDebInfo"

OPENMVG_SFM_BIN = os.path.abspath(OPENMVG_SFM_BIN)

# Indicate the openMVG camera sensor width directory
CAMERA_SENSOR_WIDTH_DIRECTORY = os.path.abspath(r"src/openMVG/exif/sensor_width_database")
if len(sys.argv) < 2:
    print("Usage %s image_dir output_dir" % sys.argv[0])
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = os.path.join(input_dir, "openMVG_global_output")
matches_dir = os.path.join(output_dir, "matches")
reconstruction_dir = os.path.join(output_dir, "reconstruction_global")
camera_file_params = os.path.join(
    CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

print("Using input dir  : ", input_dir)
print("      output_dir : ", output_dir)

# Create the ouput/matches folder if not present
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
if not os.path.exists(matches_dir):
    os.mkdir(matches_dir)

print("1. Intrinsics analysis")
pIntrisics = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),
                               "-i", input_dir, "-o", matches_dir, "-d", camera_file_params])
pIntrisics.wait()

print("2. Compute features")
pFeatures = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),
                              "-i", os.path.join(matches_dir, "sfm_data.json"), "-o", matches_dir, "-m", "SIFT"])
pFeatures.wait()

print("3. Compute matches")
pMatches = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),
                             "-i", os.path.join(matches_dir, "sfm_data.json"), "-o", matches_dir, "-g", "e"])
pMatches.wait()

# Create the reconstruction if not present
if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir)

print("4. Do Global reconstruction")
pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_GlobalSfM"),
                            "-i", os.path.join(matches_dir, "sfm_data.json"), "-m", matches_dir, "-o", reconstruction_dir])
pRecons.wait()

print("5. Colorize Structure")
pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i",
                            os.path.join(reconstruction_dir, "sfm_data.bin"), "-o", os.path.join(reconstruction_dir, "colorized.ply")])
pRecons.wait()

# optional, compute final valid structure from the known camera poses
print("6. Structure from Known Poses (robust triangulation)")
pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", os.path.join(reconstruction_dir, "sfm_data.bin"), "-m", matches_dir, "-f", os.path.join(matches_dir, "matches.e.bin"), "-o", os.path.join(reconstruction_dir, "robust.bin")])
pRecons.wait()

pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i",
                            os.path.join(reconstruction_dir, "robust.bin"), "-o", os.path.join(reconstruction_dir, "robust_colorized.ply")])
pRecons.wait()
