#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:54:03 2025

@author: Jean Negrel
"""

import os
import xml.etree.ElementTree as ET
import json
import pandas as pd
import zipfile
import glob
from datetime import datetime as dt

# Read template xml file and return it
def import_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root

# Unzip the archive exported from QuinCe into the temporary folder
def unzip_data(data_file):
    with zipfile.ZipFile(data_file, 'r') as zipf:
        zipf.extractall(tmp_path)

# Load the metadata contained in the manifest.json file as well as the data in
# the tsv file.
# The original data zipfile is unpacked into the temp folder in order to load
# the .tsv file.
def import_metadata(tmp_folder, data_file):
    unzip_data(data_file)
    metadata_fname = os.path.join(tmp_folder, 'manifest.json')
    with open(metadata_fname, 'r') as file:
        metadata = json.load(file)
    data_fname = os.path.join(
        tmp_folder,
        'dataset',
        'SOCAT',
        zip_fname.replace('.zip','.tsv')
        )
    data = pd.read_csv(data_fname, delimiter = '\t')
    return metadata, data

# Fill the missing data in the template xml file with data found in the metadata
# and/or datafile
#
# TODO: retrieve url/doi from carbon portal
def get_value(tag, metadata):
    if 'metadataRecordCreationDate' in tag:
        value = dt.today().date().isoformat()
    if 'submissionDate' in tag:
        value = metadata['manifest']['metadata']['last_touched'][:10]
    if 'metadataURL' in tag:
        value = 'TODO'
    if 'datasetURL' in tag:
        value = 'TODO'
    if 'datasetDOI' in tag:
        value = 'TODO'
    if 'startDate' in tag:
        value = metadata['manifest']['exportFiles']['SOCAT']['validStartDate'][:10] # Should the date be "rounded"?
    if 'endDate' in tag:
        value = metadata['manifest']['exportFiles']['SOCAT']['validEndDate'][:10] # Same question?
    if 'westernBounds' in tag:
        value = str(metadata['manifest']['exportFiles']['SOCAT']['validBounds']['west'])
    if 'easternBounds' in tag:
        value = str(metadata['manifest']['exportFiles']['SOCAT']['validBounds']['east'])
    if 'northernBounds' in tag:
        value = str(metadata['manifest']['exportFiles']['SOCAT']['validBounds']['north'])
    if 'southernBounds' in tag:
        value = str(metadata['manifest']['exportFiles']['SOCAT']['validBounds']['south'])
    if 'expocode' in tag:
        value = metadata['manifest']['metadata']['name']
    return value

# Recursive function that scans all the xml structure, looking for missing data
#
# TODO: missing data are currently filled with 'TK' value in the xml file. Probably
# improvement to do here
#
# NB: for some reason the test for leave value within the loop causes the recursive
# call to crash (something to do with local variables). To be investigated further
# later on for optimisation.
def populate_xml(xml_data, metadata):
    if len(list(xml_data))==0:
            if xml_data.text == 'TK':
                xml_data.text = get_value(xml_data.tag, metadata)
    for child in xml_data:
        child = populate_xml(child, metadata)
    return xml_data


# Save the competed xml file into the data folder
#
# TODO: Verify folder organisation
def save_xml(xml_data, tmp_folder):
    fname = os.path.join(tmp_folder, tmp_folder.split('/')[-1] + '.xml')
    xml_str = ET.tostring(xml_data).decode()
    with open(fname, 'w') as xml_file:
        xml_file.write(xml_str)

# Recompress the data into a zip ready for upload.
#
# TODO: Verify structure and maybe clean extra/unecessary files (for instance raw/)
def repack_zip(tmp_folder, data_file):
    with zipfile.ZipFile(data_file, 'w') as zipf:
        for root, dirs, files in os.walk(tmp_folder):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(tmp_folder, '..')))

# Clean up the temporary files to avoid unecessary fill up of hard-drive
def clean_tmp(tmp_folder):
    for root, dirs, files in os.walk(tmp_folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(tmp_folder)

# Define various useful path and file names
#
# TODO: modify the main script to be able to call it as a command line with 
# parameters directly for terminal to easy processing
base_path = 'Data/'
tmp_path = '/tmp/'
xml_path = ''
xml_fname = '1199_template.xml'
data_path = ''
zip_fname = '1199.zip'
zip_fname = 'NRT74FS1695385225200.zip'

# Create the file names with full path
xml_file = os.path.join(base_path, xml_path, xml_fname)
data_file = os.path.join(base_path, data_path, zip_fname)
tmp_folder = os.path.join(tmp_path, zip_fname.split('.')[0])

# Import the template xml file data
xml_data = import_xml(xml_file)
# Import the metadata from manifest.json and data from .tsv file
metadata, data = import_metadata(tmp_folder, data_file)
# Fill up the missing metadata in the xml file
xml_data = populate_xml(xml_data, metadata)
# write the xml file to disk
save_xml(xml_data, tmp_folder)
# Recompress the data with updated metadata into a file for import into SOCAT
repack_zip(tmp_folder, data_file)
# Clean after yourself :)
clean_tmp(tmp_folder)