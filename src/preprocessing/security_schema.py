
import pandas as pd


# ============================================================
# CANONICAL SECURITY SCHEMA
# ============================================================

SECURITY_SCHEMA = {
    "timestamp": "string",
    "src_ip": "string",
    "dst_ip": "string",
    "src_port": "Int64",
    "dst_port": "Int64",
    "protocol": "string",
    "flow_duration": "float64",
    "src_packets": "float64",
    "dst_packets": "float64",
    "src_bytes": "float64",
    "dst_bytes": "float64",
    "src_packet_rate": "float64",
    "dst_packet_rate": "float64",
    "src_byte_rate": "float64",
    "dst_byte_rate": "float64",
    "connection_state": "string",
    "service": "string",
    "attack_type": "string",
    "binary_label": "Int64",
    "dataset_source": "string",
}


# Required for the current binary-classification pipeline.
REQUIRED_MODEL_COLUMNS = [
    "protocol",
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "binary_label",
    "attack_type",
    "dataset_source",
]


# Fields that may be unavailable in a particular dataset.
OPTIONAL_COLUMNS = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "src_packet_rate",
    "dst_packet_rate",
    "src_byte_rate",
    "dst_byte_rate",
    "connection_state",
    "service",
]


# ============================================================
# DATASET COLUMN MAPPINGS
# ============================================================

DATASET_COLUMN_MAPPINGS = {
    "ton_iot": {
        "src_ip": "src_ip",
        "dst_ip": "dst_ip",
        "src_port": "src_port",
        "dst_port": "dst_port",
        "proto": "protocol",
        "duration": "flow_duration",
        "src_pkts": "src_packets",
        "dst_pkts": "dst_packets",
        "src_bytes": "src_bytes",
        "dst_bytes": "dst_bytes",
        "conn_state": "connection_state",
        "service": "service",
        "label": "binary_label",
        "type": "attack_type",
    },
    "unsw_nb15": {
        "dur": "flow_duration",
        "proto": "protocol",
        "spkts": "src_packets",
        "dpkts": "dst_packets",
        "sbytes": "src_bytes",
        "dbytes": "dst_bytes",
        "state": "connection_state",
        "service": "service",
        "attack_cat": "attack_type",
        "label": "binary_label",
    },
}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_schema(df: pd.DataFrame) -> None:
    """Raise an error if required canonical columns are missing."""

    missing = [
        col
        for col in REQUIRED_MODEL_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required canonical columns: {missing}"
        )


def validate_dataset_name(dataset_name: str) -> None:
    """Ensure that the dataset has a registered column mapping."""

    if dataset_name not in DATASET_COLUMN_MAPPINGS:
        raise ValueError(
            f"Unknown dataset: {dataset_name}. "
            f"Expected one of: {list(DATASET_COLUMN_MAPPINGS)}"
        )


def create_empty_canonical_frame(
    index: pd.Index | None = None,
) -> pd.DataFrame:
    """Create an empty frame containing every canonical column."""

    return pd.DataFrame(
        index=index,
        columns=list(SECURITY_SCHEMA.keys()),
    )
