# Copyright (C) 2021-2022 Battelle Memorial Institute
# file: test_cimder.py

import cimhub.api as cimhub
import cimhub.CIMHubConfig as CIMHubConfig
import os
import sys

if sys.platform == 'win32':
  cfg_json = '../queries/cimhubjar.json'
else:
  cfg_json = '../queries/cimhubdocker.json'

test_mRID = 'F9A70D1F-8F8D-49A5-8DBF-D73BF6DA7B29'  # 13-bus
test_froot = 'test13'

# empty the database, load 2 test feeders, then delete one
cimhub.clear_db (cfg_json)
xml_path = '../model_output_tests/'  # copied from the example directory, different mRIDs than platform
CIMHubConfig.ConfigFromJsonFile (cfg_json)
for fname in ['IEEE13']:
  cmd = 'curl -D- -H "Content-Type: application/xml" --upload-file ' + xml_path + fname + '.xml' + ' -X POST ' + CIMHubConfig.blazegraph_url
  os.system (cmd)
cimhub.list_feeders ()
cimhub.summarize_db (cfg_json)

# der testing
der_fname = test_froot + '_new_der.dat'
der_uuids = test_froot + '_new_der_uuid.txt'
cimhub.insert_der (cfg_json, der_fname)
cimhub.summarize_db (cfg_json)
