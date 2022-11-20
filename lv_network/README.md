# CIMHub Test Cases for Low-Voltage Distribution

Copyright (c) 2021-2022, Battelle Memorial Institute

## Process

The test cases are executed with ```python3 test_lvn.py```. They cover:

1. IEEE Low-voltage secondary network distribution, with parallel secondary lines retained
2. IEEE Low-voltage secondary network distribution, with secondary lines reduced from 5 or 6 in parallel, to 1 equivalent line
3. European Low-voltage radial distribution

The test cases are configured by entries in the ```cases``` array near the top of ```test_lvn.py```.
Each array element is a dictionary with the following keys:

- **dsspath** provides a path to the original model, in a local copy of the OpenDSS repository
- **dssname** is the root file name of the original OpenDSS base case
- **root** is used to generate file names for converted files
- **mRID** is a UUID4 to make the test case feeder unique. For a new test case, generate a random new mRID with this Python script: ```import uuid;idNew=uuid.uuid4();print(str(idNew).upper())```'
- **glmvsrc** is the substation source line-to-neutral voltage for GridLAB-D
- **bases** is an array of voltage bases to use for interpretation of the voltage outputs. Specify line-to-line voltages, in ascending order, leaving out 208 and 480.
- **export_options** is a string of command-line options to the CIMImporter Java program. ```-e=carson``` keeps the OpenDSS line constants model compatible with GridLAB-D's
- **skip_gld** specify as ```True``` when you know that GridLAB-D won't support this test case
- **check_branches** an array of branches in the model to compare power flows and line-to-line voltages. Each element contains:
    - **dss_link** is the name of an OpenDSS branch for power and current flow; power delivery or power conversion components may be used
    - **dss_bus** is the name of an OpenDSS bus attached to **dss_link**. Line-to-line voltages are calculated here, and this bus establishes flow polarity into the branch at this bus.
    - **gld_link** is the name of a GridLAB-D branch for power and current flow; only links, e.g., line or transformer, may be used. Do not use this when **skip_gld** is ```True```
    - **gld_bus** is the name of a GridLAB-D bus attached to **gld_link**. Do not use this when **skip_gld** is ```True```

The script outputs include the comparisons requested from **check_branches**, and summary information:

- **Nbus** is the number of buses found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **Nlink** is the number of links found in [Base OpenDSS, Converted OpenDSS, Converted GridLAB-D]
- **MAEv** is the mean absolute voltage error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in per-unit. This is based on line-to-neutral voltages.
- **MAEi** is the mean absolute link current error between Base OpenDSS and [Converted OpenDSS, Converted GridLAB-D], in Amperes

## Results

For the IEEE 390-bus low-voltage network, the branch comparisons comprise two transformers, each
serving 4 radial primary feeders. For the European-style radial low-voltage circuit, the branch
comparison is at the feeder head.

```
  OpenDSS branch flow in TRANSFORMER.1 from P4, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     61.88 -0.5938   7149.426 + j  4825.981     AB   241453.08  0.5236
    B 139403.00 -2.0944     61.43 -2.6979   7051.049 + j  4860.561     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.13  1.5020   7070.348 + j  4758.245     CA   241453.94  2.6180
    Total S = 21270.823 + j 14444.787
  OpenDSS branch flow in TRANSFORMER.1 from P4, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     61.88 -0.5938   7149.311 + j  4825.903     AB   241453.08  0.5236
    B 139403.00 -2.0944     61.43 -2.6979   7050.945 + j  4860.490     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.13  1.5020   7070.233 + j  4758.167     CA   241453.94  2.6180
    Total S = 21270.489 + j 14444.560
  GridLAB-D branch flow in XF_1 from P4
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139427.42 -0.0000     54.43 -0.6692   5952.110 + j  4707.761     AB   241496.06  0.5236
    B 139428.12  4.1888     52.58  3.6042   6113.553 + j  4045.582     BC   241496.79 -1.5708
    C 139428.04  2.0944     57.40  1.4947   6606.360 + j  4516.755     CA   241495.56  2.6180
    Total S = 18672.022 + j 13270.097
  OpenDSS branch flow in TRANSFORMER.2 from P8, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     62.56 -0.5955   7219.700 + j  4891.780     AB   241453.08  0.5236
    B 139403.00 -2.0944     62.09 -2.6992   7120.953 + j  4921.594     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.82  1.5008   7144.299 + j  4820.705     CA   241453.94  2.6180
    Total S = 21484.952 + j 14634.079
  OpenDSS branch flow in TRANSFORMER.2 from P8, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     62.56 -0.5955   7219.596 + j  4891.710     AB   241453.08  0.5236
    B 139403.00 -2.0944     62.09 -2.6992   7120.850 + j  4921.522     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.82  1.5008   7144.184 + j  4820.627     CA   241453.94  2.6180
    Total S = 21484.630 + j 14633.860
  GridLAB-D branch flow in XF_2 from P8
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139427.41 -0.0000     55.07 -0.6697   6019.565 + j  4766.067     AB   241496.05  0.5236
    B 139428.11  4.1888     53.17  3.6027   6176.589 + j  4100.435     BC   241496.77 -1.5708
    C 139428.03  2.0944     58.02  1.4940   6674.595 + j  4569.512     CA   241495.54  2.6180
    Total S = 18870.749 + j 13436.014
IEEE390par       Nbus=[  1170,  1170,  1482] Nlink=[  2319,  2319,  1380] MAEv=[ 0.0000, 0.0040] MAEi=[   0.0118,  80.9169]
  OpenDSS branch flow in TRANSFORMER.1 from P4, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     61.88 -0.5938   7149.426 + j  4825.981     AB   241453.08  0.5236
    B 139403.00 -2.0944     61.43 -2.6979   7051.049 + j  4860.561     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.13  1.5020   7070.348 + j  4758.245     CA   241453.94  2.6180
    Total S = 21270.823 + j 14444.787
  OpenDSS branch flow in TRANSFORMER.1 from P4, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     61.90 -0.5945   7148.908 + j  4832.899     AB   241453.08  0.5236
    B 139403.00 -2.0944     61.46 -2.6986   7050.533 + j  4867.470     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.16  1.5013   7069.834 + j  4765.073     CA   241453.94  2.6180
    Total S = 21269.275 + j 14465.443
  OpenDSS branch flow in TRANSFORMER.2 from P8, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     62.56 -0.5955   7219.700 + j  4891.780     AB   241453.08  0.5236
    B 139403.00 -2.0944     62.09 -2.6992   7120.953 + j  4921.594     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.82  1.5008   7144.299 + j  4820.705     CA   241453.94  2.6180
    Total S = 21484.952 + j 14634.079
  OpenDSS branch flow in TRANSFORMER.2 from P8, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A 139403.00  0.0000     62.59 -0.5962   7219.374 + j  4898.917     AB   241453.08  0.5236
    B 139403.00 -2.0944     62.12 -2.6998   7120.496 + j  4928.627     BC   241453.94 -1.5708
    C 139404.00  2.0944     61.85  1.5001   7143.993 + j  4827.760     CA   241453.94  2.6180
    Total S = 21483.863 + j 14655.304
IEEE390          Nbus=[  1170,  1170,     0] Nlink=[  4884,  4884,     0] MAEv=[ 0.0004,-1.0000] MAEi=[   0.2038,  -1.0000]
  OpenDSS branch flow in LINE.LINE1 from 1, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    251.73 -0.5271     93.87 -0.8409     22.476 + j     7.294     AB      436.01 -0.0035
    B    251.73 -2.6215     85.03 -2.9391     20.333 + j     6.685     BC      436.10 -2.0978
    C    251.84  1.5673     67.52  1.2521     16.166 + j     5.271     CA      436.10  2.0908
    Total S =    58.975 + j    19.251
  OpenDSS branch flow in LINE.LINE1 from 1, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    251.75 -0.5271     89.19 -0.8411     21.356 + j     6.935     AB      436.05 -0.0035
    B    251.75 -2.6215     80.61 -2.9393     19.277 + j     6.342     BC      436.14 -2.0978
    C    251.86  1.5673     63.26  1.2519     15.147 + j     4.942     CA      436.14  2.0908
    Total S =    55.780 + j    18.219
  GridLAB-D branch flow in LINE_LINE1 from 1
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A    251.87 -0.5264     89.14 -0.8398     21.358 + j     6.922     AB      436.25 -0.0026
    B    251.90  3.6627     80.55  3.3449     19.275 + j     6.339     BC      436.29 -2.0966
    C    251.96  1.5688     63.23  1.2529     15.143 + j     4.949     CA      436.44  2.0919
    Total S =    55.776 + j    18.211
LVTest           Nbus=[  2721,  2721,  2886] Nlink=[  2776,  2776,  2718] MAEv=[ 0.0008, 0.0013] MAEi=[   0.4376,   0.4469]
```

## Notes on GridLAB-D Conversion

For the IEEE 390-bus network, the secondary parallel lines have to be reduced for GridLAB-D. The model that
retains these parallel lines will not solve.
