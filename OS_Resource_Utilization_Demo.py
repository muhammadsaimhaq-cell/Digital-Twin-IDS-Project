"""
OS Resource Utilization Experiment
Measures CPU, RAM, Python process memory, thread count and execution time.
Safe educational workload only. Does not stress or modify the operating system.

Run using Python IDLE: Open this file and press F5.
Requires psutil (already used in the project environment).
"""

import os
import csv
import json
import time
import threading
from datetime import datetime

try:
    import psutil
except ImportError:
    print("ERROR: psutil is not installed.")
    print("Install psutil using IDLE: open Shell and run: pip install psutil")
    input("Press Enter to close...")
    raise SystemExit

PROCESS = psutil.Process(os.getpid())


def get_resource_snapshot():
    # A short CPU sampling interval gives a more useful system CPU reading.
    system_cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    process_memory = PROCESS.memory_info().rss / (1024 * 1024)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "system_cpu_percent": system_cpu,
        "system_ram_percent": memory.percent,
        "system_ram_used_mb": round(memory.used / (1024 * 1024), 2),
        "python_process_memory_mb": round(process_memory, 2),
        "python_process_threads": PROCESS.num_threads()
    }


def simulated_tank_workload(number_of_steps=300000):
    """
    Small deterministic digital-twin-style calculation.
    No real devices, networks, or industrial equipment are accessed.
    """
    water_level = 50.0
    total = 0.0

    for step in range(number_of_steps):
        inflow = 0.08 if step % 3 == 0 else 0.04
        outflow = 0.03 if step % 5 == 0 else 0.02
        water_level = water_level + inflow - outflow

        if water_level > 80:
            water_level = 80.0
        elif water_level < 20:
            water_level = 20.0

        total += water_level

    return {
        "simulation_steps": number_of_steps,
        "final_simulated_water_level_percent": round(water_level, 3),
        "average_calculated_level": round(total / number_of_steps, 3)
    }


def main():
    output_folder = "dt_ids_results"
    os.makedirs(output_folder, exist_ok=True)

    print("=" * 60)
    print("OS RESOURCE UTILIZATION EXPERIMENT")
    print("=" * 60)

    print("\nTaking BEFORE resource snapshot...")
    before = get_resource_snapshot()

    print("Running safe Digital Twin calculation workload...")
    start_time = time.perf_counter()
    workload_result = simulated_tank_workload()
    execution_time = time.perf_counter() - start_time

    print("Taking AFTER resource snapshot...")
    after = get_resource_snapshot()

    observations = {
        "experiment": "OS Resource Utilization Analysis",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "note": (
            "Measurements are machine- and run-specific snapshots. "
            "The workload is a safe software simulation only."
        ),
        "before_workload": before,
        "after_workload": after,
        "execution_time_seconds": round(execution_time, 6),
        "workload_result": workload_result
    }

    json_path = os.path.join(
        output_folder, "os_resource_utilization_observations.json"
    )
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(observations, file, indent=4)

    csv_path = os.path.join(
        output_folder, "os_resource_utilization_observations.csv"
    )
    fields = [
        "stage", "timestamp", "system_cpu_percent",
        "system_ram_percent", "system_ram_used_mb",
        "python_process_memory_mb", "python_process_threads"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerow({"stage": "before", **before})
        writer.writerow({"stage": "after", **after})

    print("\n" + "-" * 60)
    print("BEFORE WORKLOAD")
    for key, value in before.items():
        print(f"{key}: {value}")

    print("\nAFTER WORKLOAD")
    for key, value in after.items():
        print(f"{key}: {value}")

    print("\nExecution time:", round(execution_time, 6), "seconds")
    print("Workload result:", workload_result)
    print("\nExperiment completed successfully.")
    print("Saved:", json_path)
    print("Saved:", csv_path)
    print("Output folder:", os.path.abspath(output_folder))


if __name__ == "__main__":
    main()
