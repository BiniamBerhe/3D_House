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
import requests
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import streamlit as st
from utils.ploting import get_coordinates, get_bounds,get_tif, check_tif_location,clip_tif,plot_tif

address_csv = './House_address/Belgium_houses_address.csv'
dsm_path = '/media/biniam/Elements/data/DSM/**/*.tif'
dtm_path = '/media/biniam/Elements/data/DTM/**/*.tif'

if __name__ == '__main__':

    start = time.time()
    st.title("3D Houses in Belgium")
    address = st.text_input('Enter an address from Brussels or Flanders: ')
    n = st.text_input('Please provide an area for your 3D house: ')
    if len(address) > 0:
        response = requests.get(f'https://loc.geopunt.be/v4/Location?q={address}')

        address_dict = response.json()

        if len(address_dict['LocationResult']) == 0:
            st.error('This address does not exist in our database. Please try another address.')
        else:
            if n:
                n = int(n)
                xx,yy = get_coordinates(address)
                tif_file = get_tif(dsm_path)
                tif_bounds = get_bounds(tif_file)
                found_dsm_path, found_dtm_path = check_tif_location(tif_bounds,xx,yy)
                img_dsm = clip_tif(n,address,xx,yy,found_dsm_path,found_dtm_path)
                plot_tif(img_dsm,address)
                st.write('The address is: ', address)



