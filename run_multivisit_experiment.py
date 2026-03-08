import os
import csv
import time
import random
import sys
import types
import multiprocessing as mp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import openpyxl before numpy shim so its optional numpy checks are resolved normally.
import openpyxl  # noqa: F401

# Work around local numpy import issue in this environment.
class _FakeArray2D:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            i, j = idx
            return self._data[i][j]
        return self._data[idx]

    def __setitem__(self, idx, value):
        if isinstance(idx, tuple):
            i, j = idx
            self._data[i][j] = value
        else:
            self._data[idx] = value

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


fake_numpy = types.SimpleNamespace(array=lambda x: _FakeArray2D(x))
class _RandomShim:
    @staticmethod
    def choice(n, p=None):
        population = list(range(n))
        return random.choices(population, weights=p, k=1)[0]
fake_numpy.random = _RandomShim()
sys.modules['numpy'] = fake_numpy

import Data
import Function
import test_similarity

INSTANCES = [
    r"test_data\data_demand_random\30\C201_3.dat",
    r"test_data\data_demand_random\30\C201_0.5.dat",
]
THETAS = [1, 2, 3]
RUNS = 5
DRONE_CAPACITIES = [4, 8]
DRONE_LIMIT_TIMES = [60, 120]
WORKERS = 4
OUTPUT_CSV = os.path.join("result", f"multivisit_experiment_{int(time.time())}.csv")


def ensure_parent(path):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def _extract_drone_trip_lists(solution):
    if not solution or not isinstance(solution, list) or len(solution) < 2:
        return []
    trips = solution[1]
    if not isinstance(trips, list):
        return []

    # Each drone trip is a list of one or more flight legs, each leg like [launch_city, [delivered_customers...]].
    all_trips = []
    for trip in trips:
        if not isinstance(trip, list):
            continue
        customers = []
        for leg in trip:
            if not isinstance(leg, list) or len(leg) < 2:
                continue
            delivered = leg[1]
            if isinstance(delivered, list):
                for c in delivered:
                    if isinstance(c, int):
                        customers.append(c)
        all_trips.append(customers)
    return all_trips


def _extract_drone_trip_launch_points(solution):
    if not solution or not isinstance(solution, list) or len(solution) < 2:
        return []
    trips = solution[1]
    if not isinstance(trips, list):
        return []

    launch_trips = []
    for trip in trips:
        if not isinstance(trip, list):
            continue
        launches = []
        for leg in trip:
            if not isinstance(leg, list) or len(leg) < 1:
                continue
            launch_city = leg[0]
            if isinstance(launch_city, int):
                launches.append(launch_city)
        launch_trips.append(launches)
    return launch_trips


def _calc_single_trip_distance(launch_points):
    if not launch_points:
        return 0.0

    # Keep the same nearest-neighbor visiting logic used in feasibility checks.
    remaining = list(launch_points)
    route = []
    current = 0
    while remaining:
        next_point = min(remaining, key=lambda c: Data.euclid_flight_matrix[current][c])
        route.append(next_point)
        remaining.remove(next_point)
        current = next_point

    distance = Data.euclid_flight_matrix[0][route[0]] + Data.euclid_flight_matrix[route[-1]][0]
    for i in range(len(route) - 1):
        distance += Data.euclid_flight_matrix[route[i]][route[i + 1]]
    return float(distance)


def calc_drone_trip_distances(solution):
    launch_trips = _extract_drone_trip_launch_points(solution)
    if not launch_trips:
        return [], None

    distances = [_calc_single_trip_distance(points) for points in launch_trips]
    if not distances:
        return [], None

    avg_distance = sum(distances) / len(distances)
    return distances, avg_distance


def calc_wait_stats(solution):
    if solution is None:
        return {}, {}, None, None

    truck_wait_by_point = Function.cal_truck_wait_time_by_point(solution)
    drone_wait_by_point = Function.cal_drone_wait_time_by_point(solution)

    truck_avg_wait = None
    drone_avg_wait = None

    if truck_wait_by_point:
        truck_avg_wait = sum(truck_wait_by_point.values()) / len(truck_wait_by_point)
    if drone_wait_by_point:
        drone_avg_wait = sum(drone_wait_by_point.values()) / len(drone_wait_by_point)

    return truck_wait_by_point, drone_wait_by_point, truck_avg_wait, drone_avg_wait


def calc_drone_trip_stats(solution):
    trips = _extract_drone_trip_lists(solution)
    if not trips:
        return None, None

    total_customers = 0
    total_demand = 0.0
    for customers in trips:
        total_customers += len(customers)
        for c in customers:
            if 0 <= c < len(Data.city_demand):
                total_demand += Data.city_demand[c]

    trip_count = len(trips)
    if trip_count == 0:
        return None, None

    avg_customers = total_customers / trip_count
    avg_demand = total_demand / trip_count
    return avg_customers, avg_demand


def run_one_task(task):
    instance, theta, run, drone_capacity, drone_limit_time = task
    t0 = time.time()

    if not os.path.exists(instance):
        return {
            "instance": instance,
            "drone_capacity": drone_capacity,
            "drone_limit_time": drone_limit_time,
            "theta": theta,
            "run": run,
            "best_fitness": "",
            "best_sol": "",
            "best_multi_visit_fitness": "",
            "best_multi_visit_sol": "",
            "best_sol_avg_customers_per_drone_trip": "",
            "best_sol_avg_demand_per_drone_trip": "",
            "best_sol_drone_trip_distances": "",
            "best_sol_avg_distance_per_drone_trip": "",
            "best_sol_truck_wait_by_point": "",
            "best_sol_drone_wait_by_point": "",
            "best_sol_avg_truck_wait_by_point": "",
            "best_sol_avg_drone_wait_by_point": "",
            "best_multi_visit_sol_avg_customers_per_drone_trip": "",
            "best_multi_visit_sol_avg_demand_per_drone_trip": "",
            "best_multi_visit_sol_drone_trip_distances": "",
            "best_multi_visit_sol_avg_distance_per_drone_trip": "",
            "best_multi_visit_sol_truck_wait_by_point": "",
            "best_multi_visit_sol_drone_wait_by_point": "",
            "best_multi_visit_sol_avg_truck_wait_by_point": "",
            "best_multi_visit_sol_avg_drone_wait_by_point": "",
            "status": "DATA_NOT_FOUND",
            "runtime_sec": round(time.time() - t0, 3),
        }

    # Ensure each run has an independent random stream.
    random.seed((os.getpid() * 1000003) + run + int(theta) * 997)

    try:
        Data.read_data_random(instance)
        Data.drone_capacity = drone_capacity
        Data.drone_limit_time = drone_limit_time
        test_similarity.theta = theta

        best_fitness, best_sol, data_to_write = test_similarity.Tabu_search_for_CVRP(1)
        best_multi_visit_sol = data_to_write.get("best_multi_visit_sol")

        best_avg_cust, best_avg_demand = calc_drone_trip_stats(best_sol)
        mv_avg_cust, mv_avg_demand = calc_drone_trip_stats(best_multi_visit_sol)
        best_distances, best_avg_distance = calc_drone_trip_distances(best_sol)
        mv_distances, mv_avg_distance = calc_drone_trip_distances(best_multi_visit_sol)
        best_truck_wait, best_drone_wait, best_avg_truck_wait, best_avg_drone_wait = calc_wait_stats(best_sol)
        mv_truck_wait, mv_drone_wait, mv_avg_truck_wait, mv_avg_drone_wait = calc_wait_stats(best_multi_visit_sol)

        return {
            "instance": instance,
            "drone_capacity": drone_capacity,
            "drone_limit_time": drone_limit_time,
            "theta": theta,
            "run": run,
            "best_fitness": best_fitness,
            "best_sol": str(best_sol),
            "best_multi_visit_fitness": data_to_write.get("best_multi_visit_fitness"),
            "best_multi_visit_sol": str(best_multi_visit_sol),
            "best_sol_avg_customers_per_drone_trip": None if best_avg_cust is None else round(best_avg_cust, 6),
            "best_sol_avg_demand_per_drone_trip": None if best_avg_demand is None else round(best_avg_demand, 6),
            "best_sol_drone_trip_distances": str([round(v, 6) for v in best_distances]),
            "best_sol_avg_distance_per_drone_trip": None if best_avg_distance is None else round(best_avg_distance, 6),
            "best_sol_truck_wait_by_point": str({k: round(v, 6) for k, v in best_truck_wait.items()}),
            "best_sol_drone_wait_by_point": str({k: round(v, 6) for k, v in best_drone_wait.items()}),
            "best_sol_avg_truck_wait_by_point": None if best_avg_truck_wait is None else round(best_avg_truck_wait, 6),
            "best_sol_avg_drone_wait_by_point": None if best_avg_drone_wait is None else round(best_avg_drone_wait, 6),
            "best_multi_visit_sol_avg_customers_per_drone_trip": None if mv_avg_cust is None else round(mv_avg_cust, 6),
            "best_multi_visit_sol_avg_demand_per_drone_trip": None if mv_avg_demand is None else round(mv_avg_demand, 6),
            "best_multi_visit_sol_drone_trip_distances": str([round(v, 6) for v in mv_distances]),
            "best_multi_visit_sol_avg_distance_per_drone_trip": None if mv_avg_distance is None else round(mv_avg_distance, 6),
            "best_multi_visit_sol_truck_wait_by_point": str({k: round(v, 6) for k, v in mv_truck_wait.items()}),
            "best_multi_visit_sol_drone_wait_by_point": str({k: round(v, 6) for k, v in mv_drone_wait.items()}),
            "best_multi_visit_sol_avg_truck_wait_by_point": None if mv_avg_truck_wait is None else round(mv_avg_truck_wait, 6),
            "best_multi_visit_sol_avg_drone_wait_by_point": None if mv_avg_drone_wait is None else round(mv_avg_drone_wait, 6),
            "status": "OK",
            "runtime_sec": round(time.time() - t0, 3),
        }
    except Exception as exc:
        return {
            "instance": instance,
            "drone_capacity": drone_capacity,
            "drone_limit_time": drone_limit_time,
            "theta": theta,
            "run": run,
            "best_fitness": "",
            "best_sol": "",
            "best_multi_visit_fitness": "",
            "best_multi_visit_sol": "",
            "best_sol_avg_customers_per_drone_trip": "",
            "best_sol_avg_demand_per_drone_trip": "",
            "best_sol_drone_trip_distances": "",
            "best_sol_avg_distance_per_drone_trip": "",
            "best_sol_truck_wait_by_point": "",
            "best_sol_drone_wait_by_point": "",
            "best_sol_avg_truck_wait_by_point": "",
            "best_sol_avg_drone_wait_by_point": "",
            "best_multi_visit_sol_avg_customers_per_drone_trip": "",
            "best_multi_visit_sol_avg_demand_per_drone_trip": "",
            "best_multi_visit_sol_drone_trip_distances": "",
            "best_multi_visit_sol_avg_distance_per_drone_trip": "",
            "best_multi_visit_sol_truck_wait_by_point": "",
            "best_multi_visit_sol_drone_wait_by_point": "",
            "best_multi_visit_sol_avg_truck_wait_by_point": "",
            "best_multi_visit_sol_avg_drone_wait_by_point": "",
            "status": f"ERROR: {type(exc).__name__}: {exc}",
            "runtime_sec": round(time.time() - t0, 3),
        }


def main():
    ensure_parent(OUTPUT_CSV)
    tasks = []
    for instance in INSTANCES:
        for drone_capacity in DRONE_CAPACITIES:
            for drone_limit_time in DRONE_LIMIT_TIMES:
                for theta in THETAS:
                    for run in range(1, RUNS + 1):
                        tasks.append((instance, theta, run, drone_capacity, drone_limit_time))

    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=WORKERS) as pool:
        rows = list(pool.imap_unordered(run_one_task, tasks))

    rows.sort(
        key=lambda r: (
            r.get("instance", ""),
            r.get("drone_capacity", 0),
            r.get("drone_limit_time", 0),
            r.get("theta", 0),
            r.get("run", 0),
        )
    )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "instance",
            "drone_capacity",
            "drone_limit_time",
            "theta",
            "run",
            "best_fitness",
            "best_sol",
            "best_multi_visit_fitness",
            "best_multi_visit_sol",
            "best_sol_avg_customers_per_drone_trip",
            "best_sol_avg_demand_per_drone_trip",
            "best_sol_drone_trip_distances",
            "best_sol_avg_distance_per_drone_trip",
            "best_sol_truck_wait_by_point",
            "best_sol_drone_wait_by_point",
            "best_sol_avg_truck_wait_by_point",
            "best_sol_avg_drone_wait_by_point",
            "best_multi_visit_sol_avg_customers_per_drone_trip",
            "best_multi_visit_sol_avg_demand_per_drone_trip",
            "best_multi_visit_sol_drone_trip_distances",
            "best_multi_visit_sol_avg_distance_per_drone_trip",
            "best_multi_visit_sol_truck_wait_by_point",
            "best_multi_visit_sol_drone_wait_by_point",
            "best_multi_visit_sol_avg_truck_wait_by_point",
            "best_multi_visit_sol_avg_drone_wait_by_point",
            "runtime_sec",
            "status",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    ok_count = sum(1 for r in rows if r.get("status") == "OK")
    print("output_csv=", OUTPUT_CSV)
    print("total_rows=", len(rows))
    print("ok_rows=", ok_count)
    print("workers=", WORKERS)


if __name__ == "__main__":
    main()
