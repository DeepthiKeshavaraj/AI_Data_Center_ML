from typing import Dict, Any, List, Optional
import math
from fastapi import HTTPException

from app.schemas.security import SecurityPredictRequest, SecurityPredictResponse
from app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationPresetInfo,
    MetricItem,
    SimulationEventItem,
    SimulationRecommendationItem,
    DomainStatus,
)
from app.services.security_service import predict_security, SAMPLE_PRESETS
from app.services.model_loader import registry

# Baseline thermodynamic and cluster simulation constants
BASELINE_CLUSTER_IDLE_KW = 100.0
BASELINE_CLUSTER_MAX_DYNAMIC_KW = 150.0
BASELINE_IDLE_TEMP_RISE_C = 8.0
BASELINE_DYNAMIC_TEMP_RISE_C = 30.0


PRESET_CONFIGS: Dict[str, SimulationPresetInfo] = {
    "security_incident": SimulationPresetInfo(
        id="security_incident",
        name="Security Incident & Deep Inspection",
        description=(
            "Simulates an influx of adversarial reconnaissance traffic. The Random Forest security model "
            "evaluates incoming flows, and the resulting high threat profile triggers simulated Deep Packet Inspection (DPI) "
            "overhead on management/gateway nodes, increasing compute demand."
        ),
        initiating_domain="security",
        defaults={
            "preset": "security_incident",
            "base_cpu_demand": 450.0,
            "cluster_capacity": 1000.0,
            "suspicious_traffic_intensity": 0.85,
            "ambient_inlet_temp": 24.0,
            "throttling_threshold": 60.0,
            "inspection_overhead_factor": 0.35,
            "throttling_penalty_rate": 0.05,
            "max_throttling_limit": 0.50,
            "flow_sample": SAMPLE_PRESETS[1]["values"],  # OSPF Reconnaissance Probe
        },
    ),
    "workload_surge": SimulationPresetInfo(
        id="workload_surge",
        name="Workload Surge & Thermal Dissipation",
        description=(
            "Simulates a massive spike in tenant job demand (92% base cluster capacity) under benign network traffic. "
            "Sustained high compute density triggers Joule heating, elevating simulated outlet temperature beyond safe thresholds "
            "and triggering automated safety downclocking."
        ),
        initiating_domain="workload",
        defaults={
            "preset": "workload_surge",
            "base_cpu_demand": 920.0,
            "cluster_capacity": 1000.0,
            "suspicious_traffic_intensity": 0.10,
            "ambient_inlet_temp": 24.0,
            "throttling_threshold": 60.0,
            "inspection_overhead_factor": 0.15,
            "throttling_penalty_rate": 0.05,
            "max_throttling_limit": 0.50,
            "flow_sample": SAMPLE_PRESETS[0]["values"],  # Standard HTTP Web Traffic
        },
    ),
    "thermal_emergency": SimulationPresetInfo(
        id="thermal_emergency",
        name="Thermal Emergency & Hardware Throttling",
        description=(
            "Simulates elevated ambient inlet air (36°C) due to severe external heatwave or CRAH chiller subsystem degradation. "
            "Even moderate workload demand pushes outlet temperature into the critical range, triggering aggressive capacity curtailment "
            "and creating significant workload backlog."
        ),
        initiating_domain="thermal",
        defaults={
            "preset": "thermal_emergency",
            "base_cpu_demand": 750.0,
            "cluster_capacity": 1000.0,
            "suspicious_traffic_intensity": 0.15,
            "ambient_inlet_temp": 36.0,
            "throttling_threshold": 58.0,
            "inspection_overhead_factor": 0.20,
            "throttling_penalty_rate": 0.05,
            "max_throttling_limit": 0.50,
            "flow_sample": SAMPLE_PRESETS[2]["values"],  # DNS Lookup Query
        },
    ),
}


def get_simulation_presets() -> List[SimulationPresetInfo]:
    return list(PRESET_CONFIGS.values())


def run_cross_domain_simulation(request: SimulationRunRequest) -> SimulationRunResponse:
    # 1. Determine scenario identity and initiating domain
    preset_id = request.preset.lower()
    if preset_id in PRESET_CONFIGS:
        preset_info = PRESET_CONFIGS[preset_id]
        scenario_name = preset_info.name
        initiating_domain = preset_info.initiating_domain
    else:
        scenario_name = "Custom Cross-Domain Scenario"
        # Infer initiating domain from highest deviance from baseline
        if request.ambient_inlet_temp >= 32.0:
            initiating_domain = "thermal"
        elif request.suspicious_traffic_intensity >= 0.60:
            initiating_domain = "security"
        else:
            initiating_domain = "workload"

    # 2. Step 1: Initial Baseline Calculations (Pre-simulation steady state)
    init_cap = float(request.cluster_capacity)
    init_base_demand = float(request.base_cpu_demand)
    init_utilization = round(min(100.0, (init_base_demand / init_cap) * 100.0), 2)
    
    # Power model rule: P_idle + P_max * (utilization/100)^1.3
    init_power_kw = round(
        BASELINE_CLUSTER_IDLE_KW + BASELINE_CLUSTER_MAX_DYNAMIC_KW * ((init_utilization / 100.0) ** 1.3),
        2,
    )
    # Thermodynamic rule: T_inlet + Delta_idle + Delta_dyn * (utilization/100)
    init_outlet_temp = round(
        request.ambient_inlet_temp + BASELINE_IDLE_TEMP_RISE_C + BASELINE_DYNAMIC_TEMP_RISE_C * (init_utilization / 100.0),
        2,
    )
    
    initial_state = {
        "cluster_capacity_cores": init_cap,
        "base_cpu_demand_cores": init_base_demand,
        "inspection_overhead_cores": 0.0,
        "total_cpu_demand_cores": init_base_demand,
        "admitted_demand_cores": min(init_base_demand, init_cap),
        "backlog_cores": max(0.0, init_base_demand - init_cap),
        "cpu_utilization_pct": init_utilization,
        "power_consumption_kw": init_power_kw,
        "ambient_inlet_temp_c": round(request.ambient_inlet_temp, 1),
        "outlet_temp_c": init_outlet_temp,
        "throttling_penalty_pct": 0.0,
    }

    event_log: List[SimulationEventItem] = []
    triggered_rules: List[str] = []
    step_counter = 1

    # Log initial step
    event_log.append(
        SimulationEventItem(
            step=step_counter,
            timestamp_offset_sec=0,
            domain=initiating_domain,
            severity="info",
            title=f"Scenario Triggered: {scenario_name}",
            description=(
                f"Simulation started with {init_base_demand:.0f} base CPU cores requested across "
                f"{init_cap:.0f} cluster capacity ({init_utilization:.1f}% baseline utilization). "
                f"Ambient inlet temperature is {request.ambient_inlet_temp:.1f}°C."
            ),
        )
    )
    step_counter += 1

    # 3. Domain: Security Evaluation & Security -> Workload Propagation
    security_ml_used = False
    security_result: Optional[SecurityPredictResponse] = None
    security_explanation = ""
    attack_prob = float(request.suspicious_traffic_intensity)

    if request.flow_sample is not None:
        try:
            security_result = predict_security(request.flow_sample)
            security_ml_used = True
            attack_prob = security_result.attack_probability
            security_explanation = (
                f"Real Random Forest ML Model classified flow as {security_result.label.upper()} "
                f"({attack_prob * 100:.1f}% attack probability). "
                f"Source: {request.flow_sample.protocol.upper()} flow, duration {request.flow_sample.flow_duration}s."
            )
            event_log.append(
                SimulationEventItem(
                    step=step_counter,
                    timestamp_offset_sec=5,
                    domain="security",
                    severity="danger" if security_result.label == "Attack" else "info",
                    title="Real ML Security Inference Completed",
                    description=security_explanation,
                )
            )
        except Exception as e:
            security_ml_used = False
            security_explanation = f"Security model unavailable or error ({str(e)}). Used configured suspicious intensity."
            event_log.append(
                SimulationEventItem(
                    step=step_counter,
                    timestamp_offset_sec=5,
                    domain="security",
                    severity="warning",
                    title="Security Model Fallback",
                    description=security_explanation,
                )
            )
    else:
        security_explanation = (
            f"No individual network flow sample provided. Evaluating based on configured suspicious traffic intensity "
            f"({request.suspicious_traffic_intensity * 100:.1f}%)."
        )
        event_log.append(
            SimulationEventItem(
                step=step_counter,
                timestamp_offset_sec=5,
                domain="security",
                severity="info",
                title="Telemetry Ingestion",
                description=security_explanation,
            )
        )
    step_counter += 1

    # Rule: Security -> Workload simulated inspection overhead
    # We combine traffic intensity and model attack probability
    threat_weight = (0.5 * request.suspicious_traffic_intensity) + (0.5 * attack_prob)
    inspection_overhead_cores = round(
        init_base_demand * (request.inspection_overhead_factor * threat_weight),
        2,
    )

    if inspection_overhead_cores > 5.0:
        triggered_rules.append("SECURITY_DPI_INSPECTION_OVERHEAD_ADDED")
        event_log.append(
            SimulationEventItem(
                step=step_counter,
                timestamp_offset_sec=12,
                domain="workload",
                severity="warning" if threat_weight >= 0.5 else "info",
                title="Security -> Workload: Deep Packet Inspection Overhead",
                description=(
                    f"Suspicious traffic and threat indicators triggered automated Deep Packet Inspection (DPI) "
                    f"and firewall state tracking. Simulated inspection penalty added +{inspection_overhead_cores:.1f} cores "
                    f"(+{((inspection_overhead_cores / init_base_demand) * 100):.1f}% demand increase)."
                ),
            )
        )
        step_counter += 1

    total_cpu_demand = round(init_base_demand + inspection_overhead_cores, 2)

    # 4. Domain: Workload -> Thermal Propagation (Pre-throttling heat assessment)
    unthrottled_utilization = (total_cpu_demand / init_cap) * 100.0
    pre_throttling_temp = round(
        request.ambient_inlet_temp
        + BASELINE_IDLE_TEMP_RISE_C
        + BASELINE_DYNAMIC_TEMP_RISE_C * min(1.0, unthrottled_utilization / 100.0),
        2,
    )

    event_log.append(
        SimulationEventItem(
            step=step_counter,
            timestamp_offset_sec=20,
            domain="thermal",
            severity="warning" if pre_throttling_temp >= request.throttling_threshold else "info",
            title="Workload -> Thermal: Compute Dissipation Assessment",
            description=(
                f"Total requested CPU demand evaluated at {total_cpu_demand:.1f} cores ({unthrottled_utilization:.1f}% unthrottled load). "
                f"Simulated Joule heating projects outlet temperature reaching {pre_throttling_temp:.1f}°C."
            ),
        )
    )
    step_counter += 1

    # 5. Domain: Thermal -> Workload Capacity Throttling
    throttling_penalty = 0.0
    final_capacity = init_cap

    if pre_throttling_temp > request.throttling_threshold:
        temp_excess = pre_throttling_temp - request.throttling_threshold
        # Calculate throttling fraction: penalty_rate per degree excess up to max limit
        raw_penalty = temp_excess * request.throttling_penalty_rate
        throttling_penalty = min(request.max_throttling_limit, round(raw_penalty, 4))
        final_capacity = round(init_cap * (1.0 - throttling_penalty), 2)
        
        triggered_rules.append("THERMAL_CAPACITY_THROTTLING_TRIGGERED")
        event_log.append(
            SimulationEventItem(
                step=step_counter,
                timestamp_offset_sec=30,
                domain="policy",
                severity="danger" if throttling_penalty >= 0.25 else "warning",
                title="Thermal -> Workload: Thermal Throttling Policy Activated",
                description=(
                    f"Projected outlet temperature ({pre_throttling_temp:.1f}°C) exceeded the configured "
                    f"safety ceiling ({request.throttling_threshold:.1f}°C) by {temp_excess:.1f}°C. "
                    f"Dynamic Frequency Downclocking / node protection curtailed cluster capacity by "
                    f"{throttling_penalty * 100:.1f}%, reducing available cores from {init_cap:.0f} to {final_capacity:.0f}."
                ),
            )
        )
        step_counter += 1
    else:
        event_log.append(
            SimulationEventItem(
                step=step_counter,
                timestamp_offset_sec=30,
                domain="policy",
                severity="info",
                title="Thermal Policy: Temperature Within Safe Operating Margin",
                description=(
                    f"Projected outlet temperature ({pre_throttling_temp:.1f}°C) is below the throttling threshold "
                    f"({request.throttling_threshold:.1f}°C). Full cluster capacity ({init_cap:.0f} cores) remains available."
                ),
            )
        )
        step_counter += 1

    # 6. Final Cluster Equilibrium (Admitted Demand & Backlog)
    if total_cpu_demand <= final_capacity:
        admitted_demand = total_cpu_demand
        backlog_cores = 0.0
        final_utilization = round((admitted_demand / final_capacity) * 100.0, 2)
    else:
        admitted_demand = final_capacity
        backlog_cores = round(total_cpu_demand - final_capacity, 2)
        final_utilization = 100.0
        triggered_rules.append("WORKLOAD_BACKLOG_ACCUMULATED")
        event_log.append(
            SimulationEventItem(
                step=step_counter,
                timestamp_offset_sec=45,
                domain="workload",
                severity="danger",
                title="Workload Contention: Backlog Formed",
                description=(
                    f"Available cluster capacity ({final_capacity:.0f} cores) was insufficient to satisfy total demand "
                    f"({total_cpu_demand:.0f} cores). An unmet workload backlog of {backlog_cores:.1f} cores was queued."
                ),
            )
        )
        step_counter += 1

    # Recalculate Final Thermal & Power Equilibrium based on active admitted compute
    active_load_ratio = admitted_demand / init_cap
    final_outlet_temp = round(
        request.ambient_inlet_temp
        + BASELINE_IDLE_TEMP_RISE_C
        + BASELINE_DYNAMIC_TEMP_RISE_C * min(1.0, active_load_ratio),
        2,
    )
    final_power_kw = round(
        BASELINE_CLUSTER_IDLE_KW
        + BASELINE_CLUSTER_MAX_DYNAMIC_KW * ((min(1.0, active_load_ratio)) ** 1.3),
        2,
    )

    final_state = {
        "cluster_capacity_cores": final_capacity,
        "base_cpu_demand_cores": init_base_demand,
        "inspection_overhead_cores": inspection_overhead_cores,
        "total_cpu_demand_cores": total_cpu_demand,
        "admitted_demand_cores": admitted_demand,
        "backlog_cores": backlog_cores,
        "cpu_utilization_pct": final_utilization,
        "power_consumption_kw": final_power_kw,
        "ambient_inlet_temp_c": round(request.ambient_inlet_temp, 1),
        "outlet_temp_c": final_outlet_temp,
        "throttling_penalty_pct": round(throttling_penalty * 100, 2),
    }

    # 7. Before-and-After Metrics List
    def calc_pct(initial: float, final: float) -> Optional[float]:
        if initial == 0:
            return None if final == 0 else round(final * 100.0, 1)
        return round(((final - initial) / initial) * 100.0, 1)

    metrics: List[MetricItem] = [
        MetricItem(
            label="Total CPU Demand",
            initial_value=init_base_demand,
            final_value=total_cpu_demand,
            unit="cores",
            category="simulation_assumption",
            category_label="Simulated Assumption",
            change_pct=calc_pct(init_base_demand, total_cpu_demand),
        ),
        MetricItem(
            label="Security Inspection Overhead",
            initial_value=0.0,
            final_value=inspection_overhead_cores,
            unit="cores",
            category="simulation_assumption",
            category_label="Simulated Assumption",
            change_pct=None if inspection_overhead_cores == 0 else 100.0,
        ),
        MetricItem(
            label="Available Cluster Capacity",
            initial_value=init_cap,
            final_value=final_capacity,
            unit="cores",
            category="rule_policy",
            category_label="Rule-based Policy",
            change_pct=calc_pct(init_cap, final_capacity),
        ),
        MetricItem(
            label="Cluster CPU Utilization",
            initial_value=init_utilization,
            final_value=final_utilization,
            unit="%",
            category="simulation_assumption",
            category_label="Simulated Rule",
            change_pct=calc_pct(init_utilization, final_utilization),
        ),
        MetricItem(
            label="Simulated Thermal Outlet Temp",
            initial_value=init_outlet_temp,
            final_value=final_outlet_temp,
            unit="°C",
            category="simulation_assumption",
            category_label="Simulated Rule",
            change_pct=calc_pct(init_outlet_temp, final_outlet_temp),
        ),
        MetricItem(
            label="Estimated Power Draw",
            initial_value=init_power_kw,
            final_value=final_power_kw,
            unit="kW",
            category="simulation_assumption",
            category_label="Simulated Rule",
            change_pct=calc_pct(init_power_kw, final_power_kw),
        ),
        MetricItem(
            label="Thermal Capacity Reduction",
            initial_value=0.0,
            final_value=round(throttling_penalty * 100, 1),
            unit="%",
            category="rule_policy",
            category_label="Rule-based Policy",
            change_pct=None,
        ),
        MetricItem(
            label="Workload Backlog (Unmet Demand)",
            initial_value=0.0,
            final_value=backlog_cores,
            unit="cores",
            category="rule_policy",
            category_label="Rule-based Policy",
            change_pct=None if backlog_cores == 0 else 100.0,
        ),
    ]

    # 8. Domain Statuses (Normal, Warning, Critical)
    # Security Status
    if attack_prob >= 0.70:
        sec_state = "critical"
        sec_headline = "High Threat Detected"
        sec_details = f"Active attack classification ({attack_prob * 100:.1f}% risk). Deep packet inspection elevated."
    elif attack_prob >= 0.35:
        sec_state = "warning"
        sec_headline = "Elevated Suspicion"
        sec_details = f"Borderline telemetry ({attack_prob * 100:.1f}% risk). Light filtering applied."
    else:
        sec_state = "normal"
        sec_headline = "Benign Traffic"
        sec_details = "Normal baseline network flows observed."
    
    sec_metric = f"Attack Prob: {attack_prob * 100:.1f}%" if not security_ml_used else f"ML Prob: {attack_prob * 100:.1f}% ({security_result.label})"

    # Workload Status
    if backlog_cores > 0.0:
        work_state = "critical"
        work_headline = "Workload Backlog / Saturation"
        work_details = f"{backlog_cores:.0f} cores queued due to capacity deficit."
    elif final_utilization >= 85.0:
        work_state = "warning"
        work_headline = "Near-Capacity Operation"
        work_details = f"{final_utilization:.1f}% cluster utilization reached."
    else:
        work_state = "normal"
        work_headline = "Balanced Allocation"
        work_details = f"{final_utilization:.1f}% load within safe operational envelope."

    work_metric = f"{admitted_demand:.0f} / {final_capacity:.0f} cores ({final_utilization:.0f}%)"

    # Thermal Status
    if final_outlet_temp >= 65.0 or throttling_penalty >= 0.25:
        therm_state = "critical"
        therm_headline = "High Thermal Stress"
        therm_details = f"Outlet temp {final_outlet_temp:.1f}°C. Aggressive throttling active (-{throttling_penalty * 100:.0f}%)."
    elif final_outlet_temp >= request.throttling_threshold or throttling_penalty > 0.0 or final_outlet_temp >= 55.0:
        therm_state = "warning"
        therm_headline = "Thermal Warning Zone"
        therm_details = f"Outlet temp {final_outlet_temp:.1f}°C. Protective throttling active (-{throttling_penalty * 100:.0f}%)."
    else:
        therm_state = "normal"
        therm_headline = "Optimal Thermal Zone"
        therm_details = f"Outlet temp {final_outlet_temp:.1f}°C well below safety limits."

    therm_metric = f"{final_outlet_temp:.1f}°C (Inlet: {request.ambient_inlet_temp:.1f}°C)"

    domain_statuses = {
        "security": DomainStatus(
            state=sec_state,
            headline=sec_headline,
            details=sec_details,
            primary_metric=sec_metric,
        ),
        "workload": DomainStatus(
            state=work_state,
            headline=work_headline,
            details=work_details,
            primary_metric=work_metric,
        ),
        "thermal": DomainStatus(
            state=therm_state,
            headline=therm_headline,
            details=therm_details,
            primary_metric=therm_metric,
        ),
    }

    # 9. Dynamic Recommendations based on actual state and triggered rules
    recommendations: List[SimulationRecommendationItem] = []

    if attack_prob >= 0.70:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_sec_filter",
                domain="security",
                priority="critical",
                action="Deploy Targeted Gateway Flow Filtering",
                rationale=(
                    f"Random Forest model and telemetry indicated {attack_prob * 100:.1f}% threat confidence. "
                    "Deploying eBPF/hardware flow filtering at edge switches mitigates CPU overhead from software DPI."
                ),
            )
        )
    elif attack_prob >= 0.35:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_sec_sample",
                domain="security",
                priority="medium",
                action="Increase NetFlow Sampling Rate",
                rationale="Borderline traffic patterns observed; elevate flow capture resolution on ingress routers.",
            )
        )

    if throttling_penalty > 0.0:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_therm_chiller",
                domain="thermal",
                priority="high",
                action="Ramp Up CRAH Cooling Airflow & Check Cold Aisle",
                rationale=(
                    f"Thermal throttling triggered curtailment of {throttling_penalty * 100:.1f}% capacity. "
                    "Increasing CRAH fan speeds and inspecting containment baffles can restore thermal equilibrium."
                ),
            )
        )

    if backlog_cores > 0.0:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_workload_shed",
                domain="workload",
                priority="critical",
                action="Shed or Migrate Non-Critical Batch Queues",
                rationale=(
                    f"{backlog_cores:.0f} cores currently backlogged. Defer low-priority machine learning training jobs "
                    "or spill over burst workloads to secondary cloud regions until thermal headroom recovers."
                ),
            )
        )
    elif final_utilization >= 85.0:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_workload_rebalance",
                domain="workload",
                priority="medium",
                action="Apply Bin-Packing Allocation Strategy",
                rationale="High cluster utilization; consolidate fragmented pods to optimize airflow distribution.",
            )
        )

    if not recommendations:
        recommendations.append(
            SimulationRecommendationItem(
                id="rec_nominal",
                domain="system",
                priority="low",
                action="Maintain Current Dispatch Scheduling",
                rationale="All subsystems operating within safe green-tier thresholds. No intervention needed.",
            )
        )

    return SimulationRunResponse(
        scenario_name=scenario_name,
        initiating_domain=initiating_domain,
        security_ml_used=security_ml_used,
        security_result=security_result,
        security_explanation=security_explanation,
        initial_state=initial_state,
        final_state=final_state,
        metrics=metrics,
        domain_statuses=domain_statuses,
        triggered_rules=triggered_rules,
        event_log=event_log,
        recommendations=recommendations,
        is_simulation=True,
    )
