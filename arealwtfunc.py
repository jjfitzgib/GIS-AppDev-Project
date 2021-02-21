# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 09:29:35 2021

@author: John Fitzgibbons, Michael Ward
"""

import geopandas as gpd
import pandas as pd

# defining the class
class arealWeight:
    
    # parameterized constructor, initializes variables
    # allows end user to input variable file, column, and output names
    def __init__(self, source, target, targetarea, sourcearea,
                 sourcestat, targetdivisions, finalshp):        
        self.source = source
        self.target = target
        self.targetarea = targetarea
        self.sourcearea = sourcearea
        self.sourcestat = sourcestat
        self.targetdivisions = targetdivisions
        self.finalshp = finalshp
    
    # read dataframes function
    def read_df(self):
        self.source_df = gpd.read_file(self.source)
        self.target_df = gpd.read_file(self.target)     
    
    # join dataframes function     
    def join_df(self):  
        self.join = gpd.sjoin(self.source_df, self.target_df,
                              how = 'left', op = 'intersects')          
   
    # execute areal weighting algorithm on dataframes   
    def areal_alg(self):    
        self.join["AREAL_WT"] = self.join[self.targetarea] / self.join[self.sourcearea]
        self.join["EST"] = self.join["AREAL_WT"] * self.join[self.sourcestat]
        results1 = self.join[[self.targetdivisions, "EST"]].groupby(self.targetdivisions).sum()
        final = pd.merge(self.target_df, results1, on=self.targetdivisions)
        return final.to_file(self.finalshp)

    # method for running program
    def run_areal(self):
        self.read_df()
        self.join_df()
        self.areal_alg()
        
        
# creating object of the class invoking constructor
philly = arealWeight('john_data/accident_districts.shp',
                     'john_data/c16590ca-5adf-4332-aaec-9323b2fa7e7d2020328-1-1jurugw.pr6w.shp',
                     'ALAND10', 'AREA_SQMI', 'size', 'NAME10', 'interpolated.shp')

#calling methods using the run function on object that was just created
philly.run_areal()

# need to convert some attributes to private attributes
# need to add a crs check


