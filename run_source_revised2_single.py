from __future__ import annotations

import argparse
import csv
import glob
import json
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from Source_revised2 import AtsParams, ProblemData, adaptive_tabu_search, read_data_file


DEFAULT_INSTANCE = Path(
    "/Users/huetran/CheckzingHueTT/test_data/data_demand_random/15/C101_3.dat"
)
DEFAULT_CONFIG = Path(
    "/Users/huetran/CheckzingHueTT/source_revised2_c201_batch.yml"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Source_revised2 Adaptive Tabu Search on one instance or a config batch."
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=DEFAULT_INSTANCE,
        help="Path to the .dat instance file for single-run mode.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional config file for batch-run mode. JSON syntax in .yml is supported.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for single-run mode.")
    parser.add_argument("--nimp", type=int, default=30, help="ATS inner stagnation limit.")
    parser.add_argument("--seg", type=int, default=8, help="Segments before diversification.")
    parser.add_argument("--div", type=int, default=3, help="Diversification stop limit.")
    parser.add_argument(
        "--truck-max-neighbors",
        type=int,
        default=300,
        help="Max truck neighbors per neighborhood call.",
    )
    parser.add_argument(
        "--drone-max-neighbors",
        type=int,
        default=120,
        help="Max drone neighbors per local-search call.",
    )
    parser.add_argument(
        "--no-drone-refine",
        action="store_true",
        help="Disable drone local search refinement.",
    )
    parser.add_argument(
        "--time-limit-seconds",
        type=float,
        default=None,
        help="Optional wall-clock limit for one ATS run.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print ATS segment progress.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a compact JSON summary at the end.",
    )
    return parser.parse_args()


def _legacy_solution_or_none(solution: Any) -> Any:
    if solution is None:
        return None
    if hasattr(solution, "to_legacy"):
        return solution.to_legacy()
    return solution


def _solution_summary(result: Any) -> dict[str, Any]:
    return {
        "objective": result.best_eval.objective,
        "initial_objective": result.initial_eval.objective,
        "segments_run": result.segments_run,
        "diversification_rounds": result.diversification_rounds,
        "terminated_by_time_limit": result.terminated_by_time_limit,
        "elapsed_seconds": result.elapsed_seconds,
        "weights": result.weights,
        "truck_routes": result.best_solution.to_legacy()[0],
        "drone_queue": result.best_solution.to_legacy()[1],
        "best_multi_visit_fitness": None
        if result.best_multi_visit_eval is None
        else result.best_multi_visit_eval.objective,
        "best_multi_visit_solution": _legacy_solution_or_none(result.best_multi_visit_solution),
    }


def _load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Config is not valid JSON and PyYAML is unavailable in this interpreter."
            ) from exc
        loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError("Config root must be a mapping/object.")
    return loaded


def _discover_instances(patterns: list[str]) -> list[Path]:
    seen: set[str] = set()
    discovered: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        for match in matches:
            resolved = str(Path(match).resolve())
            if resolved not in seen:
                seen.add(resolved)
                discovered.append(Path(resolved))
    return discovered


def _override_data(base_data: ProblemData, drone_capacity: float, drone_limit_time: float) -> ProblemData:
    data = ProblemData(**asdict(base_data))
    data.drone_capacity = float(drone_capacity)
    data.drone_limit_time = float(drone_limit_time)
    return data


def _run_one(
    instance_path: Path,
    *,
    seed: int,
    drone_capacity: float | None,
    drone_limit_time: float | None,
    params: AtsParams,
    verbose: bool,
) -> dict[str, Any]:
    base_data = read_data_file(instance_path)
    data = base_data
    if drone_capacity is not None or drone_limit_time is not None:
        data = _override_data(
            base_data,
            drone_capacity if drone_capacity is not None else base_data.drone_capacity,
            drone_limit_time if drone_limit_time is not None else base_data.drone_limit_time,
        )

    run_params = AtsParams(
        nimp=params.nimp,
        seg=params.seg,
        div=params.div,
        gamma1=params.gamma1,
        gamma2=params.gamma2,
        gamma3=params.gamma3,
        gamma4=params.gamma4,
        seed=seed,
        truck_max_neighbors=params.truck_max_neighbors,
        drone_max_neighbors=params.drone_max_neighbors,
        use_drone_refine=params.use_drone_refine,
        drone_ls_iterations=params.drone_ls_iterations,
        diversification_max_neighbors=params.diversification_max_neighbors,
        diversification_max_moves_per_route=params.diversification_max_moves_per_route,
        diversification_accept_non_improving=params.diversification_accept_non_improving,
        time_limit_seconds=params.time_limit_seconds,
    )
    result = adaptive_tabu_search(
        data=data,
        params=run_params,
        verbose=verbose,
    )
    return {
        "instance": str(instance_path),
        "seed": seed,
        "drone_capacity": data.drone_capacity,
        "drone_limit_time": data.drone_limit_time,
        **_solution_summary(result),
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "instance",
        "run_index",
        "seed",
        "drone_capacity",
        "drone_limit_time",
        "objective",
        "initial_objective",
        "segments_run",
        "diversification_rounds",
        "terminated_by_time_limit",
        "elapsed_seconds",
        "best_multi_visit_fitness",
        "truck_routes",
        "drone_queue",
        "best_multi_visit_solution",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "instance": row["instance"],
                    "run_index": row.get("run_index"),
                    "seed": row["seed"],
                    "drone_capacity": row["drone_capacity"],
                    "drone_limit_time": row["drone_limit_time"],
                    "objective": row["objective"],
                    "initial_objective": row["initial_objective"],
                    "segments_run": row["segments_run"],
                    "diversification_rounds": row["diversification_rounds"],
                    "terminated_by_time_limit": row["terminated_by_time_limit"],
                    "elapsed_seconds": row["elapsed_seconds"],
                    "best_multi_visit_fitness": row["best_multi_visit_fitness"],
                    "truck_routes": json.dumps(row["truck_routes"], ensure_ascii=False),
                    "drone_queue": json.dumps(row["drone_queue"], ensure_ascii=False),
                    "best_multi_visit_solution": json.dumps(
                        row["best_multi_visit_solution"],
                        ensure_ascii=False,
                    ),
                }
            )


def _run_from_config(config_path: Path, verbose: bool) -> None:
    cfg = _load_config(config_path)
    patterns = cfg.get("instance_patterns", [])
    if not isinstance(patterns, list) or not patterns:
        raise ValueError("Config must provide a non-empty 'instance_patterns' list.")

    instances = _discover_instances(patterns)
    if not instances:
        raise FileNotFoundError("No instance matched 'instance_patterns'.")

    drone_capacities = cfg.get("A", [4, 8])
    drone_limit_times = cfg.get("L", [60, 90, 120])
    runs_per_config = int(cfg.get("runs_per_config", 3))
    base_seed = int(cfg.get("base_seed", 42))
    output_json = Path(cfg.get("output_json", "Result/source_revised2_c201_runs.json")).resolve()
    output_csv = Path(cfg.get("output_csv", "Result/source_revised2_c201_runs.csv")).resolve()

    params_cfg = cfg.get("ats_params", {})
    params = AtsParams(
        nimp=int(params_cfg.get("nimp", 30)),
        seg=int(params_cfg.get("seg", 8)),
        div=int(params_cfg.get("div", 3)),
        gamma1=float(params_cfg.get("gamma1", 0.5)),
        gamma2=float(params_cfg.get("gamma2", 0.3)),
        gamma3=float(params_cfg.get("gamma3", 0.1)),
        gamma4=float(params_cfg.get("gamma4", 0.3)),
        truck_max_neighbors=int(params_cfg.get("truck_max_neighbors", 300)),
        drone_max_neighbors=int(params_cfg.get("drone_max_neighbors", 120)),
        use_drone_refine=bool(params_cfg.get("use_drone_refine", True)),
        drone_ls_iterations=params_cfg.get("drone_ls_iterations"),
        diversification_max_neighbors=int(params_cfg.get("diversification_max_neighbors", 200)),
        diversification_max_moves_per_route=int(params_cfg.get("diversification_max_moves_per_route", 80)),
        diversification_accept_non_improving=bool(
            params_cfg.get("diversification_accept_non_improving", True)
        ),
        time_limit_seconds=float(cfg.get("time_limit_seconds", 7200)),
    )

    rows: list[dict[str, Any]] = []
    total_jobs = len(instances) * len(drone_capacities) * len(drone_limit_times) * runs_per_config
    job_idx = 0
    started_at = time.strftime("%Y-%m-%d %H:%M:%S")

    for instance in instances:
        for drone_capacity in drone_capacities:
            for drone_limit_time in drone_limit_times:
                for run_idx in range(runs_per_config):
                    job_idx += 1
                    seed = base_seed + run_idx
                    print(
                        f"[{job_idx}/{total_jobs}] instance={instance.name} "
                        f"A={drone_capacity} L={drone_limit_time} run={run_idx + 1}/{runs_per_config} seed={seed}"
                    )
                    row = _run_one(
                        instance,
                        seed=seed,
                        drone_capacity=float(drone_capacity),
                        drone_limit_time=float(drone_limit_time),
                        params=params,
                        verbose=verbose,
                    )
                    row["run_index"] = run_idx + 1
                    rows.append(row)
                    output_json.parent.mkdir(parents=True, exist_ok=True)
                    output_json.write_text(
                        json.dumps(
                            {
                                "started_at": started_at,
                                "config": cfg,
                                "results": rows,
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
                    _write_csv(output_csv, rows)

    print(f"JSON saved to: {output_json}")
    print(f"CSV saved to: {output_csv}")


def main() -> None:
    args = _parse_args()

    if args.config is not None:
        _run_from_config(args.config, verbose=args.verbose)
        return

    params = AtsParams(
        seed=args.seed,
        nimp=args.nimp,
        seg=args.seg,
        div=args.div,
        truck_max_neighbors=args.truck_max_neighbors,
        drone_max_neighbors=args.drone_max_neighbors,
        use_drone_refine=not args.no_drone_refine,
        time_limit_seconds=args.time_limit_seconds,
    )

    row = _run_one(
        args.instance,
        seed=args.seed,
        drone_capacity=None,
        drone_limit_time=None,
        params=params,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return

    print(f"Instance: {args.instance}")
    print(f"Initial objective: {row['initial_objective']}")
    print(f"Best objective: {row['objective']}")
    print(f"Segments run: {row['segments_run']}")
    print(f"Diversification rounds: {row['diversification_rounds']}")
    print(f"Elapsed seconds: {row['elapsed_seconds']}")
    print(f"Terminated by time limit: {row['terminated_by_time_limit']}")
    print("Best truck routes:")
    for idx, route in enumerate(row["truck_routes"]):
        print(f"  Truck {idx}: {route}")
    print("Best drone queue:")
    for idx, trip in enumerate(row["drone_queue"]):
        print(f"  Trip {idx}: {trip}")
    print(f"Best multi visit fitness: {row['best_multi_visit_fitness']}")
    print(f"Best multi visit solution: {row['best_multi_visit_solution']}")


if __name__ == "__main__":
    main()
