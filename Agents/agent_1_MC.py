import numpy as np
import gym_foo.envs.foo_env as envFoo
import dynamics.demand_models.demandModels as modelG
from dynamics.fooTools import roadSegments
import pickle
from sklearn.neighbors import KernelDensity
import itertools
import matplotlib.pyplot as plt
import scipy.spatial.distance as dist
from datetime import timedelta, time

# try:
#     from mpl_

# Agent's side bing account
BING_MAP_KEY = ' Ar3CJK6UhlfiInoTaLwsZwwjezd6okCCDWUbaEXS76Ru5CkXN2hbJWqg5vsNXncG'

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


class agent1():

    def __init__(self, foo_env, bandwdth=100):
        """
        Require to create and initialize an instance of foo_env first
        dayOfOp is the integer defining which day of the week the agent is operating
        bandwdt is the param controlling the smoothing when generating KDE model
        """
        # Truck's zone [max long, min long, max lat, min lat]
        coords = foo_env.deliverydata[:, -2:]
        self.zone = [np.amax(coords[:, 0]), np.amin(coords[:, 0]), np.amax(coords[:, 1]), np.amin(coords[:, 1])]

        # time span to model demand (here 12h considered as whole day)
        self.t_range = 12*60
        self.starttime = int(foo_env.startTime)

        # Date of operation
        self.date = foo_env.deliverydata[0, 0]
        self.day = int(foo_env.deliverydata[0, 1])

        # State of the environment
        self.curLocID = foo_env.currentLocation  # ID
        self.curLocCoords = foo_env.currentCoords  # Coordinates (Longitude, Latitude) np.array

        self.curTime = foo_env.time
        self.demCoords = foo_env.tasks[:, -2:]

        self.N_loc = 30  # total fixed number of locations to visit

        if self.N_loc > len(foo_env.visited_customer):
            self.n_p = self.N_loc - len(foo_env.visited_customer)  # unknown locations to be sampled
        else:
            self.n_p = 0  # terminal state
            raise NameError("Initialized agent with a fully serviced environment")

        self.visitCust = foo_env.visited_customer.extend(self.n_p * [0])

        # ------------------- DEMAND ------------------------------------
        # Call fedex.data for KDE only
        self.path = modelG.fedex_data_path + "fedex.data"
        self.data = np.loadtxt(self.path)

        # KDE model to sample new models
        mask = (self.data[:, 0] != self.date) & (self.data[:, 7] != 0)
        self.data_oth = self.data[mask]  # demand data from other day of operations (for test purpose)
        self.kdeZone = modelG.modelGenerator_fedex_data(self.data_oth, self.day, self.starttime, self.t_range,
                                                        self.zone, bandwidth=bandwdth)

        # ------------------------------------------------------

    def

    def updateState(self, foo_env):
        """
            Update State of the environment, and return the state

        :return: tuple, curent coordinates,
        """
        self.curLocID = foo_env.currentLocation  # ID
        self.curLocCoords = foo_env.currentCoords


        self.curTime = foo_env.time
        self.demCoords = foo_env.tasks[:, -2:]

        if self.N_loc > len(foo_env.visited_customer):
            self.n_p = self.N_loc - len(foo_env.visited_customer)  # unknown locations to be sampled
        else:
            self.n_p = 0  # terminal state
            raise NameError("All jobs completed !")

        self.visitCust = foo_env.visited_customer + [0]*self.n_p

        return self.curLocCoords, self.curTime, np.vstack((self.demCoords, np.zeros((self.n_p, 2)))) , self.visitCust

    # --------------------------------- Sampling ------------------------------------------------

    def sample_demands(self, seed = 0):
        """
        Return self.n_p demand coordinates
        :return: array (self.n_p , 2)
        """
        return self.kdeZone.sample(self.n_p, random_state=seed)



    def mean_pi(self, distance):
        """
        Return mean and std of the normal distribution of the travel time at time t, for a specific distance

        :param distance: float in KM !!
        :param time: int, ex 1205 => 12h05
        :return: mean and std
        """

        # Stats retrieval

        stats = np.loadtxt("//home/louis/Documents/Research/Code/foo-Environment_2/dynamics/travelling time/"
                           "traveltime_stats.txt", skiprows=2)

        print('shape of the stats array ', stats.shape)

        # Corresponding travel time file

        cur_time = timedelta(hours=int(np.floor(int(self.curTime)/100)), minutes=int(self.curTime[-2:]))
        time_file = timedelta(hours=int(np.floor(stats[0, 1]/100)), minutes=int(str(int(stats[0, 1]))[-2:]) )
        delta_file = cur_time - time_file

        for closest in range(1, stats[1:, 1].shape[0]):

            time_file = timedelta(hours=np.floor(stats[closest, 1] / 100), minutes=int(str(int(stats[closest, 1]))[-2:]))
            if (cur_time - time_file) < delta_file:
                delta_file = timedelta(cur_time, time_file)
                closest_file = closest

        # Retrieve model
        a, b, c = stats[closest, 4], stats[closest, 3], stats[closest, 2]
        t = stats[closest, 5]
        s_err = stats[closest, 6]
        n_trip = stats[closest, 7]
        mean = stats[closest, 8]
        errMeanSq = stats[closest, 9]

        # Compute mean and std (for the given )
        mean_dist = a*np.power(distance, 2) + b*distance + c
        PI = t * s_err * np.sqrt(1 + 1 / n_trip + (distance - mean) ** 2 / errMeanSq)

        return mean_dist, PI




    def nearest_neighbor(self, sampled_demand):
        """
        To be used after updateState
        Return \mu(x_k) nearest neighbor among non-serviced locations including sampled demands
        as an index of self.demCoords if \mu(x_k) is part of demCoords (0)
        or as an index of sampled_demand otherwise (1)

        :param sampled_demand, array (self_np, 2)
        :return: tuple : coordinates (np.array), indx , among sapled_demand or not (0 or 1)
        """
        # Non serviced locations (including sampled_demand)
        mask = self.visitCust == 0
        nonServicedLoc = np.stack((self.demCoords[mask], sampled_demand))

        # Distance between self.current_location and all the non-serviced locations
        distance = dist.cdist(self.curLocCoords, nonServicedLoc)

        # index of the minimun => nearest neighbor
        nearest = np.argmin(distance)

        # identify the id of the nearest neighbor in self.demCoords or sampled_demand
        if nearest > self.demCoords[mask].shape[0]:  # nearest is among the sampled demands
            return  distance[nearest], self.demCoords.shape[0] + (nearest - self.demCoords[mask].shape[0]), 1
        else:
            return distance[nearest], np.where(np.all(self.demCoords == distance[nearest], axis=1)), 0


    def pathmaker(self):

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


def cost_to_go_mc(agent, zone, n_sim = 100, t_range=12):
    """
    Return an approximation of the cost to go function from the input state,
    using Monte-Carlo method with the nearest neighbor base policy

    :param  agent , current state
            n_sim int, number of scenario generated
            zone list, coord boundaries
            t_range int, hours defining time span

    :return: float
    """
    # Initialization

    # For loop/scenario
    for i in range(n_sim):
        # traveling time of scenario i
        h = 0

        # Sample new customers
        new_demand_coord = agent.sample_demands()  # np array (n_p, 20 containing coordinates

        # Path generation
        ## nearest neighbors

        ## travel time of each step

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





