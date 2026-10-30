"""Page replacement: FIFO, LRU, Optimal."""


def _validate(refs, frames):
    if not refs:
        raise ValueError("Enter a reference string.")
    if frames < 1:
        raise ValueError("Number of frames must be at least 1.")


def _summary(steps, n):
    faults = sum(1 for s in steps if s["fault"])
    return {"steps": steps, "faults": faults, "hits": n - faults,
            "hit_ratio": round(100 * (n - faults) / n, 2)}


def fifo(refs, nframes):
    _validate(refs, nframes)
    frames, ptr, steps = [None] * nframes, 0, []
    for page in refs:
        fault = page not in frames
        if fault:
            frames[ptr] = page
            ptr = (ptr + 1) % nframes
        steps.append({"page": page, "frames": frames[:], "fault": fault})
    return _summary(steps, len(refs))


def lru(refs, nframes):
    _validate(refs, nframes)
    frames, last, steps = [None] * nframes, {}, []
    for t, page in enumerate(refs):
        fault = page not in frames
        if fault:
            if None in frames:
                frames[frames.index(None)] = page
            else:
                victim = min(frames, key=lambda p: last[p])
                frames[frames.index(victim)] = page
        last[page] = t
        steps.append({"page": page, "frames": frames[:], "fault": fault})
    return _summary(steps, len(refs))


def optimal(refs, nframes):
    _validate(refs, nframes)
    frames, steps = [None] * nframes, []
    for t, page in enumerate(refs):
        fault = page not in frames
        if fault:
            if None in frames:
                frames[frames.index(None)] = page
            else:
                def next_use(p):
                    try:
                        return refs.index(p, t + 1)
                    except ValueError:
                        return float("inf")
                victim = max(frames, key=next_use)
                frames[frames.index(victim)] = page
        steps.append({"page": page, "frames": frames[:], "fault": fault})
    return _summary(steps, len(refs))


ALGORITHMS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal}


def run_all(refs, nframes):
    return {name: fn(refs, nframes) for name, fn in ALGORITHMS.items()}
