import geopandas as gpd

def  lim_var(source, ancillary, class_col, class_dict, cols = [None], source_identifier = '', suffix = ''):
    """
    Interpolates values into disaggregated source polygons using limiting variable method 
    with ancillary data. Thresholds are set for desired area-class categories.  Remaining
    values are interpolated into area-class(es) with threshold designated as 0 or None.  Area
    classes with no intended data should be left out of dictionary.
    
    Parameters
    ----------
    source : DataFrame
        DataFrame with values for interpolation.
    ancillary : DataFrame
        DataFrame with area-class map categories.
    class_col : str
        Area-class categories.
    class_dict : dict
        Area-class categories with assigned thresholds per square unit. 
        Classes with no threshold should be assigned None.
        Classes with no data should not be included in dictionary.
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
    
    #reindex for summing excess data and used area per source polygon
    source['_index'] = source.index
    
    #intersect source and ancillary
    join1 = gpd.overlay(source, ancillary, how='intersection')
    
    #calculate intersected areas
    join1['intersect_area']=join1.geometry.area
    
    #Assign thresholds to area classes
    for key, value in class_dict.items():
        join1.loc[join1[class_col]== key, 'threshold']=value
    
    #start interpolation for designated columns; create new_cols for target dataframe
    new_cols = []
    for col in cols:
        source_copy = col + 'copy'
        if suffix:
            new_col = col + suffix
        else:
            new_col = '_' + col
        new_cols.append(new_col)
        
        #calculate areal weight
        join1['arealwt']=join1['intersect_area']/join1['source_area']
    
        #copy column for interpolation (lambda in loop doesn't work first time without this)
        join1[source_copy] = join1[col]
        
        #set new_col to 0 (lambda in loop doesn't work first time without this)
        join1[new_col] = 0
        
        #create used area column - move area that will never be used
        join1['used_area'] = join1.apply(lambda x: x['intersect_area'] if x[class_col] not in class_dict.keys() else 0, axis=1)
    
        #create copy of class_dict for multiple columns, drop values of None
        class_dict_copy = {key:val for key, val in class_dict.items() if val != None and val != 0}
        
        while class_dict_copy != {}:
        
            #interpolate  
            join1[new_col] = join1.apply(lambda x: x['arealwt']*x[source_copy] if x[class_col] == min(class_dict_copy, key = class_dict_copy.get) else x[new_col], axis=1)
        
            #if new column exceeds threshold, new column gets threshold density
            join1[new_col] = join1[new_col].clip(upper = join1['threshold']*join1['intersect_area'])
               
            #add up successfully interpolated data and decrement
            totals = join1.groupby('_index')[new_col].sum()
            totals.rename('temp_sum', inplace=True)
            join1 = join1.merge(totals, on='_index')
            join1[source_copy] = join1[col] - join1['temp_sum']
            
            #copy used area for decrementing
            join1['used_area'] = join1.apply(lambda x: x['intersect_area'] if x[class_col] == min(class_dict_copy, key = class_dict_copy.get) else x['used_area'], axis=1)
            
            #add up successfully interpolated areas and decrement 
            totals2 = join1.groupby('_index')['used_area'].sum()
            totals2.rename('temp_area_sum', inplace=True)
            join1 = join1.merge(totals2, on ='_index')
            join1['source_area_copy'] = join1['source_area'] - join1['temp_area_sum']
            
            #recalculate areal weight
            join1['arealwt'] = join1['intersect_area']/join1['source_area_copy']
            
            #remove tempsum
            del join1['temp_sum']
            
            #remove temp_area_sum
            del join1['temp_area_sum']
            
            #remove minimum from dictionary
            del class_dict_copy[min(class_dict_copy, key = class_dict_copy.get)]

        #replace null values with 0 for classes with no restriction
        join1.fillna(0, inplace=True)
        
        #interpolate least restrictive
        join1[new_col] = join1.apply(lambda x: x['arealwt']*x[source_copy] if x[class_col] in class_dict and x['threshold'] == 0 else x[new_col], axis=1)

    #filter target dataframe
    if source_identifier:
        target = join1[[source_identifier, class_col, "geometry", *new_cols]]
    else:
        target = join1[[class_col, "geometry", *new_cols]]
        
    return target


