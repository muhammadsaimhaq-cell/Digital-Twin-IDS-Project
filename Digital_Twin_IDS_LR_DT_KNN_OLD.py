"""
Digital Twin-Based Intrusion Detection for Industrial Control Systems
Beginner-friendly prototype for the OS + AI/ML assignment.

Run:
    pip install numpy pandas scikit-learn matplotlib psutil
    python digital_twin_ids.py

The program simulates a water tank. All attack events are synthetic and stay
inside this program; no real network or industrial equipment is contacted.
Outputs are saved in a folder named dt_ids_results.
"""

from pathlib import Path
import json
import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, ConfusionMatrixDisplay
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

try:
    import psutil
except ImportError:
    psutil = None


OUTPUT_DIR = Path("dt_ids_results")
OUTPUT_DIR.mkdir(exist_ok=True)
RANDOM_SEED = 42


def generate_digital_twin_data(number_of_samples=3000):
    """Create synthetic normal and abnormal water-tank process readings."""
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []
    water_level = 50.0

    attack_types = ["normal", "measurement_manipulation",
                    "command_anomaly", "network_delay"]

    for i in range(number_of_samples):
        # A simple simulated tank: pump adds water; valve releases water.
        pump_state = int(water_level < 45)
        valve_state = int(water_level > 70)
        change = (pump_state * rng.uniform(0.4, 1.4)
                  - valve_state * rng.uniform(0.3, 1.0)
                  + rng.normal(0, 0.25))
        water_level = float(np.clip(water_level + change, 5, 95))

        true_level = water_level
        sensor_level = true_level + rng.normal(0, 0.8)
        network_delay_ms = max(1.0, rng.normal(20, 5))
        command_mismatch = 0
        attack_type = "normal"

        # Approximately 25% of records are simulated anomalies.
        event = rng.random()
        if event < 0.09:
            # Simulated sensor reading manipulation (no real sensor involved).
            attack_type = "measurement_manipulation"
            sensor_level = float(np.clip(
                sensor_level + rng.choice([-1, 1]) * rng.uniform(12, 30), 0, 100
            ))
        elif event < 0.17:
            # Simulated unexpected actuator command.
            attack_type = "command_anomaly"
            command_mismatch = 1
            pump_state = 1 - pump_state
            valve_state = int(rng.random() < 0.5)
        elif event < 0.25:
            # Simulated communication delay; no packets are sent.
            attack_type = "network_delay"
            network_delay_ms = float(rng.uniform(100, 400))

        rows.append({
            "timestamp": i,
            "true_water_level": round(true_level, 3),
            "sensor_water_level": round(sensor_level, 3),
            "pump_state": pump_state,
            "valve_state": valve_state,
            "command_mismatch": command_mismatch,
            "network_delay_ms": round(network_delay_ms, 3),
            "water_level_change": round(change, 3),
            "attack_type": attack_type,
            "label": int(attack_type != "normal")
        })

    return pd.DataFrame(rows)


def get_system_resources():
    """Collect OS resource readings when psutil is installed."""
    if psutil is None:
        return {
            "cpu_percent": None,
            "memory_percent": None,
            "note": "Install psutil to collect CPU and memory readings."
        }

    process = psutil.Process(os.getpid())
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent,
        "process_memory_mb": round(process.memory_info().rss / (1024 ** 2), 2),
        "process_threads": process.num_threads()
    }


def main():
    print("=" * 65)
    print("DIGITAL TWIN-BASED INTRUSION DETECTION SYSTEM")
    print("=" * 65)

    # Remove an obsolete plot from earlier Random Forest versions, if present.
    for old_plot in OUTPUT_DIR.glob("confusion_matrix_random_forest*.png"):
        old_plot.unlink()

    # Step 1: Generate and save the simulated dataset.
    data = generate_digital_twin_data()
    csv_path = OUTPUT_DIR / "digital_twin_dataset.csv"
    data.to_csv(csv_path, index=False)

    print(f"\n1. Dataset generated: {len(data)} records")
    print(data["attack_type"].value_counts().to_string())
    print(f"Dataset saved to: {csv_path.resolve()}")

    # Step 2: Select features and target label.
    feature_columns = [
        "true_water_level", "sensor_water_level", "pump_state",
        "valve_state", "command_mismatch", "network_delay_ms",
        "water_level_change"
    ]
    X = data[feature_columns]
    y = data["label"]  # 0 = Normal, 1 = Simulated anomaly

    # Step 3: Split data before training to keep a held-out test set.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )

    # Step 4: Train three different supervised ML classifiers.
    models = {
        "Logistic Regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8, random_state=RANDOM_SEED
        ),
        "K-Nearest Neighbors (KNN)": make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=5)
        )
    }

    results = []
    resource_before = get_system_resources()

    for model_name, model in models.items():
        print(f"\n2. Training {model_name}...")
        start_train = time.perf_counter()
        model.fit(X_train, y_train)
        train_seconds = time.perf_counter() - start_train

        start_predict = time.perf_counter()
        predictions = model.predict(X_test)
        predict_seconds = time.perf_counter() - start_predict
        latency_ms_per_sample = (predict_seconds / len(X_test)) * 1000

        metrics = {
            "model": model_name,
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "f1_score": f1_score(y_test, predictions, zero_division=0),
            "training_time_seconds": train_seconds,
            "inference_time_ms_per_sample": latency_ms_per_sample
        }
        results.append(metrics)

        # Save a separate confusion-matrix plot for each classifier.
        cm = confusion_matrix(y_test, predictions, labels=[0, 1])
        display = ConfusionMatrixDisplay(
            confusion_matrix=cm, display_labels=["Normal", "Anomaly"]
        )
        display.plot()
        plt.title(f"Confusion Matrix - {model_name}")
        plt.tight_layout()
        safe_name = model_name.lower().replace(" ", "_")
        plt.savefig(OUTPUT_DIR / f"confusion_matrix_{safe_name}.png", dpi=150)
        plt.close()

        print(classification_report(
            y_test, predictions, target_names=["Normal", "Anomaly"],
            zero_division=0
        ))

    # Step 5: Save metrics and plot model comparison.
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_DIR / "model_results.csv", index=False)
    print("\n3. Model comparison:")
    print(results_df.round(4).to_string(index=False))

    results_df.set_index("model")[["accuracy", "precision", "recall", "f1_score"]].plot(
        kind="bar", ylim=(0, 1), rot=15
    )
    plt.ylabel("Score")
    plt.title("ML Model Comparison")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "model_comparison.png", dpi=150)
    plt.close()

    # Step 6: Record operating-system resource measurements.
    resource_after = get_system_resources()
    with open(OUTPUT_DIR / "os_resource_observations.json", "w", encoding="utf-8") as f:
        json.dump({
            "before_training": resource_before,
            "after_training": resource_after,
            "python_process_id": os.getpid(),
            "note": "Resource readings are observations from this machine and run."
        }, f, indent=2)

    # Step 7: Save a concise run summary.
    summary = {
        "dataset_records": int(len(data)),
        "normal_records": int((data["label"] == 0).sum()),
        "anomaly_records": int((data["label"] == 1).sum()),
        "feature_columns": feature_columns,
        "random_seed": RANDOM_SEED,
        "test_size": 0.25,
        "models": list(models.keys()),
        "results_folder": str(OUTPUT_DIR.resolve())
    }
    with open(OUTPUT_DIR / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n4. OS resource observations:")
    print(json.dumps(resource_after, indent=2))
    print(f"\nFinished. Open this folder for all results:\n{OUTPUT_DIR.resolve()}")
    print("Important: use the actual results produced by your run in your report.")
    print("Classifiers: Logistic Regression, Decision Tree, and KNN.")


if __name__ == "__main__":
    main()
