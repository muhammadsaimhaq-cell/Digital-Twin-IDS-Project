"""
IPC Demonstration: Parent-Child Communication using a Pipe
For the Digital Twin IDS OS/Runtime experiment.

How to run in Python IDLE:
1. Save this file.
2. Open it in Python IDLE.
3. Press F5 (Run > Run Module).
4. Check the dt_ids_results folder created beside this file.

This is a safe, local demonstration. It does not connect to any external system.
"""

import multiprocessing
import json
import csv
import os
import time
from datetime import datetime


def child_process_task(connection):
    """Child sends a simulated sensor-status message to the parent."""
    message = {
        "source_process": "child_process",
        "event": "simulated_sensor_status",
        "water_level_percent": 48.5,
        "pump_status": "ON",
        "valve_status": "OFF",
        "label": "normal"
    }

    time.sleep(0.5)  # Simulate a small amount of child-process work.
    connection.send(message)
    connection.close()


def run_ipc_demo():
    start_time = time.time()
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Create a one-way pipe: first endpoint receives, second sends.
    receive_connection, send_connection = multiprocessing.Pipe(duplex=False)

    child = multiprocessing.Process(
        target=child_process_task,
        args=(send_connection,),
        name="IPC-Child-Process"
    )

    child.start()
    send_connection.close()

    # Parent receives the message sent by the child process.
    received_message = receive_connection.recv()
    receive_connection.close()

    child.join()
    elapsed = round(time.time() - start_time, 4)

    results = {
        "experiment": "Inter-Process Communication (IPC) using Pipe",
        "timestamp": timestamp,
        "communication_method": "multiprocessing.Pipe",
        "parent_process_id": os.getpid(),
        "child_process_id": child.pid,
        "child_exit_code": child.exitcode,
        "message_received_by_parent": received_message,
        "communication_successful": child.exitcode == 0,
        "total_elapsed_time_seconds": elapsed,
        "observation": (
            "The child process sent a simulated sensor-status message "
            "to the parent process through a pipe."
        )
    }

    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "dt_ids_results")
    os.makedirs(output_folder, exist_ok=True)

    json_path = os.path.join(output_folder, "os_ipc_pipe_observations.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    csv_path = os.path.join(output_folder, "os_ipc_pipe_observations.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Communication method", "multiprocessing.Pipe"])
        writer.writerow(["Parent process ID", os.getpid()])
        writer.writerow(["Child process ID", child.pid])
        writer.writerow(["Child exit code", child.exitcode])
        writer.writerow(["Message received", json.dumps(received_message)])
        writer.writerow(["Communication successful", child.exitcode == 0])
        writer.writerow(["Elapsed time (seconds)", elapsed])

    print("\n===== IPC PIPE EXPERIMENT =====")
    print("Communication method: multiprocessing.Pipe")
    print("Parent process ID:", os.getpid())
    print("Child process ID:", child.pid)
    print("Message received by parent:")
    print(received_message)
    print("Child exit code:", child.exitcode)
    print("Communication successful:", child.exitcode == 0)
    print("Elapsed time:", elapsed, "seconds")
    print("\nFiles saved:")
    print(json_path)
    print(csv_path)
    print("\nIPC experiment completed.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_ipc_demo()
