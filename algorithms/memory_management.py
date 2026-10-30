"""Contiguous memory allocation (fixed partitions, one process per block):
First Fit, Best Fit, Worst Fit, Next Fit."""

STRATEGIES = {"First Fit": "first", "Best Fit": "best",
              "Worst Fit": "worst", "Next Fit": "next"}


def _check(values, name):
    if not values:
        raise ValueError(f"Enter at least one {name}.")
    if any(v <= 0 for v in values):
        raise ValueError(f"All {name} sizes must be positive.")
    return [int(v) for v in values]


def allocate(blocks, processes, strategy):
    blocks = _check(blocks, "block")
    processes = _check(processes, "process")
    nb = len(blocks)
    owner = [None] * nb
    last = 0
    alloc = []
    for pi, size in enumerate(processes):
        fits = [i for i in range(nb) if owner[i] is None and blocks[i] >= size]
        idx = None
        if fits:
            if strategy == "first":
                idx = fits[0]
            elif strategy == "best":
                idx = min(fits, key=lambda i: (blocks[i], i))
            elif strategy == "worst":
                idx = max(fits, key=lambda i: (blocks[i], -i))
            elif strategy == "next":
                for k in range(nb):
                    i = (last + k) % nb
                    if i in fits:
                        idx = i
                        break
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
        if idx is not None:
            owner[idx] = pi
            last = idx
        alloc.append({
            "pid": f"P{pi + 1}", "size": size,
            "block": None if idx is None else idx + 1,
            "block_size": None if idx is None else blocks[idx],
            "internal": None if idx is None else blocks[idx] - size,
        })

    internal = sum(a["internal"] for a in alloc if a["block"])
    unalloc = [a["size"] for a in alloc if a["block"] is None]
    free_blocks = [blocks[i] for i in range(nb) if owner[i] is None]
    # free memory that is too small for any waiting process
    external = sum(f for f in free_blocks if f < min(unalloc)) if unalloc else 0
    used = sum(a["size"] for a in alloc if a["block"])
    return {
        "allocations": alloc,
        "blocks": [{"block": i + 1, "size": blocks[i],
                    "process": None if owner[i] is None else f"P{owner[i] + 1}",
                    "free": blocks[i] if owner[i] is None
                    else blocks[i] - processes[owner[i]]} for i in range(nb)],
        "allocated": len(alloc) - len(unalloc),
        "not_allocated": len(unalloc),
        "internal_frag": internal,
        "external_frag": external,
        "utilization": round(100 * used / sum(blocks), 2),
    }


def compare_all(blocks, processes):
    out = []
    for name, key in STRATEGIES.items():
        r = allocate(blocks, processes, key)
        out.append({"algorithm": name, "allocated": r["allocated"],
                    "internal": r["internal_frag"], "external": r["external_frag"],
                    "fragmentation": r["internal_frag"] + r["external_frag"],
                    "utilization": r["utilization"]})
    return out
