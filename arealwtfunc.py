# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 09:29:35 2021

@author: tum98420
"""

import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
import mapclassify as mc

#set columns as strings
targetarea = 'ALAND10'
sourcearea = 'AREA_SQMI'
sourcestat = 'size'
targetdivisions = 'NAME10'
finalshp = 'interpolated.shp'

def arealwt(source, target):
    geosource = gpd.read_file(source)
    geotarget = gpd.read_file(target)
    joined1 = gpd.sjoin(geosource, geotarget, how = 'left', op = 'intersects')
    joined1["AREAL_WT"] = joined1[targetarea] / joined1[sourcearea]
    joined1["EST"] = joined1["AREAL_WT"] * joined1[sourcestat]
    results1 = joined1[[targetdivisions, "EST"]].groupby(targetdivisions).sum()
    final = pd.merge(geotarget, results1, on=targetdivisions)
    return final.to_file(finalshp) 


#test
arealwt('apptest/accident_districts.shp', "apptest/c16590ca-5adf-4332-aaec-9323b2fa7e7d2020328-1-1jurugw.pr6w.shp")


# check choropleth map of test data
fig, ax = plt.subplots(1, figsize=(8, 8))

gpd.read_file(finalshp).plot(column='EST', 
           cmap='YlGnBu', 
           edgecolor='0.5',
           ax = ax,
           linewidth=0.5,
           legend=True,
           k=4, 
           scheme='quantiles')


