import numpy as np
import sys
import gym_foo.envs.foo_env as envFoo
import dynamics.demand_models.demandModels as modelG
from dynamics.fooTools import roadSegments
import pickle
from sklearn.neighbors import KernelDensity
import itertools
import matplotlib.pyplot as plt
import scipy.spatial.distance as dist
from datetime import timedelta, datetime, time

# try:
#     from mpl_

# Agent's side bing account
BING_MAP_KEY = ' Ar3CJK6UhlfiInoTaLwsZwwjezd6okCCDWUbaEXS76Ru5CkXN2hbJWqg5vsNXncG'


# ------------------------ Utilities -------------------------------------

# travel duration btw 2 locations
def apicall(loc1, loc2):
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

# TODO Check all the units !!
def nearest_neighbor(curLocation, locations):
    """

    Return \mu(x_k) nearest neighbor of curLocation wrp to the locations

    :param curLocation, array (1, 2): lat and long of the reference point
        locations, array (n, 2): other locations among which we want to find the nearest neighbor
    :return: int, index of the nearest neighbor, indicating its position in locations
    """

    # Distance between curLocation and all the locations
    # print("size of locat", locations.shape)
    # print("size of curlocat", curLocation.shape)
    distance = dist.cdist(locations, curLocation)

    # index of the minimun => nearest neighbor
    nearest = np.argmin(distance)

    return nearest


def path_maker(curLocation, locations):
    """
    Gives the sequence of location to visit according to the nearest neighbor policy

    :param curLocation: np array(1,2), departure point
    :param locations: np array (n,2), points to visit
    :param store locations
    :return: list of successive coordinates, giving the places to visit (in this order)
    """
    '''Recursion tentative
    # sequence of location to visit
    if locations.shape == (1, 2):
        print(locations)
        coord.append(locations)
        return locations
    else:

        next_loc = recursive_path_maker(
                np.reshape(locations[nearest_neighbor(curLocation=curLocation,
                                                      locations=locations), :], (1, 2)),
                np.delete(locations, nearest_neighbor(curLocation=curLocation,
                                                      locations=locations), 0),
                coord)

        # print(next_loc)
        return next_loc
    '''
    coord = []  # store the sequence of locations

    while locations.shape != (1, 2):
        idx = nearest_neighbor(curLocation, locations)
        coord.append(list(locations[idx, :]))

        # Update
        curLocation = np.reshape(locations[idx, :], (1,2))
        locations = np.delete(locations, idx, 0)

    return coord

def successive_distance(coords):
    """
    Return distances btw successive coords
    :param coords: list of coordinates (output of path_maker
    :return: list of floats
    """

    return [dist.cityblock(coords[i], coords[i+1]) for i in range(len(coords)-1)]

# TODO manage the case when the time of the file is lower than the current time
def mean_pi(distance, time):
    """
    Return mean and std of the normal distribution of the travel time at time t, for a specific distance

    :param distance: float in KM !!
    :param time: str, ex '1205' => 12h05
    :return: mean and std
    """

    # Stats retrieval
    if sys.platform == 'linux':
        statPath = "//home/louis/Documents/Research/Code/foo-Environment_2/dynamics/travelling time/" \
                   "traveltime_stats.txt"
    elif sys.platform == 'darwin':
        statPath = "/Users/Louis/PycharmProjects/MEng_Research/foo-Environment_2/dynamics/travelling time/" \
                   "traveltime_stats.txt"

    stats = np.loadtxt(statPath, skiprows=2)

    # print('shape of the stats array ', stats.shape)

    # Corresponding travel time file
    cur_time = str(int(np.floor(int(time)/100)))+':'+str(int(time[-2:]))
    time_file = str(int(np.floor(stats[0, 1]/100))) + ':' + str(int(str(int(stats[0, 1]))[-2:]))
    FMT = '%H:%M'
    if datetime.strptime(time_file, FMT) > datetime.strptime(cur_time, FMT):
        delta_file = datetime.strptime(time_file, FMT) - datetime.strptime(cur_time, FMT)
    else:
        delta_file =  datetime.strptime(cur_time, FMT) - datetime.strptime(time_file, FMT)

    for closest in range(1, stats[:, 1].shape[0]):

        time_file = str(int(np.floor(stats[closest, 1] / 100))) + ':' + str(int(str(int(stats[closest, 1]))[-2:]))

        if (datetime.strptime(time_file, FMT) - datetime.strptime(cur_time, FMT)) < delta_file:
            if datetime.strptime(time_file, FMT) > datetime.strptime(cur_time, FMT):
                delta_file = datetime.strptime(time_file, FMT) - datetime.strptime(cur_time, FMT)
            else:
                delta_file = datetime.strptime(cur_time, FMT) - datetime.strptime(time_file, FMT)

            closest_file = closest

    #print("selected file ", stats[closest_file, 1])
    #print(self.curState.time)

    # Retrieve model
    a = stats[closest_file, 4]
    b = stats[closest_file, 3]
    c = stats[closest_file, 2]

    t = stats[closest_file, 5]
    s_err = stats[closest_file, 6]
    n_trip = stats[closest_file, 7]
    mean = stats[closest_file, 8]
    errMeanSq = stats[closest_file, 9]

    # Compute mean and std (for the given )
    mean_dist = a * float(np.power(distance, 2)) + b * distance + c
    PI = t * s_err * np.sqrt(1 + 1 / n_trip + (distance - mean) ** 2 / errMeanSq)
    return mean_dist, PI



# ------------------------------------------------------------------------
# STATE Class
# ------------------------------------------------------------------------
# TODO transform every time object into a datetime or time object !
class state():

    def __init__(self, foo_env):

        # Current location
        self.loc = np.reshape(foo_env.currentCoords, (1, 2))  # coords
        # self.locID = foo_env.curLocID ??

        # Current time
        self.time = foo_env.time

        # Remaining customers
        rem_customers = foo_env.tasks[:, -2:]  # coords of all customers (serviced or not)
        visited_cust = foo_env.visited_customer  # list
        self.remCustomers = np.asarray([rem_customers[row, :] for row in range(len(visited_cust))
                                        if visited_cust[row] == 0])

        # Other info
        # Repartition deliveries/pickups
        self.n_d = foo_env.remDeliv
        self.n_p = np.size(rem_customers, axis=0) - foo_env.ndl
        self.nbCust = self.n_d + self.n_p  # current nb of customers

        # Max number of tasks (n_p + n_d < N) => hence there is self.N - self.nbCust locations to sample
        self.N = foo_env.ndl + foo_env._npl
        print("Nb of artificial pickups to generate ", self.N - self.nbCust)

        # Zone
        coords = foo_env.deliverydata[:, -2:]
        self.zone = [np.amax(coords[:, 0]), np.amin(coords[:, 0]), np.amax(coords[:, 1]), np.amin(coords[:, 1])]
        print("type of zone ", self.zone)
        # Date of operation
        self.date = foo_env.deliverydata[0, 0]
        self.day = int(foo_env.deliverydata[0, 1])
        self.starttime = foo_env.startTime

        # Test
        if self.n_p + self.n_d == self.remCustomers.shape[0]:
            print("Number of pickups compatible")
        else:
            print("Number of pickups NOT compatible")

    def update(self, foo_env):
        """
        Update the state given the last observation given in foo_env object

        :param foo_env: foo_env object
        :return: nothing, update the state object
        """
        # Current location
        self.loc = foo_env.currentCoords  # coords
        # self.locID = foo_env.curLocID ??

        # Current time
        self.time = foo_env.time

        # Remaining customers (coords as a np array (:, 2)
        rem_customers = foo_env.tasks[:, -2:]  # coords of all customers (serviced or not)
        visited_cust = foo_env.visited_customer  # list
        self.remCustomers = np.asarray([rem_customers[row, :] for row in range(len(visited_cust))
                                        if visited_cust[row] == 0])

        # Other info
        # Repartition deliveries/pickups
        self.n_d = foo_env.remDeliv
        self.n_p = np.size(rem_customers, axis=0) - foo_env.ndl
        self.nbCust = self.n_d + self.n_p  # current nb of customers

        # Max number of tasks (n_p + n_d < N) => hence there is self.N - self.nbCust locations to sample
        self.N = foo_env.ndl + foo_env._npl

        # Zone
        coords = foo_env.deliverydata[:, -2:]
        self.zone = [np.amax(coords[:, 0]), np.amin(coords[:, 0]), np.amax(coords[:, 1]), np.amin(coords[:, 1])]

        # Date of operation
        self.date = foo_env.deliverydata[0, 0]
        self.day = int(foo_env.deliverydata[0, 1])

        # Test
        if self.n_p + self.n_d == self.remCustomers.shape[0]:
            print("Number of pickups compatible")
        else:
            print("Number of pickups NOT compatible")





# ------------------------------------------------------------------------
# PICKUP Class
# ------------------------------------------------------------------------
class pickup():

    def __init__(self, state, t_range, bandwidth=100):
        """

        :param data_path: path to the fedex data
        :param state: current state of operation
        """
        self.state = state

        data = np.loadtxt(modelG.fedex_data_path + "fedex.data")
        mask = (data[:, 0] != state.date) & (data[:, 7] != 0)
        data = data[mask]

        self.kdeZone = modelG.modelGenerator_fedex_data(data, state.day, state.starttime, t_range,
                                                        state.zone, bandwidth=bandwidth)

    # --------------------------------- Sampling ------------------------------------------------

    def sample_pickups(self, seed = 0):
        """
        Return artificial new pickups coordinates
        :return: array (self.curState.N - self.curState.nbCust , 2)
        """
        return self.kdeZone.sample(self.state.N - self.state.nbCust, random_state=seed)

# ------------------------------------------------------------------------
# AGENT Class
# ------------------------------------------------------------------------

class agent1():

    def __init__(self, state, t_range=12*60, bandwidth=100):
        """
        Require to retrieve the state of the environment
        dayOfOp is the integer defining which day of the week the agent is operating
        bandwdt is the param controlling the smoothing when generating KDE model
        """
        self.bandwidth = bandwidth
        self.t_range = t_range
        # Current state (not mandatory)
        self.curState = state

        # Model the pickups
        self.pickup_model = pickup(self.curState, self.t_range, self.bandwidth)

        # Nb of simulation for MC
        self.MC = 10

        # KDE model to sample new models
        # mask = (self.data[:, 0] != self.date) & (self.data[:, 7] != 0)
        # self.data_oth = self.data[mask]  # demand data from other day of operations (for test purpose)
        # self.kdeZone = modelG.modelGenerator_fedex_data(self.data_oth, self.day, self.starttime, self.t_range,
        # self.zone, bandwidth=bandwdth)

    def dispDemand(self, grid_size=10):
        """
        Display the prob distribution retrieved

        :param grid_size: resolution of the map
        :return:
        """

        mask = (self.data_oth[:, 1] == self.day) & (self.data_oth[:, 7] > self.starttime) \
               & (self.data_oth[:, 7] < self.starttime + self.t_range) \
               & (self.data_oth[:, 13] < self.zone[0]) \
               & (self.data_oth[:, 13] > self.zone[1]) \
               & (self.data_oth[:, 14] < self.zone[2]) \
               & (self.data_oth[:, 14] > self.zone[3])

        data_op = self.data_oth[mask]  # new demand data from the day of operation
        print("Shape of the previous demand data ", data_op.shape)
        # print(self.data.shape)
        # grid on which to evaluate prob distrib
        nX, nY = (grid_size, grid_size)
        x = np.linspace(np.min(data_op[:, 13]), np.max(data_op[:, 13]), nX)
        y = np.linspace(np.min(data_op[:, 14]), np.max(data_op[:, 14]), nY)

        X, Y = np.meshgrid(x, y)
        coord_comb = np.vstack([X.ravel(), Y.ravel()]).T
        # coord_comb *= np.pi / 180
        # print(coord_comb)

        proba = np.exp(self.kdeZone.score_samples(coord_comb))
        proba = proba.reshape(X.shape)

        # print(proba[0, 1])
        # levels = np.linspace(0, proba)
        plt.figure()
        # levels = np.linspace(0, coord_comb.max(), 25)
        plt.contourf(X, Y, proba, cmap=plt.cm.Reds)  # ,levels=levels
        plt.colorbar()

        plt.scatter(data_op[:, 13], data_op[:, 14])
        plt.show()


    def cost_to_go_mc(self):
        """
        Return an approximation of the cost to go function from the current state,
        using Monte-Carlo method with the nearest neighbor base policy

        :param

        :return: float
        """

        # Virtually move to ONE of the next possible location
        # and retrieve the associated cost
        next_cust = self.curState.remCustomers[1]  # Coordinates
        immediate_dist = successive_distance([self.curState.loc, next_cust])
        immediate_cost = mean_pi(immediate_dist[0], self.curState.time)

        print("Cost to go to the next ", immediate_cost[0])
        # For many scenarios (change the seed each time)
        for i in range(100):
            ## Sample pickups

            new_pickups = self.pickup_model.sample_pickups(seed=i)
            locations = np.vstack((self.curState.remCustomers, new_pickups))
            # print("size ", locations.shape)
            ## Nearest neighbour policy
            path = path_maker(self.curState.loc, locations)
            # plt.plot([path[i][0] for i in range(len(path))], [path[i][1] for i in range(len(path))])
            # plt.scatter([path[i][0] for i in range(len(path))], [path[i][1] for i in range(len(path))])
            plt.show()
            dist_path = successive_distance(path)

            ## Accumualted cost
            # TODO the second argument of mean_pi so that time is updated at each step.
            costs = [mean_pi(d, self.curState.time)[0] for d in dist_path]
            # print(sum(costs))

        # Average over all the scenarios

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





