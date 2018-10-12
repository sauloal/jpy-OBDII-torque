# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.1'
#       jupytext_version: 0.8.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

# %%
import os

# %%
import sys
print("SYS", sys.version)

# %%
from collections import OrderedDict

# %%
import datetime
from datetime import timedelta

# %%
from dateutil import parser as date_parser
from dateutil import _version as dateutil_version
print("dateutil", dateutil_version.version)

# %%
import pandas as pd
print("pandas", pd.__version__)

# %%
from IPython.display import display
from IPython import __version__ as IPython_version
print("IPython", IPython_version)

# %%
import json
print('json', json.__version__)

# %%
%load_ext autoreload
%autoreload 2
import manager

# %%
cfg = json.load(open('config.json'))
print('config', cfg)

# %%
in_folder   = cfg['in_folder']

# %%
db_folder   = cfg['db_folder']

# %%
min_time_between_trips_in_minutes = cfg['min_time_between_trips_in_minutes']

# %%
min_time_between_trips_in_seconds = min_time_between_trips_in_minutes * 60

# %%
#https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python
def roundTime(dt=None, roundTo=1):
   """Round a datetime object to any time laps in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds  = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

# %%
def toFloat(val):
    try:
        return float(val)
    except ValueError:
        return None

# %%
def toDate(val):
    try:
        d = date_parser.parse(val)
        #e = d.astimezone(tz=None)
        f = d.replace(tzinfo=None)
        g = roundTime(f,roundTo=1)
        return g
    except ValueError:
        return None

# %%
def guessType(val):
    if val is None:
        return lambda x: None
    
    try:
        val = float(val)
#         print("guessType FLOAT", val)
        return toFloat
    except:
        pass

    try:
        val = date_parser.parse(val)
#         print("guessType DATE", val)
        return toDate
    except:
        pass
    
#     print("guessType STR", val)
    return lambda x: str(x)

# %%
orderedFiles = manager.get_raw_files_ordered(in_folder)

# %%
assert len(orderedFiles) > 0, "NO FILES FOUND"

# %%
print( "\n".join( [ "{:3d}/{:3d} {} {}".format(fn+1, len(orderedFiles), "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(*d), f) for fn, (d,f) in enumerate(orderedFiles.items())if f != '' ] ) )

# %%
data    = OrderedDict()
headers = []
types   = []

for (yr, mo, da, hr, mi, se), f in orderedFiles.items():
    print("{2:02d}/{1:02d}/{0:02d} {3:02d}:{4:02d}:{5:02d} - {6}".format(yr, mo, da, hr, mi, se, f))
    with open(f, 'r') as fhd:
        for ln, line in enumerate(fhd):
            line = line.strip()
#             print(line)
            #if ln == 20: break
            cols = [ l.strip() for l in line.split(',') ]
            
            if cols[-1] == '':
                cols = cols[:-1]
                
            if cols[0] == "GPS Time":
                headers = cols
                types   = [None]*len(headers)
#                 print(headers)
                for h in headers:
                    if h not in data:
                        if len(data.keys()) > 0:
                            data[h] = [None] * len(data[list(data.keys())[0]])
                        else:
                            data[h] = []
            else:
                #assert len(cols) == len(headers), "number of columns for file {} line {} differs {} != {}".format(
                #    f, ln, len(cols), len(headers))
                
                if len(cols) != len(headers):
                    print("number of columns for file {} line {} differs {} != {}".format(
                    f, ln, len(cols), len(headers)))
                    
                    continue

                for h in data:
                    if h in headers:
                        hp  = headers.index(h)
                        val = cols[hp]
                        if val in ['-', '', u'∞']:
                            data[h].append( None )
                        else:
                            if types[hp] is None:
                                types[hp] = guessType(val)
                            val = types[hp](val)
                            data[h].append( val  )
                    else:
                        data[h].append( None )

# %%
#for f, d in data.items():
#    print(u"{:55s} {:12,d}".format(f, len(d)))

# %%
df = pd.DataFrame.from_dict(data)
df.dropna(axis=1, how='all', inplace=True)
# with pd.option_context("display.max_columns",0):
#     display(df)

# %%
cols = list(df)
cols
nunique = df.apply(pd.Series.nunique)
nunique
cols_to_drop = nunique[nunique == 1].index
cols_to_drop
df.drop(cols_to_drop, axis=1, inplace=True)

# %%
with pd.option_context("display.max_columns",0):
    display(df)

# %%
print("\n".join(["{:55} {}".format(k,v) for k,v in sorted(zip(df.dtypes.keys(), df.dtypes.values))]))

# %%
print(df.shape)
df.dropna(subset=['GPS Time'],inplace=True)
df.reset_index(inplace=True, drop=True)
# df.drop(columns=['level_0'], inplace=True)
print(df.shape)
# df

# %%
df["GPS Time DIff"] = df["GPS Time"] - df["GPS Time"].shift()
df.iloc[0,df.columns.get_loc("GPS Time DIff")] = timedelta(seconds=MIN_TIME_BETWEEN_TRIPS_IN_SECONDS*2)
df["GPS Time DIff"]

# %%
df["GPS Time New Trip"] = df["GPS Time DIff"] >= timedelta(seconds=MIN_TIME_BETWEEN_TRIPS_IN_SECONDS)
#df["GPS Time New Trip"]

# %%
df["GPS Time Trip Num"]  = df["GPS Time New Trip"].cumsum()
# df["GPS Time Trip Num"]

# %%
df["GPS Time Trip ID"] = df["GPS Time"]

for trip_num in df["GPS Time Trip Num"].unique():
    trip_vals    = df[["GPS Time","GPS Time Trip Num"]][df["GPS Time Trip Num"] == trip_num]
    num_vals     = len(trip_vals)
    min_time     = trip_vals["GPS Time"].min()
    max_time     = trip_vals["GPS Time"].max()
    del_time     = max_time - min_time
    min_time_str = str(min_time).replace('-','_').replace(':','_').replace(' ','_')
    max_time_str = str(max_time).replace('-','_').replace(':','_').replace(' ','_')
    del_time_str = str(del_time).replace('-','_').replace(':','_').replace(' ','_')
    
    print("trip_num", trip_num, 
          "num_vals", num_vals, 
          "min_time", min_time_str, 
          "max_time", max_time_str, 
          "del_time", del_time_str)
    
    df.iloc[trip_vals.index , df.columns.get_loc("GPS Time Trip ID")] = min_time_str
    
# df["GPS Time Trip ID"]
# df["GPS Time Trip ID"] = df["GPS Time Trip ID"].astype('category')
df["GPS Time Trip ID"].unique(), len(df["GPS Time Trip ID"].unique())

# %%
df[["GPS Time", "GPS Time Trip Num", "GPS Time Trip ID"]][df["GPS Time New Trip"]]

# %%
# df

# %%
print("shape before", df.shape)

df2 = df.drop_duplicates(subset="GPS Time", keep="last")
#         .drop(["GPS Time DIff","GPS Time New Trip"], 1)

print("shape after ", df2.shape)

# %%
df3 = df2.groupby(df2["GPS Time Trip ID"], as_index=True, sort=False, group_keys=True)

# %%
groups = list(df3.groups.keys())

# %%
display(df3.get_group(groups[0]))

# %%
display(df3.get_group(groups[-1]))

# %%
prefix = get_in_folder_prefix(in_folder)

xlsx = os.path.join(db_folder, "{}_batch_from_{}-to_{}.xlsx".format( prefix, groups[0], groups[-1]))

print('saving to Excel', xlsx)

df2.to_excel(xlsx)

# %%
for gn, group in enumerate(df3.groups):
    g            = df3.get_group(group)
    h            = g.dropna(axis=1, how='all')
    cols         = list(h)
    nunique      = h.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    i            = h.drop(cols_to_drop, axis=1)
    
    xlsx = os.path.join(db_folder, "{}_trackLog-{}.xlsx".format( prefix, group))
    
    shapes = " | ".join(["{} - rows {:5,d} columns {:5,d}".format(n, r, c) for n, (r, c) in (  ('all' , g.shape), 
                                                                                               ('na'  , h.shape), 
                                                                                               ('drop', i.shape))])
    
    print('saving to Excel {:3d}/{:3d} {}\n\t{}'.format(gn+1, len(df3.groups), xlsx, shapes))
    i.to_excel(xlsx)

#     display( g )

# %%
for f in orderedFiles.values():
#     t = f+".done"
#     print( "renaming", f, "to", t )
#     os.rename(f, t)
    if os.path.exists(f):
        print( "compressing", f )
        !gzip -1 $f
    else:
        print( f, "already compressed" )

# %%

