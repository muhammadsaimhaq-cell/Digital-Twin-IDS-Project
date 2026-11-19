# Digital Twin-Based Intrusion Detection for Industrial Control Systems

A beginner-friendly academic prototype that combines a simulated
water-tank Digital Twin, synthetic anomaly detection, machine-learning
classifiers, and operating-system/runtime demonstrations.

> **Safety scope:** This project uses a software-only water-tank
> simulation. All abnormal events are synthetic and remain inside the
> program. It does not connect to real industrial equipment, send
> network traffic, or perform real attacks.

## 1. Project objectives

-   Simulate normal water-tank operation using a simple process model.
-   Generate labeled synthetic records for normal operation and three
    anomaly categories.
-   Compare three supervised classifiers: Logistic Regression, Decision
    Tree, and K-Nearest Neighbors (KNN).
-   Compare process-only features with combined process and cyber/system
    features.
-   Evaluate model robustness under controlled sensor-noise settings.
-   Demonstrate selected OS concepts: processes, threads, inter-process
    communication (IPC), CPU scheduling, and resource observations.

## 2. Machine-learning models

The project uses these three models:

1.  Logistic Regression
2.  Decision Tree
3.  K-Nearest Neighbors (KNN)

Random Forest is not part of the selected final model set.

## 3. Project files

Keep the Python files in the same project folder. Use the following
names:

  -------------------------------------------------------------------------------
  File                                        Purpose
  ------------------------------------------- -----------------------------------
  `Digital_Twin_IDS_LR_DT_KNN.py`             Main Digital Twin, synthetic
                                              dataset generation, E1
                                              normal-operation experiment, model
                                              training, evaluation, confusion
                                              matrices, and resource observations

  `Run_Feature_And_Robustness_LR_DT_KNN.py`   Feature-group comparison and
                                              sensor-noise robustness experiments

  `OS_Runtime_Process_Thread_Demo.py`         Demonstrates a parent process, a
                                              child process, and threads

  `OS_Runtime_IPC_Pipe_Demo.py`               Demonstrates local parent-child
                                              communication using a
                                              multiprocessing Pipe

  `OS_CPU_Scheduling_Demo.py`                 Educational simulations of FCFS,
                                              SJF non-preemptive, SJF preemptive
                                              (SRTF), and Round Robin

  `OS_Resource_Utilization_Demo.py`           Measures selected system and
                                              Python-process resource
                                              observations during a simulated
                                              workload
  -------------------------------------------------------------------------------

**Important filename note:** The feature/robustness script imports
`Digital_Twin_IDS_LR_DT_KNN.py`. Therefore, the main script must have
that exact filename and must be in the same folder as the
feature/robustness script. If your downloaded main file is named
`Digital_Twin_IDS_LR_DT_KNN_E1_Added.py`, rename a copy to
`Digital_Twin_IDS_LR_DT_KNN.py` before running the feature/robustness
script.

## 4. Requirements

-   Windows, macOS, or Linux with Python 3.9 or newer recommended.
-   Python IDLE (included with many Python installations) or another
    Python editor.
-   Internet access only for installing the Python packages, if they are
    not already installed.

Required Python packages:

-   `numpy`
-   `pandas`
-   `scikit-learn`
-   `matplotlib`
-   `psutil`

## 5. Installation

Open **Command Prompt** on Windows (or a terminal on macOS/Linux) and
run:

``` bash
py -m pip install numpy pandas scikit-learn matplotlib psutil
```

If the `py` command is unavailable, try:

``` bash
python -m pip install numpy pandas scikit-learn matplotlib psutil
```

The `psutil` package is used for CPU, memory, and process observations.
The main script can still run without it, but some resource fields will
be unavailable.

## 6. Running the project in Python IDLE

1.  Place all six `.py` files in one project folder.
2.  Open Python IDLE.
3.  Select **File \> Open** and open the Python file you want to run.
4.  Select **Run \> Run Module** or press **F5**.
5.  When the program finishes, open the `dt_ids_results` folder created
    by the script.
6.  Repeat for the other experiment scripts.

Recommended run order:

1.  `Digital_Twin_IDS_LR_DT_KNN.py`
2.  `Run_Feature_And_Robustness_LR_DT_KNN.py`
3.  `OS_Runtime_Process_Thread_Demo.py`
4.  `OS_Runtime_IPC_Pipe_Demo.py`
5.  `OS_CPU_Scheduling_Demo.py`
6.  `OS_Resource_Utilization_Demo.py`

Run the main script before the feature/robustness script because the
latter imports the main script's data-generation function.

## 7. Experiments

  -----------------------------------------------------------------------
  Experiment                          Description
  ----------------------------------- -----------------------------------
  E1 - Normal operation               Generates a separate normal-only
                                      dataset and records water-level
                                      behavior and selected resource
                                      observations

  E2 - Synthetic anomaly generation   Generates labeled synthetic
                                      measurement-manipulation,
                                      command-anomaly, and network-delay
                                      events

  E3 - Model comparison               Trains and evaluates Logistic
                                      Regression, Decision Tree, and KNN
                                      using a held-out test set

  E4 - Feature comparison             Compares process-only features
                                      against combined process and
                                      cyber/system features

  E5 - OS/resource study              Records selected CPU, memory,
                                      thread, process, execution-time,
                                      and scheduling/IPC demonstration
                                      evidence

  E6 - Robustness                     Tests model performance when
                                      controlled noise is added to the
                                      sensor-water-level test feature
  -----------------------------------------------------------------------

The CPU scheduling and IPC programs are educational software
demonstrations. They do not change the computer's real OS scheduler or
communicate with industrial equipment.

## 8. Dataset fields and labels

The main generated dataset is `digital_twin_dataset.csv`. Its columns
are:

  -----------------------------------------------------------------------
  Column                              Meaning
  ----------------------------------- -----------------------------------
  `timestamp`                         Sequential simulation record index

  `true_water_level`                  Simulated underlying tank water
                                      level (%)

  `sensor_water_level`                Simulated sensor reading (%)

  `pump_state`                        Simulated pump state (1 = ON, 0 =
                                      OFF)

  `valve_state`                       Simulated valve state (1 = ON, 0 =
                                      OFF)

  `command_mismatch`                  Indicator for a simulated
                                      unexpected actuator command (1 =
                                      mismatch, 0 = no mismatch)

  `network_delay_ms`                  Simulated communication delay in
                                      milliseconds; no real packets are
                                      sent

  `water_level_change`                Change in simulated water level for
                                      the record

  `attack_type`                       Category: `normal`,
                                      `measurement_manipulation`,
                                      `command_anomaly`, or
                                      `network_delay`

  `label`                             Target class: 0 = normal, 1 =
                                      simulated anomaly
  -----------------------------------------------------------------------

The E1 dataset, `normal_operation_dataset.csv`, uses the same general
process fields but contains normal records only (`label = 0`).

## 9. Output files

The scripts create a folder named `dt_ids_results` in the relevant
working/output location. Depending on which experiments have been run,
it may contain:

### Main experiment

-   `digital_twin_dataset.csv`
-   `normal_operation_dataset.csv`
-   `e1_normal_operation_summary.json`
-   `normal_operation_water_level.png`
-   `model_results.csv`
-   `model_comparison.png`
-   `confusion_matrix_logistic_regression.png`
-   `confusion_matrix_decision_tree.png`
-   `confusion_matrix_k-nearest_neighbors_(knn).png` (the exact filename
    is generated from the model name)
-   `os_resource_observations.json`
-   `run_summary.json`

### Feature and robustness experiments

-   `feature_comparison_results.csv`
-   `robustness_results.csv`
-   `feature_comparison.png`
-   `robustness_comparison.png`

### OS/runtime demonstrations

-   `os_process_thread_observations.json` and `.csv`
-   `os_ipc_pipe_observations.json` and `.csv`
-   `os_cpu_scheduling_observations.json`
-   `os_cpu_scheduling_metrics.csv`
-   `os_resource_utilization_observations.json` and `.csv`

The output folder may also contain plots and other evidence generated by
the scripts. Keep the CSV, JSON, and PNG files as experiment evidence
for the report.

## 10. Reproducibility notes

-   The main dataset generator uses a fixed random seed (`42`) to make
    the synthetic data generation repeatable.
-   The feature/robustness experiment uses the same seed for its
    train/test split and controlled noise generation.
-   Resource readings such as CPU and memory vary between computers and
    between runs. Record the actual values produced by your own run.
-   Small timing differences are expected across machines.
-   Model scores describe performance on this synthetic dataset. They
    should not be interpreted as proof of performance on a real
    industrial control system. Independent scenarios or approved public
    datasets would be needed for stronger external validation.

## 11. Limitations

-   The water-tank process is a simplified software model, not a
    physically validated plant.
-   The anomaly categories are simulated labels, not observations of
    real attacks.
-   CPU, memory, and thread readings are observations from the host
    computer. Point-in-time CPU readings are not continuous profiling.
-   CPU scheduling algorithms are implemented as educational
    simulations; the project does not modify OS-level scheduling policy.
-   IPC is demonstrated locally using Python multiprocessing.
-   The project is a course prototype and is not intended for deployment
    as a production industrial intrusion-detection system.

## 12. Suggested repository structure

``` text
Digital-Twin-IDS/
|
|-- Digital_Twin_IDS_LR_DT_KNN.py
|-- Run_Feature_And_Robustness_LR_DT_KNN.py
|-- OS_Runtime_Process_Thread_Demo.py
|-- OS_Runtime_IPC_Pipe_Demo.py
|-- OS_CPU_Scheduling_Demo.py
|-- OS_Resource_Utilization_Demo.py
|-- README.md
|
|-- dt_ids_results/
    |-- CSV datasets and metrics
    |-- JSON experiment observations
    |-- PNG plots and confusion matrices
```

For GitHub, include the source files and README. You may include a
small, selected set of result files as evidence; avoid committing
unnecessary temporary files or duplicate outputs.
