from flask_cors import CORS
from app import app
from flask import Flask, jsonify, request
import numpy as np
from .lib.mongoDB import MongoDB_lc
import json
import pandas as pd
from .lib.linearRegressGen import Linear_regression

app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/api/*": {"origins": ["*"]}})


def year_ary(init,end):
    init = init.split("-")
    yearinit = int(init[0])
    end = end.split("-")
    yearend = int(end[0])
    countYear = yearend-yearinit+1
    year = []
    for i in range(0,countYear):
        year.append(yearinit+i)

    return year, [int(init[1]),int(end[1])]

def getDetail(collection):
    objDB= MongoDB_lc()
    objDB.collection(collection)
    return objDB.mongo_findDetail(collection)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/api/getgeocountry')
def getGeojson():
    with open('./app/dataset/geojson/countries.json') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/getmap/mapAVG/<type_dataset>/<yearInit>/<yearEnd>/<type_index>/')
def getmapAverage(type_dataset, yearInit, yearEnd, type_index):
    from .lib.average import Average_service
    print(f"getmapAverage : {type_dataset, yearInit, yearEnd, type_index}")
    ary, month_IE = year_ary(yearInit, yearEnd)
    collection = f"{type_dataset}_{type_index}"

    obj = Average_service(ary, collection, month_IE[0], month_IE[1])
    dataM = obj.getAverageMap(0) # Ann = 0 Jan = 1 ..... Dec = 12
    print("----------------------------------------------------",dataM)
    # df = pd.DataFrame(dataM)
    # df.fillna(-99.99, inplace=True)
    
    # print(np.count_nonzero(~np.isnan(dataM)))
    dataM[np.isnan(dataM)] = -99.99
    # print(dataM.shape)
    # count = 0
    # for i in range(0,len(dataM)):
    #     for j in range(0, len(dataM[i])):
    #         if(dataM[i][j] != -99.99):
    #             count += 1

    # print(count)

    deatail = getDetail(collection)
    return jsonify(
        {
            "detail": deatail,
            "map": { 
                "mapAVG": dataM.tolist()
            }
        }
    )

@app.route('/api/getData/Graph/<type_dataset>/<yearInit>/<yearEnd>/<type_index>/')
def getSeasonalandAVG(type_dataset, yearInit, yearEnd, type_index):
    from .lib.average import Average_service
    print(f"getSeasonalandAVG : {type_dataset, yearInit, yearEnd, type_index}")
    
    ary, month_IE = year_ary(yearInit, yearEnd)
    collection = f"{type_dataset}_{type_index}"

    # SERVICE GET Average Graph Ann
    a = Average_service(ary, collection, month_IE[0], month_IE[1])
    dataA, year  = a.getAverageGraph(0)
    
    # regAVG_ann = Linear_regression(dataA)
    # dataTrend_ann = regAVG_ann.predict_linear()
    
    # SERVICE GET Seasonal Graph
    b = Average_service(ary, collection, month_IE[0], month_IE[1])
    dataS = b.getSeasonal()
    
    # SERVICE GET Average Graph all
    c = Average_service(ary, collection, month_IE[0], month_IE[1])
    dataAll, yearAll  = c.getAverageGraph()

    # regAVG_all = Linear_regression(dataAll)
    # dataTrend_all = regAVG_all.predict_linear()

    deatail = getDetail(collection)
    month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # pop lat lon
    deatail.pop('lat_list', None)
    deatail.pop('lon_list', None)

    try:
        regAVG_all = Linear_regression(dataAll)
        dataTrend_all = regAVG_all.predict_linear()
    except:
        dataTrend_all = np.array([])

    regAVG_ann = Linear_regression(dataA)
    dataTrend_ann = regAVG_ann.predict_linear()


    return jsonify(
        {
            "detail": deatail,
            "graph":{
                "graphAVGAnn": {
                    "TaxisY": dataTrend_ann.tolist(),
                    "axisX":year,
                    "axisY":dataA.tolist()
                },
                "graphSeasonal": {
                    "axisX":month,
                    "axisY":dataS.tolist()
                },
                "graphAVG": {
                    "TaxisY": dataTrend_all.tolist(),
                    "axisX":yearAll,
                    "axisY":dataAll.tolist()
                },
            }
        }
    )

@app.route('/api/getmap/mapPCA/<type_dataset>/<yearInit>/<yearEnd>/<type_index>/')
def getmapPCA(type_dataset, yearInit, yearEnd, type_index):
    from .lib.pcaservice import Pca_service
    print(f"getmapAverage : {type_dataset, yearInit, yearEnd, type_index}")
    ary, month_IE = year_ary(yearInit, yearEnd)
    collection = f"{type_dataset}_{type_index}"

    pca_eofs = []
    # SERVICE GET PCA map and graph
    obj = Pca_service(ary, collection, month_IE[0], month_IE[1])
    comp = 6
    try:
        pca_pc, pca_eofs, pca_va_ratio =  obj.getPCA_service(comp)
        ratioX = np.linspace(1, comp, num=comp)
        date = obj.date
        print(pca_va_ratio.shape)
        print(ratioX)
    except:
        pca_pc, pca_va_ratio, ratioX = np.array([[],[],[]])
        date = []
    
    
    # dataM[np.isnan(dataM)] = -99.99

    deatail = getDetail(collection)
    return jsonify(
        {
            "detail": deatail,
            "graph":{
                "time":{
                    "axisX":date, # chnage
                    "axisY":pca_pc.tolist()
                },
                "ratio":{
                    "axisX":ratioX.tolist(),
                    "axisY":pca_va_ratio.tolist()
                }
            },
            "map": { 
                "mapPCA": pca_eofs
            }
        }
    )

@app.route('/api/getmap/mapTrend/<type_dataset>/<yearInit>/<yearEnd>/<type_index>/')
def getmapHypoTrend(type_dataset, yearInit, yearEnd, type_index):
    from .lib.hypotasisTest import Trend_service
    print(f"getmapAverage : {type_dataset, yearInit, yearEnd, type_index}")
    ary, month_IE = year_ary(yearInit, yearEnd)
    collection = f"{type_dataset}_{type_index}"

    # SERVICE GET Hypo and Trend
    import time
    obj = Trend_service(ary, collection, month_IE[0], month_IE[1])
    dataRaw = obj.getData(0)
    start = time.time()
    tempR, hypoLat = obj.trendAndHypo(dataRaw)
    print(time.time() - start)
    print(tempR.shape)
    print(hypoLat.shape)
    tempR[tempR == 0] = -99.99
    deatail = getDetail(collection)
    return jsonify(
        {
            "detail": deatail,
            "map": { 
                "mapTREND": tempR.tolist(),
                "hiypo": hypoLat.tolist() 
            }
        }
    )


@app.route('/api/getdata/selectGraph/', methods=['POST'])
def getSlectGraph():
    from .lib.selectservice import SelectCus_service
    if(request.method == 'POST'):
        data = request.data
        data = json.loads(data)
        type_dataset = data['type_dataset']
        yearInit = data['yearInit']
        yearEnd = data['yearEnd']
        type_index = data['type_index']
        custom = data['custom']
        print("////////////////////////////////////")
        # print(custom)
        print("////////////////////////////////////")
        print(f"getmapAverage : {type_dataset, yearInit, yearEnd, type_index}")

        ary, month_IE = year_ary(yearInit, yearEnd)
        collection = f"{type_dataset}_{type_index}"

        obj = SelectCus_service(ary, collection, month_IE[0], month_IE[1])
        dataAll, yearAll  = obj.getAverageGraphCus(custom)
        tempMedian = np.nanmedian(dataAll)
        dataAll[np.isnan(dataAll)] = tempMedian

        obj1 = SelectCus_service(ary, collection, month_IE[0], month_IE[1])
        dataA, year  = obj1.getAverageGraphCus(custom, 0)
        tempMedian = np.nanmedian(dataA)
        dataA[np.isnan(dataA)] = tempMedian

        print("AAAAAAAAAAAAA")
        obj2 = SelectCus_service(ary, collection, month_IE[0], month_IE[1])
        dataS  = obj2.getSeasonalCus(custom)
        tempMedian = np.nanmedian(dataS)
        dataS[np.isnan(dataS)] = tempMedian

        month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        deatail = getDetail(collection)
        # pop lat lon
        deatail.pop('lat_list', None)
        deatail.pop('lon_list', None)

        try:
            regAVG_all = Linear_regression(dataAll)
            dataTrend_all = regAVG_all.predict_linear()
        except:
            dataTrend_all = np.array([])

        regAVG_ann = Linear_regression(dataA)
        dataTrend_ann = regAVG_ann.predict_linear()

        return jsonify(
            # {"ssss":"ddddddddd"}
            {
                "detail": deatail,
                "graph":{
                    "graphAVGAnn": {
                        "TaxisY": dataTrend_ann.tolist(),
                        "axisX":year,
                        "axisY":dataA.tolist()
                    },
                    "graphSeasonal": {
                        "axisX":month,
                        "axisY":dataS.tolist()
                    },
                    "graphAVG": {
                        "TaxisY": dataTrend_all.tolist(),
                        "axisX":yearAll,
                        "axisY":dataAll.tolist()
                    },
                }
            }
        )
    else:
        return jsonify(
            {
                "status": "Error"
            }
        )
    
