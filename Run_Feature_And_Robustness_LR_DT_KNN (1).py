"""Run feature-ablation and sensor-noise robustness experiments with LR, DT and KNN.

Keep this file in the same folder as Digital_Twin_IDS_LR_DT_KNN.py.
Run: python Run_Feature_And_Robustness_LR_DT_KNN.py
Outputs: feature_comparison_results.csv and robustness_results.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from Digital_Twin_IDS_LR_DT_KNN import generate_digital_twin_data, RANDOM_SEED

OUT = Path('dt_ids_results')
OUT.mkdir(exist_ok=True)

PROCESS_FEATURES = [
    'true_water_level', 'sensor_water_level', 'pump_state',
    'valve_state', 'water_level_change'
]
COMBINED_FEATURES = PROCESS_FEATURES + ['command_mismatch', 'network_delay_ms']


def make_models():
    return {
        'Logistic Regression': make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        ),
        'Decision Tree': DecisionTreeClassifier(max_depth=8, random_state=RANDOM_SEED),
        'K-Nearest Neighbors (KNN)': make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=5)
        )
    }


def metrics(y_true, y_pred):
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1_score': f1_score(y_true, y_pred, zero_division=0),
    }


def main():
    data = generate_digital_twin_data()
    y = data['label']
    train_idx, test_idx = train_test_split(
        np.arange(len(data)), test_size=0.25, random_state=RANDOM_SEED, stratify=y
    )
    feature_rows = []

    # Feature comparison: train and test each model on both feature groups.
    for group_name, columns in [
        ('Process-only', PROCESS_FEATURES),
        ('Combined process + cyber/system', COMBINED_FEATURES),
    ]:
        X = data[columns]
        for model_name, model in make_models().items():
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            pred = model.predict(X.iloc[test_idx])
            feature_rows.append({'feature_group': group_name, 'model': model_name,
                                 **metrics(y.iloc[test_idx], pred)})

    feature_df = pd.DataFrame(feature_rows)
    feature_df.to_csv(OUT / 'feature_comparison_results.csv', index=False)

    # Robustness: train on clean combined features; add synthetic noise only
    # to the sensor_water_level test feature at each stated noise level.
    X = data[COMBINED_FEATURES]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    X_train, X_test = X.iloc[train_idx].copy(), X.iloc[test_idx].copy()
    robustness_rows = []
    for model_name, base_model in make_models().items():
        base_model.fit(X_train, y_train)
        for noise_std in [0, 2, 5, 10]:
            noisy_test = X_test.copy()
            if noise_std > 0:
                rng = np.random.default_rng(RANDOM_SEED + noise_std)
                noisy_test['sensor_water_level'] = (
                    noisy_test['sensor_water_level'].to_numpy()
                    + rng.normal(0, noise_std, size=len(noisy_test))
                )
            pred = base_model.predict(noisy_test)
            robustness_rows.append({'model': model_name,
                                     'sensor_noise_std': noise_std,
                                     **metrics(y_test, pred)})

    robustness_df = pd.DataFrame(robustness_rows)
    robustness_df.to_csv(OUT / 'robustness_results.csv', index=False)

    # Regenerate the feature-comparison chart from the newly saved results.
    feature_plot = feature_df.pivot(
        index='model', columns='feature_group', values='accuracy'
    )
    feature_plot = feature_plot * 100
    feature_plot.plot(kind='bar', figsize=(9, 5), ylim=(0, 105), rot=12)
    plt.ylabel('Accuracy (%)')
    plt.xlabel('Model')
    plt.title('Feature Comparison: Process-only vs Combined Features')
    plt.legend(title='Feature group')
    plt.tight_layout()
    plt.savefig(OUT / 'feature_comparison.png', dpi=150)
    plt.close()

    # Regenerate the robustness chart using F1-score at each noise level.
    for model_name, group in robustness_df.groupby('model'):
        plt.plot(
            group['sensor_noise_std'], group['f1_score'] * 100,
            marker='o', label=model_name
        )
    plt.xlabel('Sensor noise standard deviation')
    plt.ylabel('F1-score (%)')
    plt.title('Model Robustness Under Sensor Noise')
    plt.xticks([0, 2, 5, 10])
    plt.ylim(0, 105)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / 'robustness_comparison.png', dpi=150)
    plt.close()

    # Remove obsolete Random Forest confusion-matrix images from older runs.
    for old_plot in OUT.glob('confusion_matrix_random_forest*.png'):
        old_plot.unlink()

    print('\nFEATURE COMPARISON')
    print(feature_df.round(4).to_string(index=False))
    print('\nROBUSTNESS')
    print(robustness_df.round(4).to_string(index=False))
    print(f'\nSaved updated CSV files and charts in: {OUT.resolve()}')
    print('Models used: Logistic Regression, Decision Tree, and KNN only.')
    print('Charts: feature_comparison.png and robustness_comparison.png')


if __name__ == '__main__':
    main()
