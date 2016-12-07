# Mess with the incident reports in pandas


import pandas as pd

# UCPD Stuff
UCPD_RAW = pd.read_csv('foundation/hp_crimes_points.csv')
UCPD_INCIDENT_TYPES = UCPD_RAW['Incident']
UCPD_TYPE_COUNTS = UCPD_INCIDENT_TYPES.value_counts()

UCPD_DISP_TYPES = UCPD_RAW['Disposition']
UCPD_DISP_COUNTS = UCPD_DISP_TYPES.value_counts()

# CPD Stuff
CPD_RAW = pd.read_csv('foundation/cpd/CPD_in_UCPD_zone_2011-2015.csv')
CPD_TYPE_COUNTS = CPD_RAW['Primary Type'].value_counts()

def kw_count(kw):
    '''
    This function takes a keyword (kw) and determines how many crime reports
    have the incident category include this word
    '''
    kw_cnt = 0
    for inc_type in UCPD_UNIQUE_TYPES:
        if kw.lower() in inc_type.lower():
            kw_cnt += inc_type_cnts[inc_type]

    return(kw_cnt)

def make_kw_df_from_ucpd(kw, write = False, df = UCPD_RAW):
    '''
    This function takes a keyword (kw) and returns a dataframe that only includes
    incidents containing the entered keyword from the scraped UCPD data.
    '''
    indices = []
    for index, inc_type in enumerate(UCPD_INCIDENT_TYPES):
        if kw.lower() in inc_type.lower():
            indices.append(index)

    kw_df = UCPD_RAW.iloc[indices]
    if write:
        path = 'ready/hp_crimes_points_{}.csv'.format(kw)
        kw_df.to_csv(path)
        print('CSV Written at \n {}'.format(path))
    return(kw_df)

def make_kw_df_from_cpd(kw, write = False, df = CPD_RAW):
    '''
    This function takes a keyword (kw) and returns a dataframe that only includes
    crimes containing the entered keyword from the CPD data.
    '''
    kw = kw.upper() # CPD 'Primary Type Column' is all  caps
    kw_df = CPD_RAW[CPD_RAW['Primary Type'].str.contains(kw)]

    if write:
        path = 'ready/cpd_hp_crimes_points_{}.csv'.format(kw)
        kw_df.to_csv(path)
        print('CSV Written at: \n{}'.format(path))
    return(kw_df)
