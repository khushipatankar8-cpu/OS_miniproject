from functools import wraps

from flask import Flask, jsonify, render_template, request

from algorithms import cpu_scheduling, deadlock, memory_management, page_replacement

app = Flask(__name__)


def api(fn):
    """Return JSON and turn validation errors into HTTP 400."""
    @wraps(fn)
    def wrapper():
        data = request.get_json(force=True, silent=True) or {}
        try:
            return jsonify(fn(data))
        except (ValueError, KeyError, TypeError) as e:
            return jsonify(error=str(e) or "Invalid input."), 400
    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cpu")
def cpu():
    return render_template("cpu.html")


@app.route("/memory")
def memory():
    return render_template("memory.html")


@app.route("/pages")
def pages():
    return render_template("page_replacement.html")


@app.route("/deadlock")
def deadlock_page():
    return render_template("deadlock.html")


@app.post("/api/cpu")
@api
def api_cpu(d):
    q = d.get("quantum", 2)
    return {
        "result": cpu_scheduling.simulate(d.get("algorithm"), d.get("processes", []), q),
        "comparison": cpu_scheduling.compare_all(d.get("processes", []), q),
    }


@app.post("/api/memory")
@api
def api_memory(d):
    blocks, procs = d.get("blocks", []), d.get("processes", [])
    key = memory_management.STRATEGIES.get(d.get("algorithm"))
    if key is None:
        raise ValueError("Unknown allocation algorithm.")
    return {"result": memory_management.allocate(blocks, procs, key),
            "comparison": memory_management.compare_all(blocks, procs)}


@app.post("/api/pages")
@api
def api_pages(d):
    return page_replacement.run_all(d.get("refs", []), int(d.get("frames", 0)))


@app.post("/api/deadlock")
@api
def api_deadlock(d):
    alloc, other, avail = d.get("allocation"), d.get("matrix2"), d.get("available")
    if d.get("mode") == "detection":
        return {"mode": "detection", "result": deadlock.detect(alloc, other, avail)}
    out = {"mode": "banker", "result": deadlock.bankers(alloc, other, avail)}
    req = d.get("request")
    if req:
        out["request"] = deadlock.resource_request(
            alloc, other, avail, int(d.get("request_pid", 0)), req)
    return out


if __name__ == "__main__":
    app.run(debug=True)
