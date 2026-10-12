
from pathlib import Path
import pandas as pd

from security_schema import SECURITY_SCHEMA, DATASET_COLUMN_MAPPINGS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "security"
OUTPUT_DIR = PROJECT_ROOT / "data" / "standardized" / "security"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATASET_FILES = {
    "ton_iot": ["train_test_network(in).csv"],
    "unsw_nb15": [
        "UNSW_NB15_training-set(in).csv",
        "UNSW_NB15_testing-set(in).csv",
    ],
}


def clean_column_names(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def standardize_dataset(df, dataset_name):
    df = clean_column_names(df)
    mappings = DATASET_COLUMN_MAPPINGS[dataset_name]

    # Rename only source columns that have an explicit mapping.
    df = df.rename(columns=mappings)

    result = pd.DataFrame(index=df.index)

    for column in SECURITY_SCHEMA:
        if column in df.columns:
            result[column] = df[column]
        else:
            result[column] = pd.NA

    result["dataset_source"] = dataset_name

    numeric_columns = [
        "src_port",
        "dst_port",
        "flow_duration",
        "src_packets",
        "dst_packets",
        "src_bytes",
        "dst_bytes",
        "src_packet_rate",
        "dst_packet_rate",
        "src_byte_rate",
        "dst_byte_rate",
        "binary_label",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column], errors="coerce"
        )

    text_columns = [
        "timestamp",
        "src_ip",
        "dst_ip",
        "protocol",
        "connection_state",
        "service",
        "attack_type",
        "dataset_source",
    ]

    for column in text_columns:
        result[column] = result[column].astype("string").str.strip()

    result["protocol"] = result["protocol"].str.lower()
    result["attack_type"] = result["attack_type"].str.lower()

    return result.reset_index(drop=True)


def main():
    print("=" * 72)
    print("SECURITY DATASET STANDARDIZATION")
    print("=" * 72)

    for dataset_name, filenames in DATASET_FILES.items():
        for filename in filenames:
            input_path = RAW_DIR / filename

            if not input_path.exists():
                print(f"\nSKIPPING: {input_path}")
                print("File not found.")
                continue

            print(f"\nProcessing: {filename}")

            try:
                df = pd.read_csv(input_path, low_memory=False)
            except Exception as exc:
                print(f"Could not read file: {exc}")
                continue

            print(f"Original shape: {df.shape}")

            standardized = standardize_dataset(df, dataset_name)

            empty_columns = [
                col for col in standardized.columns
                if standardized[col].isna().all()
            ]

            output_filename = (
                f"{dataset_name}_{input_path.stem}_standardized.csv"
            )
            output_path = OUTPUT_DIR / output_filename

            standardized.to_csv(output_path, index=False)

            print(f"Standardized shape: {standardized.shape}")
            print(f"Saved: {output_path}")

            if empty_columns:
                print("Entirely empty canonical columns:")
                for col in empty_columns:
                    print(f"  - {col}")
            else:
                print("No entirely empty columns.")

    print("\nStandardization run complete.")


if __name__ == "__main__":
    main()
