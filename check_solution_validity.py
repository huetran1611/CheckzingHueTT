import argparse
import ast
import copy
import random
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


def count_multi_visits(queue):
    return sum(1 for trip in queue if len(trip) >= 2)


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
    print(f"Multi-visit trips: {count_multi_visits(solution[1])}")
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
            return (0, 0, [])

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


def build_truck_map(solution):
    truck_of_city = {}
    for truck_idx, truck_route in enumerate(solution[0]):
        for city, _ in truck_route:
            truck_of_city[city] = truck_idx
    return truck_of_city


def trip_structure_ok(solution, trip, truck_of_city):
    trucks = [truck_of_city[stop[0]] for stop in trip]
    if len(trucks) != len(set(trucks)):
        return False
    if trip_demand(trip) > Data.drone_capacity:
        return False
    if trip_time(solution, trip) > Data.drone_limit_time:
        return False
    return True


def mutate_queue(queue, solution, truck_of_city, rng):
    q = copy.deepcopy(queue)
    if not q:
        return q
    action = rng.choice(["swap", "merge", "split", "move"])

    if action == "swap" and len(q) >= 2:
        i, j = rng.sample(range(len(q)), 2)
        q[i], q[j] = q[j], q[i]

    elif action == "merge":
        singles = [i for i, t in enumerate(q) if len(t) == 1]
        if len(singles) >= 2:
            i, j = sorted(rng.sample(singles, 2), reverse=True)
            a = q[i][0]
            b = q[j][0]
            for trip in ([a, b], [b, a]):
                if trip_structure_ok(solution, trip, truck_of_city):
                    q.pop(i)
                    q.pop(j)
                    q.insert(rng.randrange(len(q) + 1), trip)
                    break

    elif action == "split":
        multi = [i for i, t in enumerate(q) if len(t) >= 2]
        if multi:
            i = rng.choice(multi)
            trip = q.pop(i)
            rng.shuffle(trip)
            for stop in trip:
                q.insert(rng.randrange(len(q) + 1), [stop])

    elif action == "move":
        src = [i for i, t in enumerate(q) if len(t) == 1]
        dst = [i for i, t in enumerate(q) if len(t) == 1]
        if src and len(dst) >= 2:
            i = rng.choice(src)
            stop = q[i][0]
            candidates = [j for j in dst if j != i and truck_of_city[q[j][0][0]] != truck_of_city[stop[0]]]
            if candidates:
                j = rng.choice(candidates)
                merged = [stop, q[j][0]]
                if trip_structure_ok(solution, merged, truck_of_city):
                    if i > j:
                        i, j = j, i
                    q.pop(j)
                    q.pop(i)
                    q.insert(rng.randrange(len(q) + 1), merged)
    return q


def search_better_with_multi_visit(solution, iterations, seed):
    rng = random.Random(seed)
    truck_of_city = build_truck_map(solution)

    base_fit, _, _ = Function.fitness(solution)
    base_multi = count_multi_visits(solution[1])

    current_q = copy.deepcopy(solution[1])
    best_solution = None
    best_metric = None

    for _ in range(iterations):
        candidate_q = mutate_queue(current_q, solution, truck_of_city, rng)
        candidate = [copy.deepcopy(solution[0]), candidate_q]
        if not Function.Check_if_feasible(candidate):
            continue

        fit, _, _ = Function.fitness(candidate)
        multi = count_multi_visits(candidate_q)

        if multi > base_multi and fit < base_fit:
            metric = (fit, -multi)
            if best_metric is None or metric < best_metric:
                best_metric = metric
                best_solution = copy.deepcopy(candidate)

        # keep a lightweight hill-climb state
        cur_fit, _, _ = Function.fitness([copy.deepcopy(solution[0]), current_q])
        cur_multi = count_multi_visits(current_q)
        if (multi > cur_multi) or (multi == cur_multi and fit < cur_fit):
            current_q = candidate_q

    return best_solution, base_fit, base_multi


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
    parser.add_argument("--iterations", type=int, default=20000, help="Iterations for search mode")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for search mode")
    parser.add_argument(
        "--maximize-multi-resupply",
        action="store_true",
        help="Try to maximize number of drone trips with >=2 resupply stops (different trucks).",
    )
    parser.add_argument(
        "--search-better-multi-visit",
        action="store_true",
        help="Run iterative transformations and search for solution with more multi-visits and better fitness.",
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

    if args.search_better_multi_visit:
        best, base_fit, base_multi = search_better_with_multi_visit(solution, args.iterations, args.seed)
        print("\n=== Search result (better fitness + more multi-visit) ===")
        if best is None:
            print("No solution found that improves BOTH fitness and multi-visit count in given iterations.")
            print(f"Baseline fitness: {base_fit}")
            print(f"Baseline multi-visit trips: {base_multi}")
        else:
            validate_and_summarize(best)
            print(f"Found solution: {best}")


if __name__ == "__main__":
    main()
