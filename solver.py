"""
Input transfer format (All is Python3 dict):

        milleniumFalcon:
            {'autonomy': 6, 'departure': 'Tatooine', 'arrival': 'Endor', 'routes_db': 'universe.db'}

        graph:
            {'Tatooine': {'Dagobah': 6, 'Hoth': 6}, 'Dagobah': {'Endor': 4, 'Hoth': 1}, 'Hoth': {'Endor': 1}}

        empire:
            {'countdown': 8, 'bounty_hunters':
                [{'planet': 'Hoth', 'day': 6},
                {'planet': 'Hoth', 'day': 7},
                {'planet': 'Hoth', 'day': 8}]}

"""

import copy
from helper_classes import Universe, Path

optimalPath = None  # Best path available
optimalBounty = +float("inf")  # Proba to be captured
n_explored_path = 0

def odds(millenium_falcon, routes, empire):

    global optimalPath
    global optimalBounty
    global n_explored_path

    optimalPath = None
    optimalBounty = +float("inf")
    n_explored_path = 0

    startNode = millenium_falcon['departure']
    targetNode = millenium_falcon['arrival']

    autonomy = millenium_falcon['autonomy']
    countdown = empire['countdown']

    # Build a fast access dict to the bounty presence given location and day
    bountyPresence = {}
    for intel in empire["bounty_hunters"]:
        bountyPresence[(intel['planet'], intel['day'])] = 1

    U = Universe(routes, bountyPresence)

    optimalPath = None  # Best path available
    optimalBounty = +float("inf")  # Proba to be captured
    n_explored_path = 0

    # Initial base case should be dag_explorer(Path(StartNode))
    def dag_explorer(path):

        global optimalPath
        global optimalBounty
        global n_explored_path

        # Pruning
        if path.is_out_of_fuel() or path.is_out_of_time() or path.n_days_bounty > optimalBounty:
            n_explored_path += 1
            del path
            return None

        # Checking Optimality Condition
        if path.has_reached_destination() and path.n_days_bounty < optimalBounty:
            optimalPath = copy.deepcopy(path)
            optimalBounty = path.n_days_bounty
            n_explored_path += 1
            del path
            return None

        ###
        # Continue recursive exploration
        ###

        # Option 1: Travel from the planet
        available_destinations = path.get_destinations()
        for destination in available_destinations:
            new_path = copy.deepcopy(path)
            new_path.go_to(destination)
            dag_explorer(new_path)

        # Option 2: Stay on the planet
        path.wait()
        dag_explorer(path)

    travel = Path(autonomy, countdown, startNode, targetNode, U)
    dag_explorer(travel)
    safe_galaxy_proba = compute_safe_galaxy_proba(optimalPath, optimalBounty)

    print('Optimal path across the galaxy:{}'.format(optimalPath))
    print('Number of bounties encrossed: {}'.format(optimalBounty))
    print('Number of explored paths: {}'.format(n_explored_path))
    print('Proba of saving the galaxy: {}'.format(safe_galaxy_proba))

    return safe_galaxy_proba


def compute_safe_galaxy_proba(path, n_bountys):
    if not path:
        return 0
    if n_bountys == 0:
        return 1
    p = 0
    for i in range(n_bountys):
        p += (9**i)/(10**(i+1))
    return 1- p