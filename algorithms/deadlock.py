"""Deadlock handling: Banker's Algorithm, resource-request check, detection."""


def _shape(alloc, other, avail, other_name):
    if not alloc or not avail:
        raise ValueError("Allocation matrix and available vector are required.")
    m = len(avail)
    if len(other) != len(alloc):
        raise ValueError(f"Allocation and {other_name} must have the same number of processes.")
    for row in alloc + other:
        if len(row) != m:
            raise ValueError("Every row must have one value per resource type.")
    if any(v < 0 for row in alloc + other for v in row) or any(v < 0 for v in avail):
        raise ValueError("Values cannot be negative.")


def bankers(allocation, maximum, available):
    _shape(allocation, maximum, available, "Maximum")
    n, m = len(allocation), len(available)
    need = [[maximum[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    if any(v < 0 for row in need for v in row):
        raise ValueError("Maximum must be >= Allocation for every entry.")
    work, finish, seq, steps = available[:], [False] * n, [], []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                before = work[:]
                work = [work[j] + allocation[i][j] for j in range(m)]
                finish[i] = True
                seq.append(f"P{i}")
                steps.append({"process": f"P{i}", "need": need[i],
                              "work_before": before, "work_after": work[:]})
                progress = True
    return {"need": need, "safe": all(finish), "sequence": seq, "steps": steps,
            "unfinished": [f"P{i}" for i in range(n) if not finish[i]]}


def resource_request(allocation, maximum, available, pid, request):
    base = bankers(allocation, maximum, available)
    n, m = len(allocation), len(available)
    if not 0 <= pid < n:
        raise ValueError(f"Process index must be between 0 and {n - 1}.")
    if len(request) != m:
        raise ValueError("Request must have one value per resource type.")
    if any(r > x for r, x in zip(request, base["need"][pid])):
        return {"granted": False, "reason": f"P{pid} exceeded its maximum claim."}
    if any(r > a for r, a in zip(request, available)):
        return {"granted": False, "reason": f"Resources not available; P{pid} must wait."}
    new_alloc = [row[:] for row in allocation]
    new_alloc[pid] = [a + r for a, r in zip(new_alloc[pid], request)]
    new_avail = [a - r for a, r in zip(available, request)]
    check = bankers(new_alloc, maximum, new_avail)
    if check["safe"]:
        return {"granted": True, "sequence": check["sequence"],
                "reason": "Request can be granted; the system stays safe."}
    return {"granted": False, "reason": "Granting the request would leave the system unsafe."}


def detect(allocation, request, available):
    _shape(allocation, request, available, "Request")
    n, m = len(allocation), len(available)
    work = available[:]
    finish = [all(v == 0 for v in allocation[i]) for i in range(n)]
    order = []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(m)):
                work = [work[j] + allocation[i][j] for j in range(m)]
                finish[i] = True
                order.append(f"P{i}")
                progress = True
    dead = [f"P{i}" for i in range(n) if not finish[i]]
    return {"deadlock": bool(dead), "deadlocked": dead, "order": order}
