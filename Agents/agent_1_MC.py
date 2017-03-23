import numpy as np
import gym_foo.envs.foo_env as envFoo
import dynamics.demand_models.demandModels as modelG
from dynamics.fooTools import roadSegments
import pickle
from sklearn.neighbors import KernelDensity
import itertools
import matplotlib.pyplot as plt
# try:
#     from mpl_

# Agent's side bing account
BING_MAP_KEY = ' Ar3CJK6UhlfiInoTaLwsZwwjezd6okCCDWUbaEXS76Ru5CkXN2hbJWqg5vsNXncG'

# TODO ---------------------------------- CREATE A CLASS FOR THE AGENT -----------------------------------------


def agent_1_MC(env, nb_sim=100):
    """
    Return the next place to go based on the current state of the environment env
    :param env: FooEnv class instance
            coord_boundaries: list, [max_long, min_long, max_lat, min_lat]
    :return: integer, index of the next location to visit corresponding to a row of env.tasks
    """
    # # ------------------- DEMAND ------------------------------------
    # # Call fedex.data for KDE only
    # path = modelG.fedex_data_path + "fedex.data"
    # data = np.loadtxt(path)
    # # print("de", data[0,0])
    #
    # mask = data[:, 0] != 2122015  # remove data corresponding to the scenario replayer
    # data = data[mask]
    #
    # # To be removed, for COMPLETION only
    # # env = envFoo.FooEnv(data)
    # # kernel density estimation test: ok !
    #
    # # Construction of the demand model
    # kde = modelG.modelGenerator_fedex_data(data, env.deliverydata[0, 1], int(env.time), 7 * 60, env.coord_boundaries)  #  [105, 100, 2, 0])  # whole SG



    # Algorithm main steps. Output: decision of where to go next
    # Examine all possible next locations (including of the new sampled demand), not visited yet
    mask = np.asarray(env.visited_customer) < 1
    for next_loc in env.tasks[mask]:

        # 1. reward (traveling time obtained through API
        # when we will implement in Real situation
        # reward = rewardForecast(env.currentLocation, next_loc)

        # For now, using the replayer ONLY at the current time

        first_loc = int(np.where(env.deliverydata[:, 4] == env.currentLocation)[0])  # index based on env.deliverydata
        # print(np.where(env.deliverydata[:, 4] == next_loc[4])[0])
        try:
            second_loc = int(np.where(env.deliverydata[:, 4] == next_loc[4])[0])
        except:  # most common problem: 2 same addresses so int() cannot work
            second_loc = int(np.where(env.deliverydata[:, 4] == next_loc[4])[0][0])

        print(second_loc, first_loc)

        if first_loc < second_loc:  # reading our triangular matrix as a list of lists
            reward = env.durations[first_loc][abs(first_loc - second_loc) - 1]
        else:
            reward = env.durations[second_loc][abs(first_loc - second_loc) - 1]

        # 2. cost-to-go function: Monte Carlo, generation of multiple scenarios
        for nb_scen in range(nb_sim):
            # Tasks remaining to be done (ie tasks minus all the visited til now + next_loc)
            # print("truc ", np.where(np.all(env.tasks[mask] == next_loc, axis=1)))
            further_tasks = np.delete(env.tasks[mask],  int(np.where(np.all(env.tasks[mask] == next_loc,axis=1))[0]) , 0)
            # (i) Generate path
            # a. Sample demand using KDE # TODO add demand once for all, or through time? For now, once for all...
            new_demand = kde.sample(2)  # TODO how many new demand occur per period ? Cannot be a constant. For now, constant !
            # update the tasks
            new_tasks = np.hstack((np.zeros((new_demand.shape[0], 13)), new_demand))  # TODO chec that it works !
            tasks = np.vstack((further_tasks, new_tasks))



            # b. heuristic to build the path to service all the locations: nearest neighbor
            path = pathmaker(env, tasks)

            # c. Sample traveling times for each segments of the path built in a.
            # see Samuel's work

            # d. Compute the average total servicing time til the end



    # Take the min of all the values computed in e. of the previous loop


def rewardForecast(loc1, loc2):
    """
    Gives the reward from going to loc1 to loc2. For now, traveling time given by API
    :param: loc1 and loc2, np arrays (1,~14) entries of env.tasks
    :return: integer, reward (typically traveling time in seconds)
    """
    # Retrieve Addresses
    add1 = int(loc1[:,4])  # ID
    add2 = int(loc2[:,4])

    with open("/home/louis/Documents/Research/Code/foo-Environment_2/gym_foo/envs/addresses.fedex", "rb") as ad:
         addresses = pickle.load(ad)

    add1 = addresses[add1]  # string
    add2 = addresses[add2]

    # API call using our second bing account
    statusCode, travelDistance, travelDuration, travelDurationTraffic, numberSegments, roadName, \
    travelDistances, travelDurations, maneuverType, pathCoord = roadSegments([add1, add2], API_key=BING_MAP_KEY)

    return travelDuration

def travelTimesModel():
    """

    :return:
    """

# TODO Implement, use env.visited_customer !
def pathmaker(env, tasks):
    """
    Return a sequence of places to visit next using a heuristic. Now the nearest neighbor using the manhattan distance

    :param: tasks np array (nbTasks, 14), nb of features is 14 like fedex.data
        env, FooEnv object. Just to use env.visited_customer !
    :return: list of integers, indexes of tasks
        ex: [0, 1, 3, 2] means doing successively tasks[0] tasks[1] tasks[3] and finally tasks[2]
    """
    coord = tasks[:, 13:14]


def traveltimeprob(stat_file, time, dist):
    """

    :param stat_file:
    :param time:
    :param dist:
    :return:
    """


if __name__ == '__main__':
    # ------------------- DEMAND ------------------------------------
    # Call fedex.data for KDE only
    path = modelG.fedex_data_path + "fedex.data"
    data = np.loadtxt(path)

    print(data.shape)
    # kernel density estimation test: ok !

    # Construction of the demand model
    kde = modelG.modelGenerator_fedex_data(data, 2, 800, 12 * 60,
                                           [105, 100, 2, 0], bandwidth=75)  # whole SG

    day = 2
    startTime = 800
    timeSpan = 12*60
    coord_boundaries = [104, 102, 2, 1]

    mask = mask = (data[:, 1] == day) & (data[:, 7] > startTime) & (data[:, 7] < startTime + timeSpan ) \
           & (data[:, 13] < coord_boundaries[0]) & (data[:, 13] > coord_boundaries[1]) & (data[:, 14] < coord_boundaries[2])\
           & (data[:, 14] > coord_boundaries[3])

    data = data[mask]
    print(data.shape)
    # grid on which to evaluate prob distrib
    nX, nY = (100, 100)
    x = np.linspace(np.min(data[:, 13]), np.max(data[:, 13]), nX)
    y = np.linspace(np.min(data[:, 14]), np.max(data[:, 14]), nY)

    print()
    X, Y = np.meshgrid(x, y)
    coord_comb = np.vstack([ X.ravel(), Y.ravel()]).T
    # coord_comb *= np.pi / 180
    print(coord_comb)

    # sample = np.asarray([103.636, 1.31814])
    # sample *= np.pi / 180
    # sample = sample.reshape(1,-1)
    # print("hwat !", np.exp(kde.score_samples(sample)))

    proba = np.exp(kde.score_samples(coord_comb))

    proba = proba.reshape(X.shape)
    print(proba[0,1])
    # levels = np.linspace(0, proba)
    plt.figure()
    # levels = np.linspace(0, coord_comb.max(), 25)
    plt.contourf(X,Y, proba, cmap=plt.cm.Reds) # ,levels=levels
    plt.colorbar()

plt.show()







