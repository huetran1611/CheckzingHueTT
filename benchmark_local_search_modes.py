import argparse
import copy
import csv
import random
import time
from pathlib import Path

import numpy as np

import Data
import Function
import Neighborhood_drone

EPS = 1e-5
SEED = 42


def wrap_solution_for_ls(solution):
    fit, dt, tt = Function.fitness(solution)
    return [copy.deepcopy(solution), [fit, dt, tt], -1, 0, 1]


def apply_drone_local_search(entry, operators, loops):
    current = copy.deepcopy(entry)
    best_in_ls = current[1][0]
    accept_trucks = [0, 1] if Data.number_of_trucks > 1 else [0]
    j = 0

    while j < loops:
        j += 1
        for op in operators:
            if op.__name__ == "Neighborghood_change_drone_route_max_pro_plus_for_specific_truck":
                neighborhood = op(current[0], accept_trucks)
            else:
                neighborhood = op(current[0])
            if not neighborhood:
                continue

            min_in_loop = float("inf")
            next_idx = 0
            for idx, candidate in enumerate(neighborhood):
                cfnode = candidate[1][0]
                if cfnode < best_in_ls - EPS:
                    current = candidate
                    next_idx = idx
                    min_in_loop = cfnode
                    best_in_ls = cfnode
                    j = 0
                elif cfnode < min_in_loop - EPS:
                    min_in_loop = cfnode
                    next_idx = idx
            current = neighborhood[next_idx]

    return current


def run_mode(instance_path, mode, loops):
    random.seed(SEED)
    np.random.seed(SEED)
    Data.read_data_random(instance_path)
    init_sol = Function.initial_solution7()
    entry = wrap_solution_for_ls(init_sol)

    operators_map = {
        "all3": [
            Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus_for_specific_truck,
            Neighborhood_drone.Neighborhood_change_index_trip,
            Neighborhood_drone.Neighborhood_group_trip,
        ],
        "relocation": [Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus_for_specific_truck],
        "index_trip": [Neighborhood_drone.Neighborhood_change_index_trip],
        "group_trip": [Neighborhood_drone.Neighborhood_group_trip],
        "none": [],
    }

    t0 = time.perf_counter()
    result = entry if mode == "none" else apply_drone_local_search(entry, operators_map[mode], loops=loops)
    elapsed = time.perf_counter() - t0
    return result[1][0], elapsed


def main():
    parser = argparse.ArgumentParser(description="Benchmark local search modes on selected instances")
    parser.add_argument("--instance-dir", default="test_data/data_demand_random/50", help="Folder containing .dat instances")
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of instances")
    parser.add_argument("--out-prefix", default="local_search_mode_benchmark_50dir", help="Output filename prefix in Result/")
    parser.add_argument("--loops", type=int, default=2, help="number_of_loop_drone used in local search")
    args = parser.parse_args()

    instance_dir = Path(args.instance_dir)
    instances = sorted(str(p) for p in instance_dir.glob("*.dat"))
    if args.limit is not None:
        instances = instances[: args.limit]

    if not instances:
        raise ValueError(f"No .dat instances found in {instance_dir}")

    modes = ["all3", "relocation", "index_trip", "group_trip", "none"]
    rows = []

    for idx, ins in enumerate(instances, start=1):
        metrics = {}
        for mode in modes:
            fitness, runtime = run_mode(ins, mode, args.loops)
            metrics[mode] = {"fitness": fitness, "runtime": runtime}

        f_all3 = metrics["all3"]["fitness"]
        t_all3 = metrics["all3"]["runtime"]
        for mode in modes:
            fitness = metrics[mode]["fitness"]
            runtime = metrics[mode]["runtime"]
            quality_gap_pct = ((fitness - f_all3) / f_all3 * 100.0) if f_all3 else 0.0
            time_save_pct = ((t_all3 - runtime) / t_all3 * 100.0) if t_all3 else 0.0
            rows.append(
                {
                    "instance": ins,
                    "mode": mode,
                    "fitness": fitness,
                    "runtime_s": runtime,
                    "quality_gap_vs_all3_pct": quality_gap_pct,
                    "time_save_vs_all3_pct": time_save_pct,
                }
            )
        if idx % 10 == 0 or idx == len(instances):
            print(f"Processed {idx}/{len(instances)} instances")

    out_dir = Path("Result")
    out_dir.mkdir(exist_ok=True)
    out_csv = out_dir / f"{args.out_prefix}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "instance",
                "mode",
                "fitness",
                "runtime_s",
                "quality_gap_vs_all3_pct",
                "time_save_vs_all3_pct",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for mode in modes:
        subset = [r for r in rows if r["mode"] == mode]
        summary[mode] = {
            "avg_quality_gap_pct": sum(r["quality_gap_vs_all3_pct"] for r in subset) / len(subset),
            "avg_time_save_pct": sum(r["time_save_vs_all3_pct"] for r in subset) / len(subset),
            "avg_runtime_s": sum(r["runtime_s"] for r in subset) / len(subset),
            "avg_fitness": sum(r["fitness"] for r in subset) / len(subset),
        }

    out_txt = out_dir / f"{args.out_prefix}_summary.txt"
    with out_txt.open("w", encoding="utf-8") as f:
        f.write(f"Benchmark on {len(instances)} instances in {instance_dir}\n")
        f.write(f"Reference mode for gaps: all3 | loops={args.loops}\n\n")
        for mode in modes:
            s = summary[mode]
            f.write(
                f"{mode}: avg_fitness={s['avg_fitness']:.4f}, avg_runtime_s={s['avg_runtime_s']:.6f}, "
                f"avg_quality_gap_vs_all3_pct={s['avg_quality_gap_pct']:.4f}, "
                f"avg_time_save_vs_all3_pct={s['avg_time_save_pct']:.2f}\n"
            )

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_txt}")


if __name__ == "__main__":
    main()
