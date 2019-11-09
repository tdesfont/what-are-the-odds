class Universe:

    def __init__(self, routes, bounty):
        self.routes = routes
        self.bounty = bounty

    def get_destinations(self, source):
        if source not in self.routes:
            return []
        destinations = []
        for dest in self.routes[source]:
            destinations.append(dest)
        return destinations

    def get_travel_time(self, source, target):
        return self.routes[source][target]

    def get_bounty_presence(self, loc, day):
        key = (loc, day)
        if key in self.bounty:
            return self.bounty[key]
        else:
            return 0

class Path:

    def __init__(self, autonomy, countdown, start, end, universe):
        self.path = [start]
        self.end = end
        self.day = 0

        self.autonomy = autonomy
        self.fuelCap = autonomy
        self.countdown = countdown

        self.universe = universe

        self.n_days_bounty = self.universe.get_bounty_presence(self.path[-1], self.day)


    def wait(self):
        assert len(self.path) > 0
        self.autonomy = self.fuelCap
        self.path += [self.path[-1]]
        self.day += 1
        self.n_days_bounty += self.universe.get_bounty_presence(self.path[-1], self.day)

    def go_to(self, destination):
        source = self.path[-1]
        travel_time = self.universe.get_travel_time(source, destination)
        self.autonomy -= travel_time
        self.day += travel_time
        self.path += [destination]
        self.n_days_bounty += self.universe.get_bounty_presence(self.path[-1], self.day)

    def get_destinations(self):
        return self.universe.get_destinations(self.path[-1])

    def is_out_of_fuel(self):
        return self.autonomy < 0

    def is_out_of_time(self):
        return self.day > self.countdown

    def has_reached_destination(self):
        return self.path[-1] == self.end

    def __str__(self):
        return "Path: {}, Bountys:{}, Autonomy:{}, Day:{}, Countdow:{}".format(
            self.path, self.n_days_bounty, self.autonomy, self.day, self.countdown)


