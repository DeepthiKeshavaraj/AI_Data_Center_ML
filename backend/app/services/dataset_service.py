from pathlib import Path
from typing import Dict, Any, List
import math
from fastapi import HTTPException

from app.services.model_loader import PROJECT_ROOT

APPROVED_DATASETS: Dict[str, Dict[str, Any]] = {
    "unsw_nb15_train": {
        "id": "unsw_nb15_train",
        "name": "UNSW-NB15 Training Dataset",
        "component": "Security",
        "path": PROJECT_ROOT / "data" / "standardized" / "security" / "unsw_nb15_UNSW_NB15_training-set(in)_standardized.csv",
        "description": "Standardized network security training records featuring normal traffic and 9 modern cyber attack categories.",
        "size_mb": 10.3,
        "total_rows": 175341,
        "features": 20,
    },
    "unsw_nb15_test": {
        "id": "unsw_nb15_test",
        "name": "UNSW-NB15 Testing Dataset",
        "component": "Security",
        "path": PROJECT_ROOT / "data" / "standardized" / "security" / "unsw_nb15_UNSW_NB15_testing-set(in)_standardized.csv",
        "description": "Standardized holdout evaluation test set, including 47,089 unseen feature combinations.",
        "size_mb": 4.82,
        "total_rows": 82332,
        "features": 20,
    },
    "ton_iot": {
        "id": "ton_iot",
        "name": "ToN-IoT Network Dataset",
        "component": "Security",
        "path": PROJECT_ROOT / "data" / "standardized" / "security" / "ton_iot_train_test_network(in)_standardized.csv",
        "description": "Standardized telemetry from Next-Gen Internet of Things testbed with heterogeneous telemetry.",
        "size_mb": 17.56,
        "total_rows": 211043,
        "features": 20,
    },
    "pai_machine_spec": {
        "id": "pai_machine_spec",
        "name": "Alibaba PAI Machine Specifications",
        "component": "Workload & Compute",
        "path": PROJECT_ROOT / "src" / "data" / "raw" / "workload" / "pai_machine_spec.csv",
        "description": "Authentic enterprise data-center server capacities including CPU, Memory, GPU counts, and GPU architecture types.",
        "size_mb": 0.07,
        "total_rows": 1897,
        "features": 5,
    },
}


def get_all_dataset_summaries() -> List[Dict[str, Any]]:
    summaries = []
    for d_id, info in APPROVED_DATASETS.items():
        exists = info["path"].exists()
        summaries.append({
            "id": d_id,
            "name": info["name"],
            "component": info["component"],
            "description": info["description"],
            "size_mb": info["size_mb"],
            "total_rows": info["total_rows"],
            "features_count": info["features"],
            "is_available": exists,
        })
    return summaries


def get_dataset_sample(dataset_id: str, limit: int = 10) -> Dict[str, Any]:
    if dataset_id not in APPROVED_DATASETS:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{dataset_id}' not found in approved dataset catalog.",
        )

    meta = APPROVED_DATASETS[dataset_id]
    path: Path = meta["path"]

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset file is not present on disk.",
        )

    limit = max(1, min(limit, 50))  # Controlled bounded limit

    try:
        import pandas as pd
        if dataset_id == "pai_machine_spec":
            df = pd.read_csv(
                path,
                header=None,
                names=["machine_id", "gpu_type", "cap_cpu", "cap_mem", "cap_gpu"],
                nrows=limit,
            )
        else:
            df = pd.read_csv(path, nrows=limit, low_memory=False)

        # Convert DataFrame to records, sanitizing NaNs/Infs for strict JSON compliance
        raw_records = df.to_dict(orient="records")
        clean_records = []
        for row in raw_records:
            clean_row = {}
            for k, v in row.items():
                if pd.isna(v) or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
                    clean_row[k] = None
                else:
                    clean_row[k] = v
            clean_records.append(clean_row)

        columns = list(df.columns)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading dataset preview: {str(e)}",
        )

    return {
        "id": dataset_id,
        "name": meta["name"],
        "columns": columns,
        "total_rows": meta["total_rows"],
        "sample_rows": clean_records,
        "preview_count": len(clean_records),
    }
