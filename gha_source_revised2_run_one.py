from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from Source_revised2 import AtsParams, ProblemData, adaptive_tabu_search, read_data_file
from Source_revised2.fitness import FitnessResult, evaluate_fitness


def _legacy_solution_or_none(solution: Any) -> Any:
    if solution is None:
        return None
    if hasattr(solution, "to_legacy"):
        return solution.to_legacy()
    return solution


def _override_data(base_data: ProblemData, drone_capacity: float, drone_limit_time: float) -> ProblemData:
    data = ProblemData(**asdict(base_data))
    data.drone_capacity = float(drone_capacity)
    data.drone_limit_time = float(drone_limit_time)
    return data


def _extract_trip_customer_lists(solution: Any) -> list[list[int]]:
    if not solution or not isinstance(solution, list) or len(solution) < 2:
        return []
    trips = solution[1]
    if not isinstance(trips, list):
        return []
    trip_customers: list[list[int]] = []
    for trip in trips:
        customers: list[int] = []
        if not isinstance(trip, list):
            continue
        for leg in trip:
            if not isinstance(leg, list) or len(leg) < 2:
                continue
            delivered = leg[1]
            if isinstance(delivered, list):
                customers.extend(int(c) for c in delivered)
        trip_customers.append(customers)
    return trip_customers


def _count_multi_visit_trips(solution: Any) -> int | None:
    if not solution or not isinstance(solution, list) or len(solution) < 2:
        return None
    trips = solution[1]
    if not isinstance(trips, list):
        return None
    return sum(1 for trip in trips if isinstance(trip, list) and len(trip) > 1)


def _calc_trip_payload_stats(solution: Any, data: ProblemData) -> tuple[float | None, float | None]:
    trips = _extract_trip_customer_lists(solution)
    if not trips:
        return None, None
    total_customers = 0
    total_demand = 0.0
    for customers in trips:
        total_customers += len(customers)
        for customer in customers:
            if 0 <= customer < len(data.demands):
                total_demand += data.demands[customer]
    trip_count = len(trips)
    if trip_count == 0:
        return None, None
    return total_customers / trip_count, total_demand / trip_count


def _round_dict(values: dict[int, float]) -> dict[int, float]:
    return {int(k): round(float(v), 6) for k, v in values.items()}


def _collect_solution_metrics(
    solution: Any,
    eval_result: FitnessResult | None,
    data: ProblemData,
) -> dict[str, Any]:
    if solution is None:
        return {
            "solution": None,
            "multi_visit_trip_count": None,
            "avg_customers_per_drone_trip": None,
            "avg_demand_per_drone_trip": None,
            "drone_trip_times": [],
            "avg_drone_trip_time": None,
            "truck_wait_by_point": {},
            "drone_wait_by_point": {},
            "avg_truck_wait_by_point": None,
            "avg_drone_wait_by_point": None,
        }

    avg_customers, avg_demand = _calc_trip_payload_stats(solution, data)
    if eval_result is None:
        trip_times: list[float] = []
        avg_trip_time = None
        truck_wait = {}
        drone_wait = {}
        avg_truck_wait = None
        avg_drone_wait = None
    else:
        trip_times = [float(v) for _, v in sorted(eval_result.drone_trip_time.items())]
        avg_trip_time = (sum(trip_times) / len(trip_times)) if trip_times else None
        truck_wait = dict(eval_result.truck_wait_by_city)
        drone_wait = dict(eval_result.drone_wait_by_city)
        avg_truck_wait = (sum(truck_wait.values()) / len(truck_wait)) if truck_wait else None
        avg_drone_wait = (sum(drone_wait.values()) / len(drone_wait)) if drone_wait else None
    return {
        "solution": solution,
        "multi_visit_trip_count": _count_multi_visit_trips(solution),
        "avg_customers_per_drone_trip": None if avg_customers is None else round(avg_customers, 6),
        "avg_demand_per_drone_trip": None if avg_demand is None else round(avg_demand, 6),
        "drone_trip_times": [round(v, 6) for v in trip_times],
        "avg_drone_trip_time": None if avg_trip_time is None else round(avg_trip_time, 6),
        "truck_wait_by_point": _round_dict(truck_wait),
        "drone_wait_by_point": _round_dict(drone_wait),
        "avg_truck_wait_by_point": None if avg_truck_wait is None else round(avg_truck_wait, 6),
        "avg_drone_wait_by_point": None if avg_drone_wait is None else round(avg_drone_wait, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Source_revised2 GitHub Actions task.")
    parser.add_argument("--instance", required=True, type=Path)
    parser.add_argument("--instance-group", required=True)
    parser.add_argument("--job-id", required=True, type=int)
    parser.add_argument("--run-index", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--A", required=True, type=float)
    parser.add_argument("--L", required=True, type=float)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    cfg_text = args.config.read_text(encoding="utf-8")
    config = json.loads(cfg_text)
    ats_cfg = config.get("ats_params", {})

    started = time.time()

    base_data = read_data_file(args.instance)
    data = _override_data(base_data, args.A, args.L)

    params = AtsParams(
        nimp=int(ats_cfg.get("nimp", 30)),
        seg=int(ats_cfg.get("seg", 8)),
        div=int(ats_cfg.get("div", 3)),
        gamma1=float(ats_cfg.get("gamma1", 0.5)),
        gamma2=float(ats_cfg.get("gamma2", 0.3)),
        gamma3=float(ats_cfg.get("gamma3", 0.1)),
        gamma4=float(ats_cfg.get("gamma4", 0.3)),
        seed=int(args.seed),
        truck_max_neighbors=int(ats_cfg.get("truck_max_neighbors", 300)),
        drone_max_neighbors=int(ats_cfg.get("drone_max_neighbors", 120)),
        use_drone_refine=bool(ats_cfg.get("use_drone_refine", True)),
        drone_ls_iterations=ats_cfg.get("drone_ls_iterations"),
        diversification_max_neighbors=int(ats_cfg.get("diversification_max_neighbors", 200)),
        diversification_max_moves_per_route=int(ats_cfg.get("diversification_max_moves_per_route", 80)),
        diversification_accept_non_improving=bool(
            ats_cfg.get("diversification_accept_non_improving", True)
        ),
        time_limit_seconds=float(config.get("time_limit_seconds", 7200)),
    )

    result = adaptive_tabu_search(data=data, params=params, verbose=False)

    best_solution = result.best_solution.to_legacy()
    best_multi_solution = _legacy_solution_or_none(result.best_multi_visit_solution)
    best_eval = result.best_eval if result.best_eval.feasible else evaluate_fitness(best_solution, data)
    best_multi_eval = result.best_multi_visit_eval
    if best_multi_solution is not None and best_multi_eval is None:
        best_multi_eval = evaluate_fitness(best_multi_solution, data)

    payload = {
        "job_id": args.job_id,
        "instance_group": args.instance_group,
        "instance": str(args.instance),
        "instance_name": args.instance.name,
        "run_index": args.run_index,
        "seed": args.seed,
        "drone_capacity": args.A,
        "drone_limit_time": args.L,
        "status": "OK",
        "runtime_sec": round(time.time() - started, 6),
        "terminated_by_time_limit": result.terminated_by_time_limit,
        "elapsed_seconds": round(result.elapsed_seconds, 6),
        "initial_objective": result.initial_eval.objective,
        "best_fitness": result.best_eval.objective,
        "best_solution_metrics": _collect_solution_metrics(best_solution, best_eval, data),
        "best_multi_visit_fitness": None if best_multi_eval is None else best_multi_eval.objective,
        "best_multi_visit_metrics": _collect_solution_metrics(best_multi_solution, best_multi_eval, data),
        "segments_run": result.segments_run,
        "diversification_rounds": result.diversification_rounds,
        "weights": result.weights,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best_fitness": payload["best_fitness"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
