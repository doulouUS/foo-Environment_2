import numpy as np
import gym_foo.envs.foo_env as envFoo
import dynamics.demand_models.demandModels as modelG
from dynamics.fooTools import roadSegments
import pickle

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
    # ------------------- DEMAND ------------------------------------
    # Call fedex.data for KDE only
    path = modelG.fedex_data_path + "fedex.data"
    data = np.loadtxt(path)
    # print("de", data[0,0])

    mask = data[:, 0] != 2122015  # remove data corresponding to the scenario replayer
    data = data[mask]

    # To be removed, for COMPLETION only
    env = envFoo.FooEnv(data)
    # kernel density estimation test: ok !

    # Construction of the demand model
    kde = modelG.modelGenerator_fedex_data(data, env.deliverydata[0, 1], int(env.time), 30,
                                           env.coord_boundaries)  # [105, 100, 2, 0]) whole SG



    # Algorithm main steps. Output: decision of where to go next

    # Examine all possible next locations
    for next_loc in env.tasks:

        # 1. reward(nn) (traveling time obtained through API
        reward = rewardForecast(env.currentLocation, next_loc)

        # 2. cost-to-go function: Monte Carlo, generation of multiple scenarios
        for nb_scen in range(nb_sim):
            # Keep track of tasks
            tasks = env.tasks
            # (i) Generate path
            # a. Sample demand using KDE # TODO add demand once for all, or through time? For now, once for all...
            new_demand = kde.sample(2)  # TODO how many new demand occur per period ? Cannot be a constant
            # update the tasks
            new_tasks = np.hstack((np.zeros((new_demand.shape[0], 13)), new_demand))  # TODO chec that it works !
            tasks = np.vstack((tasks, new_tasks))

            # b. heuristic to build the path to service all the locations: nearest neighbor using
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

# TODO Implement, use env.visted_customer !
def pathmaker(env, tasks):
    """
    Return a sequence of places to visit next using a heuristic. Now the nearest neighbor one
    :param: tasks np array (nbTasks, 14), nb of features is 14 like fedex.data
        env, FooEnv object. Just to use env.visited_customer !
    :return: list of integers, indexes of tasks
        ex: [0, 1, 3, 2] means doing successively tasks[0] tasks[1] tasks[3] and finally tasks[2]
    """

if __name__ == '__main__':

    print("file executed")