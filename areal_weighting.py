import geopandas as gpd
import pandas as pd


def arealwt(source, target, cols = [None], suffix = ''):
    """
    Interpolates values from source polygons into target polygons using simple
    areal weighting.

    Parameters
    ----------
    source : DataFrame
        Dataframe with values for interpolation.
    target : DataFrame
        DataFrame with polygons obtaining interpolated values.
    cols : list
        Column(s) from source to be interpolated. 
    suffix : str, optional
        New name for interpolated columns. The default is ''.

    Returns
    -------
    final : Dataframe
        Target dataframe with interpolated columns added.

    """
    #reindex for sum of interpolated results to merge later
    target['_index'] = target.index
    
    #calculate source areas
    source['source_area'] = source.geometry.area
    
    #intersect source and target
    joined1 = gpd.overlay(source, target, how = 'intersection')
    
    #calculate intersected areas
    joined1['intersect_area'] = joined1.geometry.area
    
    #calculate areal weight per intersected polygon
    joined1["AREAL_WT"] = joined1['intersect_area'] / joined1['source_area']    
    
    #interpolate designated columns, create list to include in target dataframe
    new_cols = []
    for col in cols:
        new_col = col + suffix
        new_cols.append(new_col)
        joined1[new_col] = joined1["AREAL_WT"] * joined1[col]
    
    #merge interpolated results to target dataframe
    results = joined1.groupby('_index').sum()
    final = pd.merge(target, results[new_cols], on='_index')
    del final['_index']
    return final




