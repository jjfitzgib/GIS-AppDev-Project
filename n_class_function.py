import geopandas as gpd

def n_class(source, ancillary, class_col, class_dict, cols = [None], source_identifier = '', suffix = ''):
    """
    Interpolates values into disaggregated source polygons using n_class method with ancillary data.  

    Parameters
    ----------
    source : DataFrame
        DataFrame with values for interpolation.
    ancillary : DataFrame
        DataFrame with area-class map categories.
    class_col : str
        Area-class categories.
    class_dict : dict
        Area-class categories with assigned percentages.
    cols : list
        Column(s) from source to be interpolated.
    source_identifier : str, optional
        Column that identifies source polygons. The default is ''.
    suffix : str, optional
        New name for interpolated columns. The default is ''.

    Returns
    -------
    target : DataFrame
        Target dataframe with interpolated columns.

    """
    #calculate source area
    source['source_area'] = source.geometry.area
    
    #reindex source for grouping sums later
    source['_index'] = source.index
    
    #assign percentages to landuse classes
    for key, value in class_dict.items():
        ancillary.loc[ancillary[class_col]== key, '_percent']=value
    
    #intersect source and ancillary data
    join1 = gpd.overlay(source, ancillary, how='intersection')
    
    #calculate intersected areas
    join1['intersect_area']=join1.geometry.area
    
    #calculate areal weight
    join1['arealwt']=join1['intersect_area']/join1['source_area']
    
    #multiply areal weight by user defined percentages
    join1['class_weight']=join1['_percent'] * join1['arealwt']
    
    #sum of areal weight times percentage per source polygon
    totals = join1.groupby('_index')['class_weight'].sum()
    totals.rename('temp_sum', inplace=True)
    join1 = join1.merge(totals, on ='_index')
    
    #fraction for interpolation
    join1['class_frac'] = join1['class_weight']/join1['temp_sum']
    
    #interpolate designated columns, create list to include in final dataframe
    new_cols = []
    for col in cols:
        new_col = col + suffix
        new_cols.append(new_col)
        join1[new_col] = join1['class_frac']*join1[col]
    
    #filter target dataframe
    if source_identifier:
        target = join1[[source_identifier, class_col, "geometry", *new_cols]]
    else:
        target = join1[[class_col, "geometry", *new_cols]]
      
    return target