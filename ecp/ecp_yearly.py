#  Copyright (c) 2022, Battelle Memorial Institute
import os
#import csv
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapz

plt.rcParams['savefig.directory'] = os.getcwd()

vbase = 7621.0
tstep = 3600.0
tbase = 3600.0

def collect_columns (d, cols, base=None):
  v = np.zeros(d.shape[0])
  for i in cols:
    v += d[:,i]
  if base is not None:
    v /= base
  return v

def make_timebase (d, base=1.0):
  n = d.shape[0]
  return np.linspace (0.0, tstep * float(n - 1) / base, n)

if __name__ == '__main__':
  d1 = np.loadtxt('ecp_yearly_Mon_pq1_1.csv', skiprows=1, delimiter=',')
  d2 = np.loadtxt('ecp_yearly_Mon_pq2_1.csv', skiprows=1, delimiter=',')
  p1 = collect_columns (d1, cols=[2,4,6])
  q1 = collect_columns (d1, cols=[3,5,7])
  p2 = collect_columns (d2, cols=[2,4,6])
  q2 = collect_columns (d2, cols=[3,5,7])
  t = make_timebase (d1, base=tbase)

  e1 = 0.001 * np.trapz (p1, dx=tstep/tbase)
  e2 = 0.001 * np.trapz (p2, dx=tstep/tbase)
  print ('Total Energy Load1={:.2f} Load2={:.2f} MWh'.format (e1, e2))

  fig, ax = plt.subplots(1, 2, figsize=(10,6))
  ax[0].set_ylabel('Power [kW]')
  ax[0].plot(t, p1, color='red', label='Load 1 orig')
  ax[0].plot(t, p2, color='blue', label='Load 2 orig')
  ax[0].set_xlabel('Time [hr]')
  ax[0].legend()
  ax[0].grid()

  ax[1].set_ylabel('Reactive Power [kvarh]')
  ax[1].plot(t, q1, color='red', label='Load 1 orig')
  ax[1].plot(t, q2, color='blue', label='Load 2 orig')
  ax[1].set_xlabel('Time [hr]')
  ax[1].legend()
  ax[1].grid()

  plt.show()