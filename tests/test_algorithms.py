import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import cpu_scheduling as cpu, memory_management as mem
from algorithms import page_replacement as pg, deadlock as dl
from app import app

P = [{"pid": "P1", "at": 0, "bt": 5, "pr": 2}, {"pid": "P2", "at": 1, "bt": 3, "pr": 1},
     {"pid": "P3", "at": 2, "bt": 8, "pr": 3}, {"pid": "P4", "at": 3, "bt": 2, "pr": 2}]


def ct(res):
    return {r["pid"]: r["ct"] for r in res["processes"]}


class CPUTests(unittest.TestCase):
    def test_fcfs(self):
        r = cpu.simulate("FCFS", P)
        self.assertEqual(ct(r), {"P1": 5, "P2": 8, "P3": 16, "P4": 18})
        self.assertEqual(r["avg_wt"], 5.75)

    def test_sjf(self):
        self.assertEqual(ct(cpu.simulate("SJF", P)), {"P1": 5, "P2": 10, "P3": 18, "P4": 7})

    def test_srtf(self):
        self.assertEqual(ct(cpu.simulate("SRTF", P)), {"P1": 10, "P2": 4, "P3": 18, "P4": 6})

    def test_priority(self):
        self.assertEqual(ct(cpu.simulate("Priority", P)), {"P1": 5, "P2": 8, "P3": 18, "P4": 10})

    def test_round_robin(self):
        self.assertEqual(ct(cpu.simulate("Round Robin", P, 2)), {"P1": 14, "P2": 11, "P3": 18, "P4": 10})

    def test_all_arrive_at_zero(self):
        procs = [{"pid": f"P{i}", "at": 0, "bt": 4, "pr": 1} for i in range(3)]
        self.assertEqual(cpu.simulate("FCFS", procs)["avg_wt"], 4.0)

    def test_single_process(self):
        r = cpu.simulate("Round Robin", [{"pid": "A", "at": 0, "bt": 7}], 3)
        self.assertEqual((r["avg_wt"], r["avg_tat"]), (0, 7))

    def test_idle_gap(self):
        r = cpu.simulate("FCFS", [{"pid": "A", "at": 3, "bt": 2}])
        self.assertEqual(r["gantt"][0]["pid"], "Idle")
        self.assertEqual(r["processes"][0]["rt"], 0)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            cpu.simulate("FCFS", [{"pid": "A", "at": 0, "bt": 0}])


class MemoryTests(unittest.TestCase):
    B, S = [100, 500, 200, 300, 600], [212, 417, 112, 426]

    def blocks(self, s):
        return [a["block"] for a in mem.allocate(self.B, self.S, s)["allocations"]]

    def test_first(self): self.assertEqual(self.blocks("first"), [2, 5, 3, None])
    def test_best(self): self.assertEqual(self.blocks("best"), [4, 2, 3, 5])
    def test_worst(self): self.assertEqual(self.blocks("worst"), [5, 2, 4, None])

    def test_exact_fit(self):
        r = mem.allocate([100], [100], "first")
        self.assertEqual((r["internal_frag"], r["utilization"]), (0, 100.0))


class PagingTests(unittest.TestCase):
    REF = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

    def test_classic(self):
        r = pg.run_all(self.REF, 3)
        self.assertEqual((r["FIFO"]["faults"], r["LRU"]["faults"], r["Optimal"]["faults"]), (15, 12, 9))

    def test_repeated_pages(self):
        self.assertEqual(pg.fifo([1, 1, 1], 2)["faults"], 1)


class DeadlockTests(unittest.TestCase):
    A = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
    M = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]

    def test_safe(self):
        r = dl.bankers(self.A, self.M, [3, 3, 2])
        self.assertTrue(r["safe"])
        self.assertEqual(r["sequence"], ["P1", "P3", "P4", "P0", "P2"])

    def test_unsafe(self):
        self.assertFalse(dl.bankers(self.A, self.M, [0, 0, 0])["safe"])

    def test_request(self):
        self.assertTrue(dl.resource_request(self.A, self.M, [3, 3, 2], 1, [1, 0, 2])["granted"])
        self.assertFalse(dl.resource_request(self.A, self.M, [3, 3, 2], 1, [5, 0, 0])["granted"])

    def test_detection(self):
        a = [[0, 1, 0], [2, 0, 0], [3, 0, 3], [2, 1, 1], [0, 0, 2]]
        self.assertFalse(dl.detect(a, [[0, 0, 0], [2, 0, 2], [0, 0, 0], [1, 0, 0], [0, 0, 2]], [0, 0, 0])["deadlock"])
        r = dl.detect(a, [[0, 0, 0], [2, 0, 2], [0, 0, 1], [1, 0, 0], [0, 0, 2]], [0, 0, 0])
        self.assertEqual(r["deadlocked"], ["P1", "P2", "P3", "P4"])


class APITests(unittest.TestCase):
    def test_routes(self):
        c = app.test_client()
        for url in ["/", "/cpu", "/memory", "/pages", "/deadlock"]:
            self.assertEqual(c.get(url).status_code, 200)
        r = c.post("/api/cpu", json={"algorithm": "FCFS", "processes": P})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(c.post("/api/cpu", json={"algorithm": "FCFS", "processes": []}).status_code, 400)
        self.assertEqual(c.post("/api/pages", json={"refs": [1, 2, 3], "frames": 2}).status_code, 200)
        self.assertEqual(c.post("/api/memory", json={"algorithm": "Best Fit", "blocks": [5], "processes": [3]}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
