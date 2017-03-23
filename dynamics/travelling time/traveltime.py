import numpy as np
import pickle
from dynamics.fooTools import roadSegments
import time
import os
import matplotlib.pyplot as plt
import schedule
import re
import numpy.polynomial.polynomial as poly
import scipy.stats as stats
# Stats
# from statsmodels.sandbox.regression.predstd import wls_prediction_std
# import statsmodels.api as sm




BING_MAP_KEY = ' Ar3CJK6UhlfiInoTaLwsZwwjezd6okCCDWUbaEXS76Ru5CkXN2hbJWqg5vsNXncG'

def traveltimeRand(idx, N=100):
    trips = []
    travelsDistance = []
    travelDurationTraffics = []

    for i in idx[0:200]:
        if deliverydata[i, 4] != deliverydata[i+1, 4]:
            trips.append([int(deliverydata[i, 4]), int(deliverydata[i+1, 4])])


    # 3 leaps
    for i in idx[31:200]:
        if deliverydata[i, 4] != deliverydata[i+3, 4]:
            trips.append([int(deliverydata[i, 4]), int(deliverydata[i+3, 4])])

    # 6 leaps
    for i in idx[61:100]:
        if deliverydata[i, 4] != deliverydata[i+6, 4]:
            trips.append([int(deliverydata[i, 4]), int(deliverydata[i+6, 4])])



    # Call the API => this will have to be done at relevant time of the day
    # distance between each couple

    # Transform ids into strings
    with open('/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/addresses.fedex', 'rb') as fp:
        addresses = pickle.load(fp)

    for trip in trips:
        add1 = addresses[trip[0]]
        add2 = addresses[trip[1]]
        try:
            statusCode,travelDistance,travelDuration,travelDurationTraffic,numberSegments,roadName, travelDistances,\
            travelDurations, maneuverType, pathCoord = roadSegments([add1+', Singapore',add2+' Singapore'], API_key=BING_MAP_KEY)

            if travelDistance != 0:

                # distance and travel time between each couple with traffic conditions
                travelsDistance.append(travelDistance)
                travelDurationTraffics.append(travelDurationTraffic)


        except:
            print("erreur mwhaaa")



    print('Trips successfully retrieved: ', len(travelsDistance))

    # Generate a binary file to store these two lists
    # name
    curpath = os.path.abspath(os.curdir)
    date = time.localtime()

    with open(curpath + '/travelTime_samuels_method/traveltime_' + str(date.tm_mon) + '-' + str(
            date.tm_mday) + '_' + time.strftime("%H%M"), 'wb') as fp:
        pickle.dump([travelsDistance, travelDurationTraffics], fp)



def datatomodel():


    # TODO CLEAN UP
    # READING
    abspath="//home/louis/Documents/Research/Code/foo-Environment_2/dynamics/travelling time/travelTime_samuels_method/"
    files = os.listdir(abspath)
    cmap = plt.get_cmap('jet')
    colors = cmap(np.linspace(0, 1, len(files)))

    # Storing coefficients, intervals and time
    coeff = []
    time = []
    # intervals = []

    # for file, color in zip(files, colors):
    file = "traveltime_3-14_1000"
    color = colors[0]
    with open(abspath + file,'rb') as ff:
        dist = pickle.load(ff)

    time.append(int(re.split("_", file)[-1]))  # eg 1008

    # STAT
    # poly regression. degree 2 ; y = coeff[0] + coeff[1]*x + coeff[2]*x^2
    n = len(dist[0])

    p, v = poly.polyfit(dist[0], dist[1], 2 ,full=True)
    m = p.size
    DF = n - m
    t = stats.t.ppf(0.95, n - m)  # used for CI and PI bands
    s_err = np.sqrt(v[0]/DF)

    coeff.append(list(p))
    # store each of these coeff, correspondingly to their time slot + Confidence Interval to compute your Standard Deviation next !

    # GENERATE MODEL and VIEWING along with the values
    x_new = np.linspace(min(dist[0]), max(dist[0]), 100)
    x = dist[0]

    # we want to compute the prediction intervals, that take into account the tendecy of y to fluctuate from its mean value
    # Prediction Interval
    # see http://stackoverflow.com/questions/27164114/show-confidence-limits-and-prediction-limits-in-scatter-plot
    PI = t * s_err * np.sqrt(1 + 1 / n + (x_new - np.mean(x)) ** 2 / np.sum((dist[0] - np.mean(x)) ** 2))

    # Confidence Interval
    CI = t * s_err * np.sqrt(1 / n + (x_new - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2))

    ffit = poly.polyval(x_new, coeff[-1])
    plt.plot(x_new, ffit, '--k', label="Polynomial fitting at "+re.split('_', file)[-1], color=color)
    plt.plot(x_new, ffit + PI, label="CI upper bound")
    plt.plot(x_new, ffit - PI, label="CI lower bound")

    plt.plot(dist[0], dist[1], 'yo')

    # Confidence intervals
    # ...
    # intervals.append(


    plt.legend(loc="best")
    plt.title("Models for Travel times vs Distance at different times of the day (based on 279 randomly chosen trips)")
    plt.show()


    # Storing coeff and confidence intervals
    # store = [time, coeff, intervals]
    # with open("traveltime_stats", "wb") as st:
    #    pickle.dump(store, st)

    # Retrieve probability p_ij(u)
    # mean from coeff

    # STD from confidence intervals

    # Proba from demands model (using KDE) => see kde.score_samples(x_new)

    return 0


if __name__ == "__main__":

    datapath = "/home/louis/Documents/Research/Code/foo-Environment_2/dynamics/demand_models/"
    deliverydata = np.loadtxt(datapath + "fedex.data")


    datatomodel()
    """
    # Select one day to avoid redundant trips
    mask = deliverydata[:, 0] == 3122015  # 2 dec 2015
    deliverydata = deliverydata[mask]



    # Select N trips i.e. N couple of addresses ID, following an equal repartition
    # 1 leap in the data
    idx = np.random.randint(0, deliverydata.shape[0]-6, size=500)

    def job():
        print("Working on...")
        # traveltimeRand(idx, 500)
        print("Distance and travel time retrieved" + time.strftime("%H%M"))

    schedule.every(30).minutes.do(job)

    while True:
        schedule.run_pending()
    """

# TODO do a linear regression of each file and store its components for future retrieval
# TODO implement a Standard Deviation technic (sort of windows evaluating the spread of points at a given distance