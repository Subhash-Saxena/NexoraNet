"""REST API endpoints for the Interactive Network Simulator."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models.simulator import (
    SimulatorScenario,
    SimulatorScenarioAttempt,
    SimulatorTopology,
)
from app.schemas.common import ModuleStatusResponse
from app.schemas.simulator import (
    ScenarioResponse,
    ScenarioValidationRequest,
    ScenarioValidationResultResponse,
    SimulatePacketRequest,
    SimulationResultResponse,
    TopologyCreateRequest,
    TopologyDataSchema,
    TopologyResponse,
    TopologyUpdateRequest,
    TopologyValidationResult,
)
from app.services.simulation_engine import simulation_engine
from app.services.simulator_catalog_service import simulator_catalog_service
from app.services.simulator_network_utils import (
    get_subnet_details,
    is_valid_gateway,
    is_valid_ipv4,
)
from app.services.simulator_validation_service import simulator_validation_service

router = APIRouter()


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
async def get_simulator_status() -> ModuleStatusResponse:
    """Return status and metadata for interactive network topology simulator."""
    return ModuleStatusResponse(
        module="simulator",
        status="planned",
        description="Visual network topology builder and packet flow simulation sandbox.",
        planned_phase="Phase 3",
        capabilities=[
            "Drag-and-drop nodes (Routers, Switches, Hosts, Firewalls)",
            "Visual step-by-step packet traversal animations",
            "ARP table and routing table inspection in real time",
            "Ping and traceroute visual simulations",
        ],
    )


# ---------------------------------------------------------------------------
# Topologies Endpoints
# ---------------------------------------------------------------------------


@router.get("/topologies", response_model=list[TopologyResponse])
def list_topologies(
    db: DbSession,
    user_id: int | None = Query(default=1, description="Current student user ID"),
) -> list[TopologyResponse]:
    """Retrieve all prebuilt library topologies and user saved topologies."""
    return simulator_catalog_service.list_topologies(db, user_id=user_id)


@router.get("/topologies/{id_or_slug}", response_model=TopologyResponse)
def get_topology(
    id_or_slug: str,
    db: DbSession,
) -> TopologyResponse:
    """Retrieve detailed topology specification by ID or slug."""
    topo = simulator_catalog_service.get_topology(db, id_or_slug)
    if not topo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topology '{id_or_slug}' not found.",
        )
    return topo


@router.post("/topologies", response_model=TopologyResponse, status_code=status.HTTP_201_CREATED)
def create_topology(
    req: TopologyCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> TopologyResponse:
    """Save a user-created network topology."""
    user_id = current_user.id
    slug = f"user-{user_id}-{uuid.uuid4().hex[:8]}"
    topo_json = req.topology_data.model_dump_json()

    new_topo = SimulatorTopology(
        user_id=user_id,
        name=req.name,
        slug=slug,
        description=req.description,
        difficulty=req.difficulty,
        is_prebuilt=False,
        topology_data=topo_json,
    )
    db.add(new_topo)
    db.commit()
    db.refresh(new_topo)

    return TopologyResponse(
        id=new_topo.id,
        user_id=new_topo.user_id,
        name=new_topo.name,
        slug=new_topo.slug,
        description=new_topo.description,
        difficulty=new_topo.difficulty,
        is_prebuilt=new_topo.is_prebuilt,
        topology_data=req.topology_data,
        created_at=new_topo.created_at,
        updated_at=new_topo.updated_at,
    )


@router.put("/topologies/{topo_id}", response_model=TopologyResponse)
def update_topology(
    topo_id: int,
    req: TopologyUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> TopologyResponse:
    """Update an existing user topology."""
    topo = db.query(SimulatorTopology).filter(SimulatorTopology.id == topo_id).first()
    if not topo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topology not found.")
    if topo.is_prebuilt:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Prebuilt library topologies cannot be overwritten. Use 'Save As' to create a copy.",
        )
    if topo.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    if req.name is not None:
        topo.name = req.name
    if req.description is not None:
        topo.description = req.description
    if req.difficulty is not None:
        topo.difficulty = req.difficulty
    if req.topology_data is not None:
        topo.topology_data = req.topology_data.model_dump_json()

    db.commit()
    db.refresh(topo)

    data = json.loads(topo.topology_data) if topo.topology_data else {"nodes": [], "links": []}
    return TopologyResponse(
        id=topo.id,
        user_id=topo.user_id,
        name=topo.name,
        slug=topo.slug,
        description=topo.description,
        difficulty=topo.difficulty,
        is_prebuilt=topo.is_prebuilt,
        topology_data=TopologyDataSchema.model_validate(data),
        created_at=topo.created_at,
        updated_at=topo.updated_at,
    )


@router.delete("/topologies/{topo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topology(
    topo_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a user-created network topology."""
    topo = db.query(SimulatorTopology).filter(SimulatorTopology.id == topo_id).first()
    if not topo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topology not found.")
    if topo.is_prebuilt:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Prebuilt topologies cannot be deleted.")
    if topo.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    db.delete(topo)
    db.commit()


@router.post("/topologies/validate", response_model=TopologyValidationResult)
def validate_topology_configuration(req: TopologyDataSchema) -> TopologyValidationResult:
    """Perform static validation of IP addressing, gateway consistency, and subnets across topology."""
    errors: list[str] = []
    warnings: list[str] = []
    subnets_detected: list[dict[str, Any]] = []

    seen_ips: dict[str, str] = {}

    for node in req.nodes:
        for iface in node.interfaces:
            if iface.ipv4_address:
                # 1. Check IP validity
                if not is_valid_ipv4(iface.ipv4_address):
                    errors.append(f"Device '{node.name}' has invalid IPv4 address '{iface.ipv4_address}'.")
                # 2. Check for duplicate IPs
                elif iface.ipv4_address in seen_ips:
                    errors.append(
                        f"Duplicate IP collision: {iface.ipv4_address} is assigned to both '{seen_ips[iface.ipv4_address]}' and '{node.name}'."
                    )
                else:
                    seen_ips[iface.ipv4_address] = node.name

                # 3. Check gateway validity
                if iface.default_gateway:
                    valid_gw, gw_reason = is_valid_gateway(
                        iface.ipv4_address,
                        iface.subnet_mask or "255.255.255.0",
                        iface.default_gateway,
                    )
                    if not valid_gw:
                        warnings.append(f"Device '{node.name}': {gw_reason}")

                # 4. Record detected subnet
                try:
                    details = get_subnet_details(iface.ipv4_address, iface.subnet_mask or "255.255.255.0")
                    subnets_detected.append({
                        "device": node.name,
                        "interface": iface.name,
                        "network": f"{details.network_address}/{details.prefix_length}",
                        "broadcast": details.broadcast_address,
                        "usable_hosts": details.usable_hosts,
                    })
                except (ValueError, TypeError):
                    warnings.append(f"Could not compute subnet details for {iface.ipv4_address}")

    return TopologyValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        subnets_detected=subnets_detected,
    )


# ---------------------------------------------------------------------------
# Simulation Execution Endpoint
# ---------------------------------------------------------------------------


@router.post("/simulate/packet", response_model=SimulationResultResponse)
def simulate_packet(req: SimulatePacketRequest) -> SimulationResultResponse:
    """Execute authoritative virtual educational packet simulation across the topology."""
    return simulation_engine.simulate(req)


# ---------------------------------------------------------------------------
# Scenarios & Challenges Endpoints
# ---------------------------------------------------------------------------


@router.get("/scenarios", response_model=list[ScenarioResponse])
def list_scenarios(db: DbSession) -> list[ScenarioResponse]:
    """Retrieve all available guided networking scenarios."""
    return simulator_catalog_service.list_scenarios(db)


@router.get("/scenarios/{slug}", response_model=ScenarioResponse)
def get_scenario(slug: str, db: DbSession) -> ScenarioResponse:
    """Retrieve scenario details, learning objectives, and initial topology by slug."""
    scenario = simulator_catalog_service.get_scenario(db, slug)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{slug}' not found.",
        )
    return scenario


@router.post("/scenarios/{slug}/validate", response_model=ScenarioValidationResultResponse)
def validate_scenario(
    slug: str,
    req: ScenarioValidationRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ScenarioValidationResultResponse:
    """Validate student's topology and simulation results against scenario completion rules."""
    scenario = db.query(SimulatorScenario).filter(SimulatorScenario.slug == slug).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{slug}' not found.")

    rules = json.loads(scenario.validation_rules) if scenario.validation_rules else []
    validation_res = simulator_validation_service.validate_scenario(
        rules=rules,
        request=req,
        solution_explanation=scenario.solution_explanation,
    )

    # Record or update student attempt progress
    user_id = current_user.id
    if user_id:
        attempt = (
            db.query(SimulatorScenarioAttempt)
            .filter(
                SimulatorScenarioAttempt.user_id == user_id,
                SimulatorScenarioAttempt.scenario_id == scenario.id,
            )
            .first()
        )
        now = datetime.now(timezone.utc)
        results_json = json.dumps(validation_res.task_results)

        if attempt:
            attempt.hints_used = max(attempt.hints_used, req.hints_used)
            attempt.score = max(attempt.score, validation_res.score)
            attempt.validation_results = results_json
            if validation_res.is_passed and attempt.status != "COMPLETED":
                attempt.status = "COMPLETED"
                attempt.completed_at = now
        else:
            db.add(
                SimulatorScenarioAttempt(
                    user_id=user_id,
                    scenario_id=scenario.id,
                    status="COMPLETED" if validation_res.is_passed else "IN_PROGRESS",
                    score=validation_res.score,
                    hints_used=req.hints_used,
                    validation_results=results_json,
                    completed_at=now if validation_res.is_passed else None,
                )
            )
        db.commit()

    return validation_res
