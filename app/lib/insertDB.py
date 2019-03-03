import numpy as np
from netCDF4 import Dataset
from mongoDB import MongoDB_lc
import pandas as pd
import os

def get_data(filez):
    location = filez
    ncin = Dataset(location, 'r')
    name = ['Ann','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # name = ['Annual','January','February','March','April','May','June','July','August','September','October','November','December']
    dicm = {}

    for i in range(0,len(name)):
        try:
            dicm[name[i]] = ncin.variables[name[i]][:]
        except:
            break
    lat = ncin.variables['lat'][:]
    lon = ncin.variables['lon'][:]
    return dicm, [lat,lon]

def insertTomongo(data,col,detail,aryLatLon,yearInit):
    name = ['Ann','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    nt, nlat, nlon = data['Ann'].shape
    a = MongoDB_lc()
    a.collection(col)
    # yearInit = yearInit
    for year in range(0, nt):
        dataAry = []
        for month in name:
            # pdAry = pd.DataFrame(data[month][year]).fillna(-99)
            # dataAry.append(pdAry.values.tolist())
            try:
                dataAry.append(data[month][year].tolist())
            except:
                break

        npAry = np.array(dataAry)
        post = {
            "year" : yearInit+year,
            "data" : dataAry
        }
        a.mongo_insert(post)     
        print(str(yearInit+year))
    
    maskAry = data['Ann'][0].mask
    maskAry = maskAry.tolist()
    post = {
            "detail" : detail,
            "lat" : aryLatLon[0].tolist(),
            "lon" : aryLatLon[1].tolist(),
            "key__" : f"{detail['dataset']}_{detail['index_name']}",
            "mask" : maskAry
        }
    a.mongo_insert(post)  
    

    
# location = "../dataset/ghcndex_current/GHCND_TXn_1951-2018_RegularGrid_global_2.5x2.5deg_LSmask.nc"
# data = get_data(location)
# detail = {
#     "index_name": 0, # TXx
#     "short_name": None, # Max Tmax
#     "type_measure": None, # temperature
#     "method": None, # intensity
#     "unit": None, # °C def
#     "dataset": 0, # ghcendex
# }
# insertTomongo(data,'ghcndex_TXn', 'ghcndex', 1951)

# multi_insert file
# basepath = "../dataset/ghcndex_current/"
# # basepath = "../dataset/hadex2_current/"
# files = os.listdir(basepath)
# index = 0
# month = ['Ann','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


    
# # for i in files:
# #     name = i.split(".")
# #     collect = name[0].split("_")[1]
# #     print(collect)
# #     dataset = 'ghcndex'
# #     data, aryLatLon = get_data(f"{basepath}{i}")
# #     detail = {
# #         "index_name": collect, # TXx
# #         "short_name": None, # Max Tmax
# #         "type_measure": None, # temperature
# #         "method": None, # intensity
# #         "unit": None, # °C def
# #         "dataset": dataset, # ghcendex
# #     }
# #     insertTomongo(data,f'ghcndex_{collect}', detail, aryLatLon, 1951)
# #     index+=1

# # print(index)

# array = []
# for i in files:
#     name = i.split(".")
#     collect = name[0].split("_")[1]
#     array.append(collect)

# print(array)