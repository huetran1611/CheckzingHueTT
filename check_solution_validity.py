import argparse
import ast
import copy
from collections import Counter
from functools import lru_cache

import Data
import Function


def infer_counts_from_instance(instance_path: str):
    number_of_trucks = None
    number_of_drones = None
    with open(instance_path, "r", encoding="utf-8") as f:
        for _ in range(8):
            line = f.readline()
            if not line:
                break
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] == "number_truck":
                number_of_trucks = int(parts[-1])
            if len(parts) >= 2 and parts[0] == "number_drone":
                number_of_drones = int(parts[-1])
    return number_of_trucks, number_of_drones


def trip_time(solution, trip):
    route, _ = Function.find_drone_flight_shortest(solution, trip)
    total = Data.euclid_flight_matrix[0][route[0]]
    for i in range(len(route)):
        if i == len(route) - 1:
            total += Data.euclid_flight_matrix[route[i]][0]
        else:
            total += Data.euclid_flight_matrix[route[i]][route[i + 1]]
    return total


def trip_demand(trip):
    return sum(Data.city_demand[pkg] for stop in trip for pkg in stop[1])


def validate_and_summarize(solution):
    feasibility = Function.Check_if_feasible(solution)
    fitness_value, _, _ = Function.fitness(solution)

    served = []
    for truck_route in solution[0]:
        for city, _ in truck_route:
            if city != 0:
                served.append(city)

    expected_customers = list(range(1, Data.number_of_cities))
    missing = [c for c in expected_customers if c not in served]
    duplicated = [c for c, count in Counter(served).items() if count > 1]

    print(f"Feasible (Check_if_feasible): {feasibility}")
    print(f"Fitness: {fitness_value}")
    print(f"Customers served: {len(served)}")
    print(f"Unique customers served: {len(set(served))}")
    print(f"Missing customers: {missing}")
    print(f"Duplicated customers: {duplicated}")


def maximize_multi_resupply(solution):
    if Data.number_of_trucks != 2:
        raise ValueError("This optimizer currently supports exactly 2 trucks.")

    truck_of_city = {}
    for truck_idx, truck_route in enumerate(solution[0]):
        for city, _ in truck_route:
            truck_of_city[city] = truck_idx

    stops = []
    for trip in solution[1]:
        for stop in trip:
            stops.append(stop)

    seq = [[], []]
    for stop in stops:
        seq[truck_of_city[stop[0]]].append(stop)

    def can_trip(trip):
        trucks = [truck_of_city[stop[0]] for stop in trip]
        if len(trucks) != len(set(trucks)):
            return False
        if trip_demand(trip) > Data.drone_capacity:
            return False
        if trip_time(solution, trip) > Data.drone_limit_time:
            return False
        return True

    @lru_cache(None)
    def dp(i, j):
        if i == len(seq[0]) and j == len(seq[1]):
            return (0, 0, [])  # pair_count, covered_in_pairs, trips

        best = (-10**9, -10**9, None)

        if i < len(seq[0]):
            t = [seq[0][i]]
            if can_trip(t):
                p, cov, trips = dp(i + 1, j)
                cand = (p, cov, [t] + trips)
                if cand[:2] > best[:2]:
                    best = cand

        if j < len(seq[1]):
            t = [seq[1][j]]
            if can_trip(t):
                p, cov, trips = dp(i, j + 1)
                cand = (p, cov, [t] + trips)
                if cand[:2] > best[:2]:
                    best = cand

        if i < len(seq[0]) and j < len(seq[1]):
            for t in ([seq[0][i], seq[1][j]], [seq[1][j], seq[0][i]]):
                if can_trip(t):
                    p, cov, trips = dp(i + 1, j + 1)
                    cand = (p + 1, cov + 2, [t] + trips)
                    if cand[:2] > best[:2]:
                        best = cand

        return best

    pair_count, covered_in_pairs, best_trips = dp(0, 0)
    improved = copy.deepcopy(solution)
    improved[1] = best_trips
    return improved, pair_count, covered_in_pairs


def main():
    parser = argparse.ArgumentParser(description="Validate a truck-drone solution.")
    parser.add_argument("--instance", required=True, help="Path to .dat instance file")
    parser.add_argument("--solution", required=True, help="Python-literal solution string")
    parser.add_argument("--L", type=float, required=True, help="Drone flight time limit")
    parser.add_argument("--A", type=int, required=True, help="Drone capacity")
    parser.add_argument("--truck-speed", type=float, default=0.5, help="Truck speed")
    parser.add_argument("--drone-speed", type=float, default=1.0, help="Drone speed")
    parser.add_argument("--trucks", type=int, default=None, help="Override number of trucks")
    parser.add_argument("--drones", type=int, default=None, help="Override number of drones")
    parser.add_argument(
        "--maximize-multi-resupply",
        action="store_true",
        help="Try to maximize number of drone trips with >=2 resupply stops (different trucks).",
    )
    args = parser.parse_args()

    solution = ast.literal_eval(args.solution)

    Data.truck_speed = args.truck_speed
    Data.drone_speed = args.drone_speed
    Data.read_data_random(args.instance)
    inferred_trucks, inferred_drones = infer_counts_from_instance(args.instance)
    Data.number_of_trucks = args.trucks if args.trucks is not None else inferred_trucks
    Data.number_of_drones = args.drones if args.drones is not None else inferred_drones
    Data.drone_limit_time = args.L
    Data.drone_capacity = args.A

    print("=== Current solution ===")
    validate_and_summarize(solution)

    if args.maximize_multi_resupply:
        improved, pair_count, covered_in_pairs = maximize_multi_resupply(solution)
        print("\n=== Improved (maximize multi-resupply trips) ===")
        validate_and_summarize(improved)
        print(f"Multi-resupply trips (>=2 stops): {pair_count}")
        print(f"Stops covered inside multi-resupply trips: {covered_in_pairs}")
        print(f"Improved drone queue: {improved[1]}")


if __name__ == "__main__":
    main()
