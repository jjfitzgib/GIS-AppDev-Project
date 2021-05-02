import geopandas as gpd
from parcel_method_final import parcel_method

def expert_system(large_zone, small_zone, parcel, tu_col, ru_col, ba_col, ra_col, intp_col):
        
    """Determines whether to use the residential unit or adjusted residential area dasymetric calculations
    for the parcel based method based on the expert system implementation. 
    Large and small interpolation zones must share the same column names for columns used in the arguments.
    Small intepolation zones must nest within large interpolation zones.
    
    :param large_zone: DataFrame with larger geography
    :type large_zone: Dataframe
    :param small_zone: DataFrame with smaller geography
    :type small_zone: Dataframe
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
    :param intp_col: Column name from Zone DataFrame containing values to interpolate. Only accepts one column
    :type intp_col: string
    
    :return: Dataframe at parcel level containing interpolated values based on expert system implementation
    :rtype: dataframe
    """    
    
    # index small_zone
    small_zone['index_s'] = small_zone.index
    
    # call parcel method on large interpolation zone
    expert_large = parcel_method(large_zone, parcel, tu_col, ru_col, ba_col, ra_col, [intp_col])    
    # call parcel method on small interpolation zone
    expert_small = parcel_method(small_zone, parcel, tu_col, ru_col, ba_col, ra_col, [intp_col])
       
    # overlay the interpolated large zone with small zone, so that it can later by grouped by small zone index
    expert = gpd.overlay(expert_large, small_zone, how='intersection')
    
    # sum ara at small zone level 
    expert_ara = expert.groupby('index_s')['ara_derived_' + intp_col].sum().reset_index(name='expert_ara')    
    # sum ru at small zone level
    expert_ru = expert.groupby('index_s')['ru_derived_' + intp_col].sum().reset_index(name='expert_ru')
    
    # merge ru and ara into same dataframe
    expert_parcel = expert_ara.merge(expert_ru, on = 'index_s')
    
    # pop diff calculation
    expert_parcel['ara_diff'] = abs(expert_small[intp_col] - expert_parcel['expert_ara'])
    expert_parcel['ru_diff'] = abs(expert_small[intp_col] - expert_parcel['expert_ru'])
    
    # merge the aggregated data back with the small zone interpolated parcel dataframe
    expert_parcel = expert_small.merge(expert_parcel, on='index_s')
    
    # apply the expert system
    expert_parcel['expert_system_interpolation'] = expert_parcel.apply(lambda x: x['ru_derived_' + intp_col] 
                                                           if x['ru_diff']<=x['ara_diff']
                                                           else x['ara_derived_' + intp_col], axis=1)
    expert_parcel.drop(['index_s', 'expert_ara', 'expert_ru', 'ara_diff', 'ru_diff'], axis=1, inplace = True)
    return expert_parcel
