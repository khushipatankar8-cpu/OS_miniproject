"""CPU scheduling algorithms: FCFS, SJF, SRTF, Priority, Round Robin.

Process format: {"pid": "P1", "at": 0, "bt": 5, "pr": 2}
Lower priority number = higher priority.
"""
from collections import deque


def validate(processes):
    if not processes:
        raise ValueError("Add at least one process.")
    clean, seen = [], set()
    for p in processes:
        pid = str(p.get("pid", "")).strip()
        if not pid:
            raise ValueError("Every process needs a Process ID.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)
        try:
            at, bt = int(p["at"]), int(p["bt"])
            pr = int(p.get("pr", 0) or 0)
        except (KeyError, ValueError, TypeError):
            raise ValueError(f"Invalid numbers for process {pid}.")
        if at < 0:
            raise ValueError(f"Arrival time of {pid} cannot be negative.")
        if bt <= 0:
            raise ValueError(f"Burst time of {pid} must be greater than 0.")
        clean.append({"pid": pid, "at": at, "bt": bt, "pr": pr})
    return clean


def _add_seg(gantt, pid, start, end):
    if gantt and gantt[-1]["pid"] == pid and gantt[-1]["end"] == start:
        gantt[-1]["end"] = end
    else:
        gantt.append({"pid": pid, "start": start, "end": end})


def _result(procs, gantt):
    first, comp = {}, {}
    for seg in gantt:
        if seg["pid"] == "Idle":
            continue
        first.setdefault(seg["pid"], seg["start"])
        comp[seg["pid"]] = seg["end"]
    rows = []
    for p in procs:
        ct = comp[p["pid"]]
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = first[p["pid"]] - p["at"]
        rows.append({**p, "ct": ct, "tat": tat, "wt": wt, "rt": rt})
    n = len(rows)
    avg = lambda k: round(sum(r[k] for r in rows) / n, 2)
    return {"gantt": gantt, "processes": rows,
            "avg_wt": avg("wt"), "avg_tat": avg("tat"), "avg_rt": avg("rt")}


def _non_preemptive(procs, key):
    remaining = sorted(procs, key=lambda p: p["at"])
    time, gantt = 0, []
    while remaining:
        ready = [p for p in remaining if p["at"] <= time]
        if not ready:
            nxt = min(p["at"] for p in remaining)
            _add_seg(gantt, "Idle", time, nxt)
            time = nxt
            continue
        p = min(ready, key=key)
        _add_seg(gantt, p["pid"], time, time + p["bt"])
        time += p["bt"]
        remaining.remove(p)
    return gantt


def fcfs(procs, **_):
    return _result(procs, _non_preemptive(procs, lambda p: p["at"]))


def sjf(procs, **_):
    return _result(procs, _non_preemptive(procs, lambda p: p["bt"]))


def priority(procs, **_):
    return _result(procs, _non_preemptive(procs, lambda p: p["pr"]))


def srtf(procs, **_):
    rem = {p["pid"]: p["bt"] for p in procs}
    time, done, gantt, n = 0, 0, [], len(procs)
    while done < n:
        ready = [p for p in procs if p["at"] <= time and rem[p["pid"]] > 0]
        if not ready:
            nxt = min(p["at"] for p in procs if rem[p["pid"]] > 0)
            _add_seg(gantt, "Idle", time, nxt)
            time = nxt
            continue
        p = min(ready, key=lambda p: (rem[p["pid"]], p["at"]))
        _add_seg(gantt, p["pid"], time, time + 1)
        time += 1
        rem[p["pid"]] -= 1
        if rem[p["pid"]] == 0:
            done += 1
    return _result(procs, gantt)


def round_robin(procs, quantum=2, **_):
    quantum = int(quantum)
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than 0.")
    order = sorted(procs, key=lambda p: p["at"])
    rem = {p["pid"]: p["bt"] for p in order}
    queue, gantt = deque(), []
    time, i, done, n = 0, 0, 0, len(order)
    while done < n:
        while i < n and order[i]["at"] <= time:
            queue.append(order[i]); i += 1
        if not queue:
            _add_seg(gantt, "Idle", time, order[i]["at"])
            time = order[i]["at"]
            continue
        p = queue.popleft()
        run = min(quantum, rem[p["pid"]])
        _add_seg(gantt, p["pid"], time, time + run)
        time += run
        rem[p["pid"]] -= run
        while i < n and order[i]["at"] <= time:
            queue.append(order[i]); i += 1
        if rem[p["pid"]] > 0:
            queue.append(p)
        else:
            done += 1
    return _result(procs, gantt)


ALGORITHMS = {"FCFS": fcfs, "SJF": sjf, "SRTF": srtf,
              "Priority": priority, "Round Robin": round_robin}


def simulate(algorithm, processes, quantum=2):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return ALGORITHMS[algorithm](validate(processes), quantum=quantum)


def compare_all(processes, quantum=2):
    procs = validate(processes)
    out = []
    for name, fn in ALGORITHMS.items():
        r = fn(procs, quantum=quantum)
        out.append({"algorithm": name, "avg_wt": r["avg_wt"],
                    "avg_tat": r["avg_tat"], "avg_rt": r["avg_rt"]})
    return out
