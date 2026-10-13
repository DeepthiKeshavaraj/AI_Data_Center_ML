
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
EDA_DIR = PROJECT_ROOT / "reports" / "security_eda"

EDA_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "ton_iot": "ton_iot_train_test_network(in)_ml_ready.csv",
    "unsw_nb15_train": (
        "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
    ),
    "unsw_nb15_test": (
        "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"
    ),
}

NUMERIC_COLUMNS = [
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
]

CATEGORICAL_COLUMNS = [
    "protocol",
    "connection_state",
    "service",
]


def analyze_dataset(dataset_name, filename):
    path = DATA_DIR / filename

    print("\n" + "=" * 72)
    print(f"EDA: {dataset_name}")
    print("=" * 72)

    if not path.exists():
        print(f"File not found: {path}")
        return

    df = pd.read_csv(path, low_memory=False)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # 1. Numeric descriptive statistics
    numeric_summary = df[NUMERIC_COLUMNS].describe().T
    numeric_summary.to_csv(
        EDA_DIR / f"{dataset_name}_numeric_summary.csv"
    )
    print("\nNumeric summary:")
    print(numeric_summary.to_string())

    # 2. Binary class distribution
    label_counts = df["binary_label"].value_counts().sort_index()
    label_counts.rename_axis("binary_label").to_csv(
        EDA_DIR / f"{dataset_name}_label_counts.csv"
    )

    print("\nBinary labels:")
    print(label_counts.to_string())

    fig, ax = plt.subplots(figsize=(7, 5))
    label_counts.plot(kind="bar", ax=ax)
    ax.set_title(f"{dataset_name}: Normal vs Attack")
    ax.set_xlabel("Binary label (0=normal, 1=attack)")
    ax.set_ylabel("Record count")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(
        EDA_DIR / f"{dataset_name}_label_distribution.png",
        dpi=150,
    )
    plt.close(fig)

    # 3. Attack-category distribution
    attack_counts = df["attack_type"].value_counts()
    attack_counts.rename_axis("attack_type").to_csv(
        EDA_DIR / f"{dataset_name}_attack_counts.csv"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    attack_counts.sort_values().plot(kind="barh", ax=ax)
    ax.set_title(f"{dataset_name}: Attack Categories")
    ax.set_xlabel("Record count")
    ax.set_ylabel("Attack category")
    fig.tight_layout()
    fig.savefig(
        EDA_DIR / f"{dataset_name}_attack_distribution.png",
        dpi=150,
    )
    plt.close(fig)

    # 4. Numeric distributions
    for column in NUMERIC_COLUMNS:
        fig, ax = plt.subplots(figsize=(8, 5))
        df[column].dropna().plot(
            kind="hist", bins=50, ax=ax
        )
        ax.set_title(f"{dataset_name}: {column} distribution")
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.savefig(
            EDA_DIR / f"{dataset_name}_{column}_histogram.png",
            dpi=150,
        )
        plt.close(fig)

    # 5. Correlation heatmap
    correlation = df[NUMERIC_COLUMNS].corr()
    correlation.to_csv(
        EDA_DIR / f"{dataset_name}_correlation.csv"
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(correlation, vmin=-1, vmax=1)
    ax.set_xticks(range(len(NUMERIC_COLUMNS)))
    ax.set_yticks(range(len(NUMERIC_COLUMNS)))
    ax.set_xticklabels(NUMERIC_COLUMNS, rotation=45, ha="right")
    ax.set_yticklabels(NUMERIC_COLUMNS)
    ax.set_title(f"{dataset_name}: Numeric Feature Correlation")
    fig.colorbar(image, ax=ax, label="Correlation")
    fig.tight_layout()
    fig.savefig(
        EDA_DIR / f"{dataset_name}_correlation_heatmap.png",
        dpi=150,
    )
    plt.close(fig)

    # 6. Categorical summaries
    for column in CATEGORICAL_COLUMNS:
        counts = df[column].value_counts(dropna=False)
        counts.rename_axis(column).to_csv(
            EDA_DIR / f"{dataset_name}_{column}_counts.csv"
        )

    print(f"\nEDA outputs saved to: {EDA_DIR}")


def main():
    for dataset_name, filename in FILES.items():
        analyze_dataset(dataset_name, filename)

    print("\nEDA complete.")


if __name__ == "__main__":
    main()
