"""
OS/Runtime Layer - Process and Thread Demonstration
Safe, lightweight demonstration for the Digital Twin IDS project.

Run this file from Python IDLE with F5.
It creates one short-lived child process and two lightweight threads.
No real industrial equipment or network is accessed.
"""

from pathlib import Path
import csv
import json
import os
import subprocess
import sys
import threading
import time

try:
    import psutil
except ImportError:
    psutil = None

OUTPUT_DIR = Path("dt_ids_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def child_process_task():
    """Code executed by the short-lived child process."""
    result = {
        "message": "Child process completed its safe demo task.",
        "child_pid": os.getpid(),
        "parent_pid": os.getppid()
    }
    print(json.dumps(result))


def thread_task(thread_number, results, lock):
    """Small task executed by each thread."""
    start = time.perf_counter()
    time.sleep(1.0)  # Small wait to make concurrent thread activity observable.
    elapsed = time.perf_counter() - start

    with lock:
        results.append({
            "thread_name": threading.current_thread().name,
            "thread_number": thread_number,
            "thread_id": threading.get_ident(),
            "task_time_seconds": round(elapsed, 4)
        })


def run_os_runtime_demo():
    print("=" * 60)
    print("OS/RUNTIME EXPERIMENT: PROCESSES AND THREADS")
    print("=" * 60)

    parent_pid = os.getpid()
    parent_process = psutil.Process(parent_pid) if psutil else None

    print("\n1. Main Python process")
    print("Parent process ID:", parent_pid)
    print("Parent process ID (reported by OS):", os.getppid())

    # Start one child process by running this same script in worker mode.
    print("\n2. Starting one child process...")
    child_start = time.perf_counter()
    child_run = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--child"],
        capture_output=True,
        text=True,
        timeout=15
    )
    child_elapsed = time.perf_counter() - child_start

    if child_run.returncode != 0:
        print("Child process failed:")
        print(child_run.stderr)
        raise RuntimeError("Child process did not complete successfully.")

    child_info = json.loads(child_run.stdout.strip())
    print("Child process ID:", child_info["child_pid"])
    print("Child process parent ID:", child_info["parent_pid"])
    print("Child process message:", child_info["message"])

    # Start two threads inside the main process.
    print("\n3. Starting two threads...")
    thread_results = []
    results_lock = threading.Lock()

    threads = [
        threading.Thread(
            target=thread_task,
            args=(i + 1, thread_results, results_lock),
            name=f"Demo-Thread-{i + 1}"
        )
        for i in range(2)
    ]

    thread_start = time.perf_counter()
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    thread_elapsed = time.perf_counter() - thread_start

    for result in thread_results:
        print(
            result["thread_name"],
            "| Thread ID:", result["thread_id"],
            "| Task time:", result["task_time_seconds"], "seconds"
        )

    # Capture a simple OS resource snapshot.
    if psutil:
        process = psutil.Process(os.getpid())
        resource_data = {
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "system_memory_percent": psutil.virtual_memory().percent,
            "python_process_memory_mb": round(
                process.memory_info().rss / (1024 ** 2), 2
            ),
            "active_threads_after_demo": process.num_threads()
        }
    else:
        resource_data = {
            "note": "psutil is not installed; resource snapshot unavailable."
        }

    report = {
        "experiment": "OS/Runtime - Process and Thread Demonstration",
        "main_process_id": parent_pid,
        "child_process_id": child_info["child_pid"],
        "child_process_parent_id": child_info["parent_pid"],
        "child_process_message": child_info["message"],
        "child_process_elapsed_seconds": round(child_elapsed, 4),
        "threads_created": len(thread_results),
        "thread_details": thread_results,
        "threads_elapsed_seconds": round(thread_elapsed, 4),
        "resource_observations": resource_data,
        "note": (
            "A child process was launched and two threads were run inside "
            "the main Python process. The child process communicated its "
            "result to the parent through captured standard output."
        )
    }

    json_path = OUTPUT_DIR / "os_process_thread_observations.json"
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    csv_path = OUTPUT_DIR / "os_process_thread_observations.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Component", "Identifier", "Observation"])
        writer.writerow(["Main process", "PID", parent_pid])
        writer.writerow(["Child process", "PID", child_info["child_pid"]])
        writer.writerow(["Child process", "Parent PID", child_info["parent_pid"]])
        for item in thread_results:
            writer.writerow([
                "Thread",
                item["thread_name"],
                f"Thread ID={item['thread_id']}; "
                f"Task time={item['task_time_seconds']} seconds"
            ])

    print("\n4. OS resource observations")
    print(json.dumps(resource_data, indent=2))
    print("\nSaved files:")
    print(json_path.resolve())
    print(csv_path.resolve())
    print("\nExperiment completed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child_process_task()
    else:
        run_os_runtime_demo()
