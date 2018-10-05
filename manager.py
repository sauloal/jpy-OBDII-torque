import os, sys
from collections import OrderedDict

DB_EXT  = '.xlsx'
RAW_EXT = '.csv'
PREFIX  = 'trackLog-'
SEP     = '_'+PREFIX

MONTHS  = ',Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec'.split(',')

def get_in_folder_prefix(in_folder):
    prefix      = in_folder.replace('/','_')
    return prefix

def get_db_files(db_folder, in_folder):
    prefix = get_in_folder_prefix(in_folder)

    files      = [os.path.join(db_folder, f) for f in os.listdir(db_folder) if f.endswith(DB_EXT) and f.startswith(prefix+SEP) and not os.path.isdir(f) ]
    files.sort()
    
    return files

def get_raw_files(in_folder):
    files    = [f for f in os.listdir(in_folder) if f.endswith(RAW_EXT) and f.startswith(PREFIX) and not os.path.isdir(f) ]
    
    return files

def get_raw_files_ordered(in_folder):
    orderedFiles = {}

    files = get_raw_files(in_folder)
    
    for f in files:
        g          = f.replace(PREFIX,'').replace(RAW_EXT,'')
        date, hour = g.split("_")
        yr, mo, da = date.split('-')
        hr, mi, se = [int(h) for h in hour.split('-')]
        yr, da     = int(yr), int(da)
        mo         = MONTHS.index(mo)
        orderedFiles[(yr, mo, da, hr, mi, se)] = os.path.join(in_folder, f)

    orderedFiles = OrderedDict(sorted(orderedFiles.items()))

    #print(orderedFiles)
    
    return orderedFiles

def get_db_date_files(db_folder, in_folder):
    files = get_db_files(db_folder, in_folder)
    
    prefix = get_in_folder_prefix(in_folder)
    
    date_file_pairs = OrderedDict([ (k.replace(prefix+SEP,'').replace(DB_EXT,'').replace(db_folder+'/',''),k) for k in files ])
    
    return date_file_pairs
