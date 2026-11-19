"""
OS CPU Scheduling Demonstration
Algorithms:
1. FCFS
2. SJF Non-Preemptive
3. SJF Preemptive (SRTF)
4. Round Robin

This is a safe educational simulation. It does not change real OS scheduling.
Run in Python IDLE using F5.
"""

import os
import csv
import json
from collections import deque
from datetime import datetime

PROCESSES = [
    {"pid": "P1", "arrival": 0, "burst": 7},
    {"pid": "P2", "arrival": 2, "burst": 4},
    {"pid": "P3", "arrival": 4, "burst": 1},
    {"pid": "P4", "arrival": 5, "burst": 4},
]

TIME_QUANTUM = 2


def calculate_metrics(processes, completion, first_start):
    rows = []
    for p in processes:
        pid = p["pid"]
        arrival = p["arrival"]
        burst = p["burst"]
        tat = completion[pid] - arrival
        wt = tat - burst
        rt = first_start[pid] - arrival
        rows.append({
            "process": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "completion_time": completion[pid],
            "turnaround_time": tat,
            "waiting_time": wt,
            "response_time": rt
        })

    count = len(rows)
    averages = {
        "average_waiting_time": round(sum(r["waiting_time"] for r in rows) / count, 2),
        "average_turnaround_time": round(sum(r["turnaround_time"] for r in rows) / count, 2),
        "average_response_time": round(sum(r["response_time"] for r in rows) / count, 2)
    }
    return rows, averages


def fcfs(processes):
    ordered = sorted(processes, key=lambda p: (p["arrival"], p["pid"]))
    time = 0
    completion = {}
    first_start = {}
    gantt = []

    for p in ordered:
        if time < p["arrival"]:
            gantt.append({"start": time, "end": p["arrival"], "process": "Idle"})
            time = p["arrival"]
        start = time
        first_start[p["pid"]] = start
        time += p["burst"]
        completion[p["pid"]] = time
        gantt.append({"start": start, "end": time, "process": p["pid"]})

    rows, averages = calculate_metrics(processes, completion, first_start)
    return {"gantt_chart": gantt, "process_metrics": rows, "averages": averages}


def sjf_non_preemptive(processes):
    time = 0
    remaining = {p["pid"]: p.copy() for p in processes}
    completion = {}
    first_start = {}
    gantt = []

    while remaining:
        ready = [p for p in remaining.values() if p["arrival"] <= time]
        if not ready:
            next_arrival = min(p["arrival"] for p in remaining.values())
            gantt.append({"start": time, "end": next_arrival, "process": "Idle"})
            time = next_arrival
            continue

        chosen = min(ready, key=lambda p: (p["burst"], p["arrival"], p["pid"]))
        pid = chosen["pid"]
        first_start[pid] = time
        start = time
        time += chosen["burst"]
        completion[pid] = time
        gantt.append({"start": start, "end": time, "process": pid})
        del remaining[pid]

    rows, averages = calculate_metrics(processes, completion, first_start)
    return {"gantt_chart": gantt, "process_metrics": rows, "averages": averages}


def sjf_preemptive(processes):
    remaining = {p["pid"]: p["burst"] for p in processes}
    completion = {}
    first_start = {}
    gantt = []
    time = 0
    total = sum(remaining.values())
    last_pid = None
    segment_start = 0

    while len(completion) < len(processes):
        ready = [
            p for p in processes
            if p["arrival"] <= time and remaining[p["pid"]] > 0
        ]

        if ready:
            chosen = min(ready, key=lambda p: (remaining[p["pid"]], p["arrival"], p["pid"]))
            pid = chosen["pid"]
            if pid not in first_start:
                first_start[pid] = time
        else:
            pid = "Idle"

        if pid != last_pid:
            if last_pid is not None:
                gantt.append({"start": segment_start, "end": time, "process": last_pid})
            segment_start = time
            last_pid = pid

        if pid == "Idle":
            time += 1
        else:
            remaining[pid] -= 1
            time += 1
            if remaining[pid] == 0:
                completion[pid] = time

    if last_pid is not None:
        gantt.append({"start": segment_start, "end": time, "process": last_pid})

    rows, averages = calculate_metrics(processes, completion, first_start)
    return {"gantt_chart": gantt, "process_metrics": rows, "averages": averages}


def round_robin(processes, quantum):
    ordered = sorted(processes, key=lambda p: (p["arrival"], p["pid"]))
    remaining = {p["pid"]: p["burst"] for p in processes}
    completion = {}
    first_start = {}
    ready = deque()
    gantt = []
    time = 0
    index = 0

    while len(completion) < len(processes):
        while index < len(ordered) and ordered[index]["arrival"] <= time:
            ready.append(ordered[index]["pid"])
            index += 1

        if not ready:
            next_arrival = ordered[index]["arrival"]
            gantt.append({"start": time, "end": next_arrival, "process": "Idle"})
            time = next_arrival
            continue

        pid = ready.popleft()
        if pid not in first_start:
            first_start[pid] = time

        start = time
        run_time = min(quantum, remaining[pid])
        time += run_time
        remaining[pid] -= run_time
        gantt.append({"start": start, "end": time, "process": pid})

        # Add processes that arrived during this time slice before re-queuing
        # the currently running process, following standard Round Robin order.
        while index < len(ordered) and ordered[index]["arrival"] <= time:
            ready.append(ordered[index]["pid"])
            index += 1

        if remaining[pid] == 0:
            completion[pid] = time
        else:
            ready.append(pid)

    rows, averages = calculate_metrics(processes, completion, first_start)
    return {"gantt_chart": gantt, "process_metrics": rows, "averages": averages}


def print_result(name, result):
    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)
    print("Gantt Chart:")
    print(" -> ".join(
        f'{item["process"]} [{item["start"]}-{item["end"]}]'
        for item in result["gantt_chart"]
    ))
    print("\nProcess Metrics:")
    print("PID | AT | BT | CT | TAT | WT | RT")
    for r in result["process_metrics"]:
        print(
            f'{r["process"]:>3} | {r["arrival_time"]:>2} | {r["burst_time"]:>2} | '
            f'{r["completion_time"]:>2} | {r["turnaround_time"]:>3} | '
            f'{r["waiting_time"]:>2} | {r["response_time"]:>2}'
        )
    print("\nAverages:", result["averages"])


def main():
    output_folder = "dt_ids_results"
    os.makedirs(output_folder, exist_ok=True)

    results = {
        "FCFS": fcfs(PROCESSES),
        "SJF_Non_Preemptive": sjf_non_preemptive(PROCESSES),
        "SJF_Preemptive_SRTF": sjf_preemptive(PROCESSES),
        "Round_Robin": round_robin(PROCESSES, TIME_QUANTUM)
    }

    for name, result in results.items():
        print_result(name, result)

    output = {
        "experiment": "CPU Scheduling Simulation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "note": "Educational simulation only; real OS scheduling is not modified.",
        "processes": PROCESSES,
        "round_robin_time_quantum": TIME_QUANTUM,
        "results": results
    }

    json_path = os.path.join(output_folder, "os_cpu_scheduling_observations.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    csv_path = os.path.join(output_folder, "os_cpu_scheduling_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "algorithm", "process", "arrival_time", "burst_time",
            "completion_time", "turnaround_time", "waiting_time", "response_time"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for algorithm, result in results.items():
            for row in result["process_metrics"]:
                writer.writerow({"algorithm": algorithm, **row})

    print("\n\nCPU scheduling experiment completed successfully.")
    print("Saved:", json_path)
    print("Saved:", csv_path)
    print("Folder:", os.path.abspath(output_folder))


if __name__ == "__main__":
    main()
