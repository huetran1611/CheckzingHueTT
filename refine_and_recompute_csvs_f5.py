#!/usr/bin/env python3
import argparse
import ast
import csv
import json
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Dict, List, Optional


def _is_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False


def _to_int(x) -> Optional[int]:
    try:
        return int(x)
    except Exception:
        try:
            return int(float(x))
        except Exception:
            return None


def read_instance_releases(path: str) -> List[int]:
    lines = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    if not lines:
        return []
    first = lines[0].split()
    parameterized = bool(first) and first[0] == "number_truck"
    header_only = (not parameterized) and bool(first) and (not _is_numeric(first[0]))
    start = 8 if parameterized else (1 if header_only else 0)
    releases: List[int] = []
    for ln in lines[start:]:
        t = ln.split()
        if len(t) >= 4:
            releases.append(int(float(t[3])))
    return releases


def normalize_solution_text(solution_text: str, releases: List[int]) -> str:
    txt = (solution_text or "").strip()
    if not txt:
        return ""
    try:
        data = ast.literal_eval(txt)
    except Exception:
        return txt
    if not (isinstance(data, list) and len(data) == 2):
        return txt
    trucks_raw, drone_raw = data
    if not isinstance(trucks_raw, list) or not isinstance(drone_raw, list):
        return txt

    n = len(releases)
    owner: Dict[int, int] = {}
    pos_on_truck: Dict[int, int] = {}
    trucks = []
    for tid, route in enumerate(trucks_raw):
        route_norm = []
        if isinstance(route, list):
            for i, st in enumerate(route):
                if not isinstance(st, (list, tuple)) or len(st) < 2:
                    continue
                c = _to_int(st[0])
                if c is None:
                    continue
                pk = st[1] if isinstance(st[1], list) else []
                pk_norm = [int(x) for x in pk if _to_int(x) is not None]
                route_norm.append([c, pk_norm])
                if c > 0 and c < n:
                    owner[c] = tid
                    pos_on_truck[c] = i
        trucks.append(route_norm)

    drone = []
    for trip in drone_raw:
        if not isinstance(trip, list):
            continue
        trip_norm = []
        for ev in trip:
            if not isinstance(ev, (list, tuple)) or len(ev) < 2:
                continue
            rv = _to_int(ev[0])
            if rv is None:
                continue
            pk = ev[1] if isinstance(ev[1], list) else []
            pk_norm = [int(x) for x in pk if _to_int(x) is not None]
            trip_norm.append([rv, pk_norm])
        drone.append(trip_norm)

    def eligible(pkg: int) -> bool:
        return 0 < pkg < n and releases[pkg] > 0

    while True:
        changed = False

        clean = []
        for trip in drone:
            evs = []
            for rv, pkgs in trip:
                if rv <= 0 or rv >= n:
                    changed = True
                    continue
                tid = owner.get(rv, -1)
                if tid < 0:
                    changed = True
                    continue
                rv_pos = pos_on_truck.get(rv, -1)
                if rv_pos < 0:
                    changed = True
                    continue

                keep = []
                for x in pkgs:
                    if not eligible(x):
                        changed = True
                        continue
                    if owner.get(x, -1) != tid:
                        changed = True
                        continue
                    if pos_on_truck.get(x, -1) < rv_pos:
                        changed = True
                        continue
                    keep.append(x)

                if not keep:
                    changed = True
                    continue
                evs.append([rv, keep])
            if evs:
                clean.append(evs)
            elif trip:
                changed = True
        drone = clean

        is_resup = [0] * n
        for trip in drone:
            for _rv, pkgs in trip:
                for x in pkgs:
                    if 0 < x < n:
                        is_resup[x] = 1

        truck_count = max(owner.values(), default=-1) + 1
        rmax = [0] * max(1, truck_count)
        for c in range(1, n):
            t = owner.get(c, -1)
            if t >= 0 and not is_resup[c]:
                rmax[t] = max(rmax[t], releases[c])

        removed = False
        pruned = []
        for trip in drone:
            evs = []
            for rv, pkgs in trip:
                t = owner.get(rv, -1)
                if t < 0:
                    removed = True
                    continue
                keep = []
                for x in pkgs:
                    if x <= rmax[t]:
                        removed = True
                        continue
                    keep.append(x)
                if keep:
                    evs.append([rv, keep])
                else:
                    removed = True
            if evs:
                pruned.append(evs)
        drone = pruned

        if not changed and not removed:
            break

    return json.dumps([trucks, drone], separators=(",", ":"))


def process_one(
    in_csv: pathlib.Path,
    out_csv: pathlib.Path,
    solver_bin: str,
    workers: int,
    release_cache: Dict[str, List[int]],
) -> int:
    with in_csv.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames or []
        rows = list(r)

    for row in rows:
        inst = (row.get("instance") or "").strip()
        rel = release_cache.get(inst)
        if rel is None:
            rel = read_instance_releases(inst) if inst else []
            release_cache[inst] = rel
        if "best_solution" in row:
            row["best_solution"] = normalize_solution_text(row.get("best_solution", ""), rel)
        if "best_multi_solution" in row:
            row["best_multi_solution"] = normalize_solution_text(row.get("best_multi_solution", ""), rel)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    env = os.environ.copy()
    env["SOLVER_BIN"] = solver_bin
    env["N_TRUCK"] = "2"
    env["N_DRONE"] = "1"
    env["PARALLEL_JOBS"] = str(workers)
    rc = subprocess.run(
        [sys.executable, "recompute_metrics_from_solutions_csv.py", str(out_csv)],
        env=env,
        text=True,
    ).returncode
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--solver-bin", default="C_Version/read_data_f5")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("inputs", nargs="+")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    release_cache: Dict[str, List[int]] = {}
    overall_rc = 0

    for s in args.inputs:
        in_csv = pathlib.Path(s)
        out_csv = out_dir / (in_csv.stem + "_refine.csv")
        print(f"[RUN] {in_csv}")
        rc = process_one(in_csv, out_csv, args.solver_bin, args.workers, release_cache)
        fail_rep = pathlib.Path("batch_init_ats_improved_with_multivisit_recompute_failures.csv")
        if fail_rep.exists():
            dst = out_dir / (in_csv.stem + "_recompute_failures.csv")
            shutil.move(str(fail_rep), str(dst))
            print(f"[REPORT] {dst}")
        print(f"[OUT] {out_csv} rc={rc}")
        if rc != 0:
            overall_rc = 1

    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
