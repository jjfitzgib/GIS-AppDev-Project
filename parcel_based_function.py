import geopandas as gpd

def parcel_method(zone, parcel, tu_col, ru_col, ba_col, ra_col, cols = [None]):     
   
    """Interpolates values using the parcel based method.
    
    :param zone: DataFrame to be interpolated
    :type zone: DataFrame
    :param parcel: Parcel DataFrame
    :type parcel: DataFrame
    :param tu_col: Column name from parcel DataFrame containing total number of units
    :type tu_col: string
    :param ru_col: Column name from parcel DataFrame containing number of residential units
    :type ru_col: string
    :param ba_col: Column name from parcel DataFrame containing building area
    :type ba_col: string
    :param ra_col: Column name from parcel DataFrame containing residential area
    :type ra_col: string
    :param cols: Column names from Zone DataFrame containing values to interpolate. Can accept one or more columns.
    :type intp_col: list
    
    :return: The parcel level DataFrame with two interpolated fields added for each column of input: One derived from residential units, and another derived from adjusted residential area
    :rtype: DataFrame
    """    
    
    # make copies of zone and parcel dataframes
    ara_parcel = parcel.copy()
    zonecopy = zone.copy()
    
    # calculate ara for parcels
    ara_parcel['M'] = ara_parcel.apply(lambda x: 1 if x[ra_col]==0 and x[ru_col] !=0 else 0, axis=1)
    ara_parcel['ara'] = (ara_parcel['M'] *((ara_parcel[ba_col] * ara_parcel[ru_col]) / ara_parcel[tu_col])) + ara_parcel[ra_col]
    
    # sum ara for zone
    zonecopy['_bindex'] = zonecopy.index
    ara_zone = gpd.overlay(zonecopy, ara_parcel, how='intersection')
    ara_zone = ara_zone.groupby('_bindex')['ara'].sum().reset_index(name='ara_zone')         
            
    # calculate RU for zone
    ru_zone = gpd.overlay(zonecopy, parcel, how='intersection')
    ru_zone = ru_zone.groupby('_bindex')[ru_col].sum().reset_index(name='ru_zone')  
    
    # Calculate dasymetrically derived populations based on RU and ara
    intp_zone = gpd.overlay(zonecopy, ara_parcel, how='intersection')
    intp_zone = intp_zone.merge(ru_zone, on='_bindex')
    intp_zone = intp_zone.merge(ara_zone, on='_bindex')
    new_cols = []
    for col in cols:
        new_col = 'ru_derived_' + col 
        new_cols.append(new_col)
        intp_zone[new_col] = intp_zone[col] * intp_zone[ru_col] / intp_zone['ru_zone']
        
    new_cols = []    
    for col in cols:
        new_col = 'ara_derived_' + col 
        new_cols.append(new_col)
        intp_zone[new_col] = intp_zone[col] * intp_zone['ara'] / intp_zone['ara_zone']
    
    # drop generated columns that were just for calculations and indexing
    intp_zone.drop(['M', '_bindex', 'ara', 'ru_zone', 'ara_zone'], axis=1, inplace = True)
    return intp_zone


