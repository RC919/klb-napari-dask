# -*- coding: utf-8 -*-
"""
Created on Wed Oct  31  2019
Modified on Tuesday December 3 2019
@author: Raghav K. Chhetri
"""
import os
from os.path import join
from glob import glob
import numpy as np
import dask
import dask.array as da
import pyklb as klb
from numcodecs import BZ2
import time
# 2701 timepoints; shape of each 3D stack is (75,768,1848)

outPath = 'W:/SV3/RC_15-06-11/Dme_E2_His2AvRFP_spiderGFP_12-03_20150611_155054.corrected/Results/zarr/'
if not os.path.exists(outPath):
    os.makedirs(outPath)

inPath = 'W:/SV3/RC_15-06-11/Dme_E2_His2AvRFP_spiderGFP_12-03_20150611_155054.corrected/Results/TimeFused/'

t0 = time.time()
for ch in range(2):
	if ch == 0:
		fnames = glob(join(inPath, '*/*CHN00.fusedStack.klb' ))
	elif ch == 1:
		fnames = glob(join(inPath, '*/*CHN01.fusedStack.klb' ))
	fnames.sort()
	#fnames = fnames[0:20] #Change the number of timepoints in the empty array below accordingly

	sample = klb.readfull(fnames[0]) #Sample image

	#Generate lazy arrays
	lazy_arrays = [dask.delayed(klb.readfull)(fn) for fn in fnames]
	lazy_arrays = [da.from_delayed(x, shape=sample.shape, dtype=sample.dtype) for x in lazy_arrays]

	#Generate empty object array to organize each chunk that loads the 3D volume
	a = np.empty((2,2701,1,1,1), dtype=object) #Dimension of (view,timepoint,Z,Y,X)
	#a = np.empty((2,10,1,1,1), dtype=object) #Dimension of (view,timepoint,Z,Y,X)

	for fn, x in zip(fnames, lazy_arrays):
		view = int(fn[fn.index("_CM")+3:].split("_")[0])
		timepoint = int(fn[fn.index("_TM")+3:].split("_")[0])
		a[view,timepoint,0,0,0] = x
		print('CM',view,'TM',timepoint)

	#Stitch together all these blocks into a single N-dimensional array
	a = da.block(a.tolist())
	a = a.rechunk((1,1,75,128,308))
	print(type(a), a.shape, a.dtype, a.chunksize, 'Size', round(a.size/(1024**3),2), 'GB')
	
	if ch == 0:
		a.to_zarr(join(outPath, 'membrane-v2.zarr'), compressor=BZ2(level=9))
	elif ch == 1:
		a.to_zarr(join(outPath, 'nuclei-v2.zarr'), compressor=BZ2(level=9))
print('Took',round(time.time()-t0,2), 'sec')