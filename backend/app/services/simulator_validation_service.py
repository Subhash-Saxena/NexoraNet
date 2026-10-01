"""Deterministic scenario validation service for the NexoraNet Network Simulator."""

from typing import Any

from app.schemas.simulator import (
    ScenarioValidationRequest,
    ScenarioValidationResultResponse,
    SimulatePacketRequest,
)
from app.services.simulation_engine import simulation_engine
from app.services.simulator_network_utils import are_same_subnet


class SimulatorValidationService:
    """Evaluates student network topologies and simulations against scenario objectives."""

    def validate_scenario(
        self,
        rules: list[dict[str, Any]],
        request: ScenarioValidationRequest,
        solution_explanation: str = "",
    ) -> ScenarioValidationResultResponse:
        """Validate current topology and simulation against scenario rules."""
        topology = request.topology
        node_map = {n.id: n for n in topology.nodes}
        name_map = {n.name.lower(): n for n in topology.nodes}

        task_results: list[dict[str, Any]] = []
        passed_count = 0

        for idx, rule in enumerate(rules):
            rule_type = rule.get("rule_type", "").upper()
            target_dev_name = rule.get("target_device", "")
            target_iface_name = rule.get("target_interface", "")
            expected_val = rule.get("expected_value")
            desc = rule.get("description", f"Rule {idx + 1}")

            is_ok = False
            feedback_msg = ""

            target_node = (
                name_map.get(target_dev_name.lower())
                or node_map.get(target_dev_name)
            )

            if rule_type == "DEVICE_EXISTS":
                expected_type = str(expected_val).upper() if expected_val else ""
                if target_node:
                    is_ok = True
                    feedback_msg = f"Device '{target_dev_name}' is present in the topology."
                elif expected_type:
                    # Check by type
                    matches = [n for n in topology.nodes if n.type.upper() == expected_type]
                    is_ok = len(matches) > 0
                    feedback_msg = f"Found {len(matches)} device(s) of type '{expected_type}'." if is_ok else f"Missing required device of type '{expected_type}'."
                else:
                    feedback_msg = f"Device '{target_dev_name}' not found."

            elif rule_type == "DEVICE_CONNECTED":
                if not target_node:
                    feedback_msg = f"Device '{target_dev_name}' is missing."
                else:
                    links = [
                        l for l in topology.links
                        if l.source_node_id == target_node.id or l.target_node_id == target_node.id
                    ]
                    if expected_val:
                        # Check connection to specific peer name or type
                        peer_target = str(expected_val).lower()
                        connected_peers = []
                        for l in links:
                            peer_id = l.target_node_id if l.source_node_id == target_node.id else l.source_node_id
                            pnode = node_map.get(peer_id)
                            if pnode:
                                connected_peers.append(pnode)
                        matched_peer = any(
                            p.name.lower() == peer_target or p.type.lower() == peer_target
                            for p in connected_peers
                        )
                        is_ok = matched_peer
                        feedback_msg = f"Device '{target_node.name}' is cabled to '{expected_val}'." if is_ok else f"Device '{target_node.name}' must be connected to '{expected_val}'."
                    else:
                        is_ok = len(links) > 0
                        feedback_msg = f"Device '{target_node.name}' has {len(links)} connection(s)." if is_ok else f"Device '{target_node.name}' is not connected to any link."

            elif rule_type == "IP_MATCH":
                if not target_node:
                    feedback_msg = f"Device '{target_dev_name}' is missing."
                else:
                    target_iface = None
                    if target_iface_name:
                        for ifc in target_node.interfaces:
                            if ifc.name.lower() == target_iface_name.lower():
                                target_iface = ifc
                                break
                    else:
                        target_iface = target_node.interfaces[0] if target_node.interfaces else None

                    if not target_iface or not target_iface.ipv4_address:
                        feedback_msg = f"Device '{target_node.name}' has no IPv4 address configured on interface."
                    elif expected_val and target_iface.ipv4_address != str(expected_val).strip():
                        feedback_msg = f"IP is {target_iface.ipv4_address}, but expected {expected_val}."
                    else:
                        is_ok = True
                        feedback_msg = f"Interface '{target_iface.name}' configured with IP {target_iface.ipv4_address}."

            elif rule_type == "SUBNET_MATCH":
                peer_name = str(expected_val)
                peer_node = name_map.get(peer_name.lower()) or node_map.get(peer_name)
                if not target_node or not peer_node:
                    feedback_msg = f"Could not find both devices '{target_dev_name}' and '{peer_name}'."
                else:
                    ifc1 = target_node.interfaces[0] if target_node.interfaces else None
                    ifc2 = peer_node.interfaces[0] if peer_node.interfaces else None
                    if not ifc1 or not ifc1.ipv4_address or not ifc2 or not ifc2.ipv4_address:
                        feedback_msg = "Both devices must have configured IPv4 addresses to compare subnets."
                    else:
                        same = are_same_subnet(
                            ifc1.ipv4_address,
                            ifc1.subnet_mask or "255.255.255.0",
                            ifc2.ipv4_address,
                            ifc2.subnet_mask or "255.255.255.0",
                        )
                        is_ok = same
                        feedback_msg = f"{target_node.name} and {peer_node.name} share the same local subnet." if same else f"{target_node.name} ({ifc1.ipv4_address}) and {peer_node.name} ({ifc2.ipv4_address}) are on different subnets."

            elif rule_type == "GATEWAY_MATCH":
                if not target_node:
                    feedback_msg = f"Device '{target_dev_name}' is missing."
                else:
                    ifc = target_node.interfaces[0] if target_node.interfaces else None
                    gw = ifc.default_gateway if ifc else None
                    if not gw:
                        feedback_msg = f"Device '{target_node.name}' has no default gateway configured."
                    elif expected_val and gw != str(expected_val).strip():
                        feedback_msg = f"Default gateway is {gw}, expected {expected_val}."
                    else:
                        is_ok = True
                        feedback_msg = f"Default gateway correctly configured as {gw}."

            elif rule_type == "ROUTE_EXISTS":
                if not target_node:
                    feedback_msg = f"Router '{target_dev_name}' is missing."
                else:
                    routes = target_node.configuration.routing_table
                    dest_expected = rule.get("destination", str(expected_val))
                    has_route = any(
                        r.destination == dest_expected or (dest_expected in ("default", "0.0.0.0/0") and r.destination in ("0.0.0.0", "default"))
                        for r in routes
                    )
                    is_ok = has_route
                    feedback_msg = f"Route to {dest_expected} is configured on {target_node.name}." if is_ok else f"Missing route to {dest_expected} in {target_node.name} routing table."

            elif rule_type == "PING_SUCCESS":
                src_dev = target_node
                dst_name = str(expected_val)
                dst_dev = name_map.get(dst_name.lower()) or node_map.get(dst_name)

                if not src_dev or not dst_dev:
                    feedback_msg = f"Source '{target_dev_name}' or destination '{dst_name}' missing."
                else:
                    # Run quick authoritative ping simulation
                    sim_req = SimulatePacketRequest(
                        topology=topology,
                        source_device_id=src_dev.id,
                        destination_device_id=dst_dev.id,
                        protocol="ICMP",
                    )
                    sim_res = simulation_engine.simulate(sim_req)
                    is_ok = sim_res.success
                    feedback_msg = sim_res.summary if is_ok else f"Ping failed: {sim_res.failure_reason}"

            elif rule_type == "VLAN_MATCH":
                if not target_node:
                    feedback_msg = f"Switch '{target_dev_name}' is missing."
                else:
                    expected_vlan = int(expected_val) if expected_val else 1
                    target_iface = None
                    if target_iface_name:
                        for ifc in target_node.interfaces:
                            if ifc.name.lower() == target_iface_name.lower():
                                target_iface = ifc
                                break
                    else:
                        target_iface = target_node.interfaces[0] if target_node.interfaces else None

                    if not target_iface:
                        feedback_msg = f"Port '{target_iface_name}' not found on {target_node.name}."
                    elif target_iface.vlan_id != expected_vlan:
                        feedback_msg = f"Port '{target_iface.name}' is in VLAN {target_iface.vlan_id}, expected VLAN {expected_vlan}."
                    else:
                        is_ok = True
                        feedback_msg = f"Port '{target_iface.name}' is correctly assigned to VLAN {expected_vlan}."

            elif rule_type == "FIREWALL_RULE":
                if not target_node:
                    feedback_msg = f"Firewall '{target_dev_name}' is missing."
                else:
                    expected_action = rule.get("action", "ALLOW").upper()
                    expected_proto = rule.get("protocol", "ANY").upper()
                    rules_list = target_node.configuration.firewall_rules
                    matched_rule = any(
                        r.action.upper() == expected_action and (expected_proto == "ANY" or r.protocol.upper() == expected_proto)
                        for r in rules_list
                    )
                    is_ok = matched_rule
                    feedback_msg = f"Firewall rule {expected_action} {expected_proto} is present." if is_ok else f"Missing firewall policy: {expected_action} {expected_proto}."

            else:
                is_ok = True
                feedback_msg = desc

            if is_ok:
                passed_count += 1

            task_results.append({
                "rule_index": idx + 1,
                "description": desc,
                "passed": is_ok,
                "message": feedback_msg,
            })

        total = len(rules) if rules else 1
        all_passed = (passed_count == len(rules)) and (len(rules) > 0)
        # Score computation: deduct 5 points per hint used, floor at 50 if passed
        base_score = int((passed_count / total) * 100)
        final_score = max(50 if all_passed else 0, base_score - (request.hints_used * 5)) if all_passed else base_score

        overall_msg = (
            "Congratulations! All scenario objectives verified successfully."
            if all_passed
            else f"{passed_count} of {total} objectives achieved. Inspect the failed tasks and retry."
        )

        return ScenarioValidationResultResponse(
            is_passed=all_passed,
            score=final_score,
            tasks_passed=passed_count,
            total_tasks=total,
            task_results=task_results,
            feedback=overall_msg,
            solution_explanation=solution_explanation if all_passed else None,
        )


simulator_validation_service = SimulatorValidationService()
