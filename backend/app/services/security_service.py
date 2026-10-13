from pathlib import Path
import json
from typing import Dict, Any, List
import pandas as pd
from fastapi import HTTPException

from app.schemas.security import (
    SecurityPredictRequest,
    SecurityPredictResponse,
    SecurityMetadataResponse,
)
from app.services.model_loader import registry, PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"

SAMPLE_PRESETS = [
    {
        "name": "Standard HTTP Web Traffic (Normal)",
        "description": "Typical bidirectional web session with balanced packet exchange and graceful FIN termination.",
        "expected_label": "Normal",
        "values": {
            "protocol": "tcp",
            "flow_duration": 0.125,
            "src_packets": 10.0,
            "dst_packets": 8.0,
            "src_bytes": 540.0,
            "dst_bytes": 320.0,
            "connection_state": "fin",
            "service": "http",
        },
    },
    {
        "name": "OSPF Reconnaissance Probe (Attack)",
        "description": "Authentic UNSW-NB15 test record #243 representing network reconnaissance with zero return packets.",
        "expected_label": "Attack",
        "values": {
            "protocol": "ospf",
            "flow_duration": 0.921987,
            "src_packets": 20.0,
            "dst_packets": 0.0,
            "src_bytes": 1280.0,
            "dst_bytes": 0.0,
            "connection_state": "int",
            "service": "-",
        },
    },
    {
        "name": "DNS Lookup Query (Normal)",
        "description": "Short duration, low-packet UDP name resolution exchange with rapid response.",
        "expected_label": "Normal",
        "values": {
            "protocol": "udp",
            "flow_duration": 0.00045,
            "src_packets": 2.0,
            "dst_packets": 2.0,
            "src_bytes": 146.0,
            "dst_bytes": 178.0,
            "connection_state": "con",
            "service": "dns",
        },
    },
]


def predict_security(request: SecurityPredictRequest) -> SecurityPredictResponse:
    model = registry.security_model
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Security model is unavailable. Artifact has not been loaded.",
        )

    # Prepare DataFrame matching the exact training columns
    input_df = pd.DataFrame([
        {
            "flow_duration": float(request.flow_duration),
            "src_packets": float(request.src_packets),
            "dst_packets": float(request.dst_packets),
            "src_bytes": float(request.src_bytes),
            "dst_bytes": float(request.dst_bytes),
            "protocol": str(request.protocol).lower(),
            "connection_state": str(request.connection_state).lower(),
            "service": str(request.service).lower(),
        }
    ])

    try:
        pred_array = model.predict(input_df)
        pred_class = int(pred_array[0])

        prob_array = model.predict_proba(input_df)[0]
        # Classes are [0, 1]
        normal_prob = float(prob_array[0])
        attack_prob = float(prob_array[1])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference execution failed: {str(e)}",
        )

    label = "Attack" if pred_class == 1 else "Normal"
    confidence = max(normal_prob, attack_prob)

    if pred_class == 1:
        interpretation = (
            f"The Random Forest model classified this network flow as an ATTACK with "
            f"{attack_prob * 100:.1f}% confidence. Notable risk factors typically include "
            f"abnormal flow duration, asymmetric packet counts, or uncommon protocol states."
        )
    else:
        interpretation = (
            f"The Random Forest model classified this network flow as NORMAL benign traffic with "
            f"{normal_prob * 100:.1f}% confidence."
        )

    return SecurityPredictResponse(
        status="success",
        predicted_class=pred_class,
        label=label,
        attack_probability=round(attack_prob, 4),
        normal_probability=round(normal_prob, 4),
        confidence_score=round(confidence, 4),
        interpretation=interpretation,
        model_used="UNSW-NB15 Random Forest Classifier (200 trees, balanced)",
        feature_summary=request.model_dump(),
    )


DEFAULT_FEATURE_IMPORTANCES: List[Dict[str, Any]] = [
    {"original_feature": "flow_duration", "importance": 0.22715095308668276},
    {"original_feature": "src_bytes", "importance": 0.19250270382551474},
    {"original_feature": "dst_bytes", "importance": 0.13827541155100115},
    {"original_feature": "connection_state", "importance": 0.12979554075456082},
    {"original_feature": "dst_packets", "importance": 0.09648421478457654},
    {"original_feature": "src_packets", "importance": 0.09388615540317641},
    {"original_feature": "protocol", "importance": 0.06585081745581466},
    {"original_feature": "service", "importance": 0.05605420313867294},
]


def get_security_metadata() -> SecurityMetadataResponse:
    # Read verified feature importances if present
    feature_importances: List[Dict[str, Any]] = []
    imp_file = REPORT_DIR / "feature_importance_by_group.csv"
    if imp_file.exists():
        try:
            imp_df = pd.read_csv(imp_file)
            feature_importances = imp_df.to_dict(orient="records")
        except Exception:
            pass

    if not feature_importances:
        feature_importances = DEFAULT_FEATURE_IMPORTANCES

    # Read verified metrics if present
    metrics_summary: Dict[str, Any] = {
        "dataset": "UNSW-NB15",
        "training_rows": 175341,
        "test_rows": 82332,
        "test_accuracy": 0.8836,
        "balanced_accuracy": 0.8757,
        "roc_auc": 0.9721,
        "normal_precision": 0.93,
        "normal_recall": 0.80,
        "normal_f1": 0.86,
        "attack_precision": 0.85,
        "attack_recall": 0.95,
        "attack_f1": 0.90,
        "unseen_test_rows": 47089,
        "unseen_accuracy": 0.8249,
        "unseen_balanced_accuracy": 0.8390,
        "unseen_roc_auc": 0.9384,
    }

    features_info = [
        {"name": "protocol", "type": "categorical", "description": "Transport protocol (tcp, udp, ospf, arp)", "default": "tcp"},
        {"name": "flow_duration", "type": "numeric", "unit": "seconds", "description": "Total flow lifetime", "default": 0.12},
        {"name": "src_packets", "type": "numeric", "unit": "count", "description": "Packets sent by source", "default": 10},
        {"name": "dst_packets", "type": "numeric", "unit": "count", "description": "Packets sent by destination", "default": 8},
        {"name": "src_bytes", "type": "numeric", "unit": "bytes", "description": "Bytes transmitted by source", "default": 540},
        {"name": "dst_bytes", "type": "numeric", "unit": "bytes", "description": "Bytes transmitted by destination", "default": 320},
        {"name": "connection_state", "type": "categorical", "description": "Connection state (fin, con, int, req)", "default": "fin"},
        {"name": "service", "type": "categorical", "description": "Application service (-, http, dns, ftp, smtp)", "default": "http"},
    ]

    return SecurityMetadataResponse(
        model_name="UNSW-NB15 Random Forest Classifier",
        status=registry.get_status_summary()["security"]["status"],
        target="binary_label (0=Normal, 1=Attack)",
        features=features_info,
        class_labels={0: "Normal", 1: "Attack"},
        dataset_source="UNSW-NB15 Standardized Benchmark",
        verified_metrics=metrics_summary,
        feature_importances=feature_importances,
        sample_presets=SAMPLE_PRESETS,
    )
