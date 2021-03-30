import geopandas as gpd

def binary_vector(source, ancillary, exclude_col=(), 
                  exclude_val= [None], suffix= '', cols= [None]):
    """Calculates areal weight using the binary dasymmetric method.
    
    :param source: Name of Dataframe that contains values that should be interpolated
    :type source: string
    :param ancillary: Name of dataframe containing ancillary geometry data, used to mask source dataframe
    :type ancillary: string
    :param exclude_col: Column name from ancillary dataframe that contains exclusionary values
    :type exclude_col: string
    :param exclude_val: Values from exclude_col that should be removed during binary mask operation
    :type exclude_val: list
    :param suffix: Suffix that should be added to the column names that are interpolated
    :type suffix: string
    :param cols: Column names that should be interpolated
    :type cols: list
    
    :return: Source dataframe with interpolated columns added
    :rtype: dataframe
    """    
    # index group 
    source['division'] = source.index
           
    #drop excluded rows from ancillary data
    binary_mask = ancillary[exclude_col].isin(exclude_val)
    ancillary = ancillary[~binary_mask]
    
    #drop all columns except geometry before join (don't want data from ancillary in final df)
    ancillary = ancillary[['geometry']]
          
    #intersect source file and ancillary file
    mask = gpd.overlay(source, ancillary, how='intersection')
    
    #calculate and store areas of intersected zone
    mask['intersectarea'] = (mask.area)  

    #calculate sum of polygon areas by tract     
    masksum = mask.groupby('division')['intersectarea'].sum()
    
    # merge summmed areas back to main dataframe
    target = mask.merge(masksum, on='division')
    
    # calculate areal weight of areas
    target["AREAL_WT"] = target['intersectarea_x'] / target['intersectarea_y']

    # loop through columns that user wants to interpolate, add suffix
    new_cols = []
    for col in cols:
        new_col = col + suffix
        new_cols.append(new_col)
        target[new_col] = target["AREAL_WT"] * target[col]
    
    # drop generated columns
    output = target
    output = output.drop(['division','intersectarea_x','intersectarea_y', 'AREAL_WT'], axis=1)
    return output
