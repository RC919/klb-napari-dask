import napari
import dask.array as da

# https://docs.dask.org/en/latest/caching.html
# Using fixed sized cache [Need the Cachey module, so 'pip install cachey' first, 12-03-2019]
from dask.cache import Cache
cache = Cache(8e9)  # Leverage eight gigabytes of memory
cache.register()    # Turn cache on globally

# Read the zarr images
memimage = da.from_zarr('W:/SV3/RC_15-06-11/Dme_E2_His2AvRFP_spiderGFP_12-03_20150611_155054.corrected/Results/zarr/membrane.zarr')
nucimage = da.from_zarr('W:/SV3/RC_15-06-11/Dme_E2_His2AvRFP_spiderGFP_12-03_20150611_155054.corrected/Results/zarr/nuclei.zarr')
print(type(memimage),memimage.shape,memimage.dtype)

# create Qt GUI context
with napari.gui_qt():
    # create a Viewer and add the images as layers
	viewer = napari.Viewer(axis_labels = ['view','t','z','y','x'])
	viewer.add_image(memimage, scale = [1,1,8,1,1], colormap='inferno', blending='additive', name='membrane', is_pyramid = False, rgb = False, contrast_limits = [10,255])
	viewer.add_image(nucimage, scale = [1,1,8,1,1], colormap='green', blending='additive', name='nuclei', is_pyramid = False, rgb = False, contrast_limits = [10,355])
	
	#scale = [1,1,8,1,1] # [view,t,z,y,x]