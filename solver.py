"""


"""

import copy
from helper_classes import Universe, Path

# Global update variable for optimal search
optimalPath = None  # Best path available
optimalBounty = +float("inf")  # Proba to be captured
n_explored_path = 0
stop_exploration = False


def graph_explorer(path):
    """
    Recurvise exploration of the graph with pruning and stopping conditions
    :param path: <Path> Initial and current paths
    :return: None (Update of the best path variable)
    """

    global optimalPath
    global optimalBounty
    global n_explored_path
    global stop_exploration

    # Stopping exploration if an optimal found is found
    if stop_exploration:
        del path
        return None

    # Pruning
    if path.is_out_of_fuel() or path.is_out_of_time() or path.n_days_bounty > optimalBounty:
        n_explored_path += 1
        del path
        return None

    # Checking optimality condition
    if path.has_reached_destination() and path.n_days_bounty < optimalBounty:
        optimalPath = copy.deepcopy(path)
        optimalBounty = path.n_days_bounty
        n_explored_path += 1
        if path.n_days_bounty == 0:
            stop_exploration = True
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
        graph_explorer(new_path)

    # Option 2: Stay on the planet
    path.wait()
    graph_explorer(path)


def odds(millenium_falcon, routes, empire):
    """
    Main function for the computation of the optimal path.

    :param millenium_falcon: <dic> The millenium falcon from json to dict
            example: {'autonomy': 6, 'departure': 'Tatooine', 'arrival': 'Endor', 'routes_db': 'universe.db'}

    :param routes: <dict>
            example: {
                        'Tatooine': {'Dagobah': 6, 'Hoth': 6},
                        'Dagobah': {'Endor': 4, 'Hoth': 1},
                        'Hoth': {'Endor': 1}
                    }

    :param empire: <dic>
            example: {'countdown': 8, 'bounty_hunters':
                        [
                        {'planet': 'Hoth', 'day': 6},
                        {'planet': 'Hoth', 'day': 7},
                        {'planet': 'Hoth', 'day': 8}
                        ]
                     }

    :return:
        :optimalPath:
        :optimalBounty:
        :n_explored_path:
        :safe_galaxy_proba:
    """

    global optimalPath
    global optimalBounty
    global n_explored_path
    global stop_exploration

    optimalPath = None
    optimalBounty = +float("inf")
    n_explored_path = 0
    stop_exploration = False

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

    # Initial base case should be gaph_explorer(Path(StartNode))
    travel = Path(autonomy, countdown, startNode, targetNode, U)
    graph_explorer(travel)
    safe_galaxy_proba = compute_safe_galaxy_proba(optimalPath, optimalBounty)

    return optimalPath, n_explored_path, safe_galaxy_proba


def compute_safe_galaxy_proba(path, n_bountys):

    if not path:
        return 0
    if n_bountys == 0:
        return 1
    p = 0
    for i in range(n_bountys):
        p += (9**i)/(10**(i+1))
    return 1- p