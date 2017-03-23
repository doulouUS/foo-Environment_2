import numpy as np
from gym_foo.envs.foo_env import timeupdate

def agent_0_fedex(instance):
    # a: index of the place to visit (action) in the FedEx order !
    a = 1
    while not instance.done:

        # adapt the FedEx actions to the tasks order
        a_new = np.argwhere(instance.tasks[:, 4] == instance.deliverydata[a, 4])

        try:  # case with 2 similar addresses
            a_new =  int(a_new[0]) if instance.visited_customer[int(a_new[0])] == 0 else int(a_new[1])

        except:  # case where there is no task anymore => wait 5 mn
            instance.time = timeupdate(instance.time, 5)

        print("action ", a)
        s, reward, done, info = instance.step(a_new)
        if info == 'Lunch break':

            # replay this same action !
            instance.render()
            instance.step(a_new)
        a += 1
        # break
        instance.render()
        print("Total number of known tasks ", instance.tasks[:, 3].size)

        print('_' * 50)
        print('_' * 50)
        print('_' * 50)