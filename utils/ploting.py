import pandas as pd

from glob import glob  
from natsort import natsorted, ns

import geopy
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import rasterio  
from rasterio.plot import show
from pyproj import Transformer
from rasterio.windows import Window
import rioxarray 

import imageio
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import streamlit as st

#address = "Gramyelaan 24 2960 Brecht"

def get_coordinates(address: str) -> float:

        geolocator = Nominatim(user_agent="3D_house_app")
        location = geolocator.geocode(address)
        
        latitude = location.latitude
        longitude = location.longitude

        transformer = Transformer.from_crs("EPSG:4326", crs_to = 'EPSG:31370' ,always_xy=True)
        lat, lon = transformer.transform(longitude, latitude)

        return lat,lon

def get_tif(path):
    #Function to get all tif files and sort them
    tif_file =[]
    files = glob(path,recursive = True) 
    for file in files: 
        tif_file.append(file)
    tif_file = natsorted(tif_file, alg=ns.IGNORECASE)
    return tif_file

def get_bounds(tif_file):
    tif_bounds = []
    for i in tif_file:
        src = rasterio.open(i)
        tif_bounds.append(src.bounds)
    return tif_bounds

def check_tif_location(bounds,xx,yy):
    found_DSM_path = []
    found_DTM_path = []
    for i,bound in enumerate(bounds,1):
        if (xx >= bound[0] and xx <= bound[2]) & \
            (yy >= bound[1] and yy <= bound[3]):
                if i<=9:
                    found_DSM_path.append('/media/biniam/Elements/data/DSM/DHMVIIDSMRAS1m_k0'+ str(i) + '.zip' +'/GeoTIFF/DHMVIIDSMRAS1m_k0'+ str(i) + '.tif')
                    found_DTM_path.append('/media/biniam/Elements/data/DTM/DHMVIIDTMRAS1m_k0'+ str(i) + '.zip' +'/GeoTIFF/DHMVIIDTMRAS1m_k0'+ str(i) + '.tif')
                    print('Tif location: ', 'DHMVIIDSMRAS1m_k0' + str(i) + '.tif')
                    print('Tif location: ', 'DHMVIIDTMRAS1m_k0' + str(i) + '.tif')
                else:
                    found_DSM_path.append('/media/biniam/Elements/data/DSM/DHMVIIDSMRAS1m_k'+ str(i) + '.zip' +'/GeoTIFF/DHMVIIDSMRAS1m_k'+ str(i) + '.tif')
                    found_DTM_path.append('/media/biniam/Elements/data/DTM/DHMVIIDTMRAS1m_k'+ str(i) + '.zip' +'/GeoTIFF/DHMVIIDTMRAS1m_k'+ str(i) + '.tif')
                    print('Tif location: ', 'DHMVIIDSMRAS1m_k' + str(i) + '.tif')
                    print('Tif location: ', 'DHMVIIDTMRAS1m_k' + str(i) + '.tif')
        else:None
    return found_DSM_path, found_DTM_path

def clip_tif(n,address,xx,yy,found_dsm_path,found_dtm_path):
    #found_dsm_path, found_dtm_path= check_tif_location(get_bounds(get_tif(dsm_path)))
    #xx,yy = get_coordinates(address)
    rast_dsm_df = rioxarray.open_rasterio(found_dsm_path[0],masked=True,chunks=True)
    rast_dtm_df = rioxarray.open_rasterio(found_dtm_path[0],masked=True,chunks=True)

    left,bottom = [(xx-n),(yy+n)],[(xx+n),(yy+n)]
    right,top = [(xx+n),(yy-n)] ,[(xx-n),(yy-n)]
    geometries = [ {'type': 'Polygon', 'coordinates': [[left,bottom, right,top,left]]}]

    clipped_dsm = rast_dsm_df.rio.clip(geometries)
    clipped_dtm = rast_dtm_df.rio.clip(geometries)

    clipped_dsm.rio.to_raster(address +"_dsm.tif",tiled=True, dtype="int32")
    clipped_dtm.rio.to_raster(address +"_dtm.tif",tiled=True, dtype="int32")

    img_dsm= imageio.imread(address +"_dsm.tif")
    img_dtm = imageio.imread(address +"_dtm.tif")
    return img_dsm

def plot_tif(img_dsm, address):

    with rasterio.open(address +"_dsm.tif") as src:
        lidar_dsm_im = src.read(1, masked=True)
        dtm_meta = src.profile

    with rasterio.open(address +"_dtm.tif") as src:
        lidar_dtm_im = src.read(1, masked=True)
        dsm_meta = src.profile
    
    lidar_chm = lidar_dsm_im - lidar_dtm_im
    
    with rasterio.open(address +'_chm.tif', 'w', **dsm_meta) as ff:
        ff.write(lidar_chm,1)
        
    chm_tif = address +'_chm.tif'

    # Each chm is a numpy matrix
    chm = imageio.imread(chm_tif)
    z1 = imageio.imread(chm_tif)

    fig = go.Figure(data=[go.Surface(z=z1)])
    fig.update_layout(title='CHM', autosize=False, width=1000, height=800)
    fig.write_html("file.html")
    #fig.show()
    st.plotly_chart(fig)
#plot_tif(clip_tif(n,address))