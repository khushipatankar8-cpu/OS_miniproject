# OS Resource Management & Scheduling Simulator

Web-based simulator for core Operating System algorithms.
Stack: Flask (Python) backend · HTML/CSS/JavaScript frontend · Chart.js graphs.

## Modules
| Module | Algorithms |
|---|---|
| CPU Scheduling | FCFS, SJF, SRTF, Priority, Round Robin (Gantt chart, CT/TAT/WT/RT, averages, comparison graph) |
| Memory Management | First Fit, Best Fit, Worst Fit, Next Fit (internal/external fragmentation, utilization) |
| Page Replacement | FIFO, LRU, Optimal (frame-by-frame table, faults/hits, comparison graph) |
| Deadlock | Banker's Algorithm (safe sequence, resource request), Deadlock Detection |

## Run (Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Open http://127.0.0.1:5000

(Charts load Chart.js from a CDN, so an internet connection is needed for graphs.)

## Run tests
```bash
python3 -m unittest discover tests -v
```

## Structure
```
app.py                  Flask routes + JSON API
algorithms/             cpu_scheduling.py, memory_management.py,
                        page_replacement.py, deadlock.py
templates/              base.html + one page per module
static/css, static/js   styling and shared helpers
tests/                  unit tests for every algorithm
```
Notes: lower priority number = higher priority; memory uses fixed partitions (one process per block).
