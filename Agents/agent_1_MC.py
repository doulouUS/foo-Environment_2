import numpy as np
import dynamics.demand_models.demandModels as modelG

if __name__ == '__main__':
    def agent_1_MC(env):


        # Call fedex.data
        path = modelG.fedex_data_path + "fedex.data"
        data = np.loadtxt(path)

        # kernel density estimation test: ok !
        kde = modelG.modelGenerator_fedex_data(data, 'tuesday', 1430, 30)
        print(kde.sample(3))


        # Algorithm main steps
        # while (env.done != True):


            # Examine all possible next locations
            # for all next loc nn

                # 1. reward(nn)

                # 2. cost-to-go function

                    # a. heuristic to build the path to service all the locations
                    # easiest one: nearest neighbor. Which distance ?

                    # b. Estimate traveling times for each segments of the path built in a.
                    # see Samuel's work

                    # c. Insert demand using KDE

                    # d. Monte-Carlo: compute the average total servicing time til the end

                    # e. Store the value

            # Take the min of all the values computed in e. of the previous loop
