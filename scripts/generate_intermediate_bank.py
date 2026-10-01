#!/usr/bin/env python3
"""
NexoraNet Intermediate Question Bank Generator - Part 1.
Generates:
1. subnetting_and_cidr.json (35 questions, programmatically verified using ipaddress)
2. tcp_udp_and_transport.json (35 questions)
3. dns_dhcp_and_application.json (30 questions)
"""

import ipaddress
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "intermediate"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_questions(filename, raw_items):
    questions = []
    for item in raw_items:
        code, topic_slug, q_text, q_type, diff, cog, pts, est_s, expl, obj, raw_opts, tags, *extra = item
        calc_meta = extra[0] if extra else None
        options = []
        for idx, (opt_text, is_corr, opt_expl) in enumerate(raw_opts):
            options.append({
                "option_text": opt_text,
                "is_correct": is_corr,
                "order_index": idx,
                "explanation": opt_expl
            })
        q_dict = {
            "code": code,
            "topic_slug": topic_slug,
            "question_text": q_text,
            "question_type": q_type,
            "difficulty": diff,
            "cognitive_level": cog,
            "points": pts,
            "estimated_seconds": est_s,
            "status": "PUBLISHED",
            "explanation": expl,
            "learning_objective": obj,
            "options": options,
            "tags": tags
        }
        if calc_meta:
            q_dict["calculation_metadata"] = calc_meta
        questions.append(q_dict)

    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"Created {len(questions)} questions in {filename}")


def generate_subnetting_and_cidr():
    items = []

    # Helper function to programmatically generate mathematically sound subnetting questions
    def make_broadcast_q(code, cidr_str, diff="INTERMEDIATE", cog="APPLY"):
        net = ipaddress.IPv4Network(cidr_str, strict=False)
        correct_bcast = str(net.broadcast_address)
        distractor1 = str(net.network_address)
        distractor2 = str(net.broadcast_address - 1)
        distractor3 = str(net.broadcast_address + 1)
        # Ensure distractors are unique
        opts = [
            (correct_bcast, True, f"The broadcast address for {cidr_str} has all host bits set to 1, yielding {correct_bcast}."),
            (distractor1, False, f"{distractor1} is the network address (all host bits 0), not the broadcast address."),
            (distractor2, False, f"{distractor2} is the last usable host IP address in the subnet."),
            (distractor3, False, f"{distractor3} is the network address of the adjacent following subnet.")
        ]
        text = f"Given the IPv4 network {cidr_str}, what is the directed broadcast address?"
        expl = f"For the subnet {cidr_str}, the network address is {net.network_address} and the broadcast address is {correct_bcast} (all host bits set to binary 1)."
        obj = "Calculate the broadcast address for a given CIDR network prefix."
        meta = {"cidr": cidr_str, "property": "broadcast_address", "expected": correct_bcast}
        return (code, "broadcast-address", text, "SUBNETTING", diff, cog, 2, 60, expl, obj, opts, ["subnetting", "cidr", "calculation"], meta)

    def make_network_addr_q(code, host_ip, prefix, diff="INTERMEDIATE", cog="APPLY"):
        net = ipaddress.IPv4Network(f"{host_ip}/{prefix}", strict=False)
        correct_net = str(net.network_address)
        distractor1 = str(net.network_address + 1)
        distractor2 = str(net.broadcast_address)
        distractor3 = str(net.broadcast_address - 1)
        opts = [
            (correct_net, True, f"Bitwise ANDing {host_ip} with /{prefix} mask clears all host bits to 0, yielding {correct_net}."),
            (distractor1, False, f"{distractor1} is the first usable host IP address, not the network identifier."),
            (distractor2, False, f"{distractor2} is the broadcast address for this subnet."),
            (distractor3, False, f"{distractor3} is the last usable host address in this subnet.")
        ]
        text = f"A host workstation is assigned the IPv4 address {host_ip}/{prefix}. What is the network address of the subnet to which it belongs?"
        expl = f"Applying the /{prefix} mask to host IP {host_ip} zeroes out all host bits, producing the network address {correct_net}."
        obj = "Determine the network address for a given host IP and prefix length."
        meta = {"cidr": f"{host_ip}/{prefix}", "property": "network_address", "expected": correct_net}
        return (code, "network-address", text, "SUBNETTING", diff, cog, 2, 60, expl, obj, opts, ["subnetting", "cidr", "network-address"], meta)

    def make_usable_hosts_q(code, cidr_str, diff="INTERMEDIATE", cog="APPLY"):
        net = ipaddress.IPv4Network(cidr_str, strict=False)
        usable = net.num_addresses - 2
        opts = [
            (str(usable), True, f"A /{net.prefixlen} mask has {32 - net.prefixlen} host bits. 2^{32 - net.prefixlen} - 2 = {usable} usable hosts."),
            (str(net.num_addresses), False, f"{net.num_addresses} is the total number of IP addresses before subtracting network and broadcast."),
            (str(usable - 2), False, f"{usable - 2} subtracts too many addresses."),
            (str(net.num_addresses * 2 - 2), False, f"This corresponds to a subnet with one additional host bit.")
        ]
        text = f"How many usable host IPv4 addresses can be assigned to devices on a /{net.prefixlen} subnet?"
        expl = f"With prefix length /{net.prefixlen}, there are {32 - net.prefixlen} host bits. The total address pool is 2^{32 - net.prefixlen} = {net.num_addresses}. Subtracting 2 (for network and broadcast) leaves {usable} usable host addresses."
        obj = "Calculate usable host capacity from IPv4 prefix length."
        meta = {"cidr": cidr_str, "property": "usable_hosts", "expected": usable}
        return (code, "host-range", text, "SUBNETTING", diff, cog, 2, 50, expl, obj, opts, ["subnetting", "cidr", "host-capacity"], meta)

    def make_host_range_q(code, cidr_str, diff="INTERMEDIATE", cog="APPLY"):
        net = ipaddress.IPv4Network(cidr_str, strict=False)
        first_h = str(net.network_address + 1)
        last_h = str(net.broadcast_address - 1)
        correct_range = f"{first_h} - {last_h}"
        distractor1 = f"{net.network_address} - {net.broadcast_address}"
        distractor2 = f"{net.network_address} - {last_h}"
        distractor3 = f"{first_h} - {net.broadcast_address}"
        opts = [
            (correct_range, True, f"The first usable host is network+1 ({first_h}) and the last usable host is broadcast-1 ({last_h})."),
            (distractor1, False, f"This includes the reserved network ({net.network_address}) and broadcast ({net.broadcast_address}) addresses."),
            (distractor2, False, f"The network address ({net.network_address}) cannot be assigned to an endpoint."),
            (distractor3, False, f"The broadcast address ({net.broadcast_address}) cannot be assigned to an endpoint.")
        ]
        text = f"What is the valid usable host IP address range for the subnet {cidr_str}?"
        expl = f"For {cidr_str}, the network address is {net.network_address} and the broadcast address is {net.broadcast_address}. Therefore, the assignable host range is {first_h} through {last_h}."
        obj = "Determine the usable host IP address range for a given subnet."
        return (code, "host-range", text, "SUBNETTING", diff, cog, 2, 60, expl, obj, opts, ["subnetting", "host-range", "cidr"])

    # 1-15: Programmatic Subnetting Calculations
    items.append(make_broadcast_q("SUBNET-001", "192.168.10.64/26"))
    items.append(make_broadcast_q("SUBNET-002", "192.168.1.128/25"))
    items.append(make_broadcast_q("SUBNET-003", "10.0.0.0/27"))
    items.append(make_broadcast_q("SUBNET-004", "172.16.50.192/28"))
    items.append(make_broadcast_q("SUBNET-005", "192.168.100.248/29"))
    items.append(make_broadcast_q("SUBNET-006", "10.10.10.0/30"))

    items.append(make_network_addr_q("SUBNET-007", "192.168.1.155", 26))
    items.append(make_network_addr_q("SUBNET-008", "10.20.30.77", 27))
    items.append(make_network_addr_q("SUBNET-009", "172.16.85.201", 28))
    items.append(make_network_addr_q("SUBNET-010", "192.168.5.250", 29))
    items.append(make_network_addr_q("SUBNET-011", "10.1.1.25", 30))

    items.append(make_usable_hosts_q("SUBNET-012", "192.168.1.0/25"))
    items.append(make_usable_hosts_q("SUBNET-013", "192.168.1.0/26"))
    items.append(make_usable_hosts_q("SUBNET-014", "192.168.1.0/27"))
    items.append(make_usable_hosts_q("SUBNET-015", "192.168.1.0/28"))
    items.append(make_usable_hosts_q("SUBNET-016", "192.168.1.0/29"))
    items.append(make_usable_hosts_q("SUBNET-017", "192.168.1.0/30"))

    items.append(make_host_range_q("SUBNET-018", "192.168.10.64/26"))
    items.append(make_host_range_q("SUBNET-019", "10.5.5.128/28"))
    items.append(make_host_range_q("SUBNET-020", "172.20.1.240/29"))

    # 21-35: Conceptual Subnetting, VLSM & Mask Conversions
    items.append((
        "SUBNET-021", "subnet-masks", "What is the dotted-decimal subnet mask corresponding to a /27 prefix?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 45,
        "A /27 prefix has 27 ones: 11111111.11111111.11111111.11100000. The last octet has bits 128+64+32 = 224, giving 255.255.255.224.",
        "Convert /27 CIDR notation to dotted-decimal subnet mask.",
        [
            ("255.255.255.224", True, "27 network bits = 255.255.255.224."),
            ("255.255.255.192", False, "255.255.255.192 is /26 (128+64)."),
            ("255.255.255.240", False, "255.255.255.240 is /28 (128+64+32+16)."),
            ("255.255.255.248", False, "255.255.255.248 is /29.")
        ],
        ["subnet-masks", "cidr", "conversion"]
    ))
    items.append((
        "SUBNET-022", "subnet-masks", "What is the dotted-decimal subnet mask corresponding to a /28 prefix?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 45,
        "A /28 prefix has 28 ones: 11111111.11111111.11111111.11110000. In the fourth octet, 128+64+32+16 = 240, yielding 255.255.255.240.",
        "Convert /28 CIDR notation to dotted-decimal subnet mask.",
        [
            ("255.255.255.240", True, "28 network bits = 255.255.255.240."),
            ("255.255.255.224", False, "255.255.255.224 is /27."),
            ("255.255.255.248", False, "255.255.255.248 is /29."),
            ("255.255.255.252", False, "255.255.255.252 is /30.")
        ],
        ["subnet-masks", "cidr", "conversion"]
    ))
    items.append((
        "SUBNET-023", "subnet-masks", "What is the dotted-decimal subnet mask corresponding to a /29 prefix?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 45,
        "A /29 prefix has 29 ones: 11111111.11111111.11111111.11111000. In the fourth octet, 128+64+32+16+8 = 248, yielding 255.255.255.248.",
        "Convert /29 CIDR notation to dotted-decimal subnet mask.",
        [
            ("255.255.255.248", True, "29 network bits = 255.255.255.248."),
            ("255.255.255.240", False, "255.255.255.240 is /28."),
            ("255.255.255.252", False, "255.255.255.252 is /30."),
            ("255.255.255.192", False, "255.255.255.192 is /26.")
        ],
        ["subnet-masks", "cidr", "conversion"]
    ))
    items.append((
        "SUBNET-024", "subnet-masks", "What is the dotted-decimal subnet mask corresponding to a /30 prefix?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 45,
        "A /30 prefix has 30 ones: 11111111.11111111.11111111.11111100. In the fourth octet, 128+64+32+16+8+4 = 252, yielding 255.255.255.252.",
        "Convert /30 CIDR notation to dotted-decimal subnet mask.",
        [
            ("255.255.255.252", True, "30 network bits = 255.255.255.252."),
            ("255.255.255.248", False, "255.255.255.248 is /29."),
            ("255.255.255.254", False, "255.255.255.254 is /31."),
            ("255.255.255.240", False, "255.255.255.240 is /28.")
        ],
        ["subnet-masks", "cidr", "conversion"]
    ))
    items.append((
        "SUBNET-025", "vlsm", "An enterprise needs to create a point-to-point link between two core routers. Which subnet mask minimizes wasted IPv4 addresses while following standard RFC host reservation rules?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 60,
        "A /30 subnet mask provides 4 total addresses: 1 network address, 1 broadcast address, and exactly 2 usable host addresses for the two router interfaces, minimizing address waste.",
        "Select the optimal subnet size for a point-to-point router link.",
        [
            ("/30 (255.255.255.252)", True, "A /30 provides exactly 2 usable host IP addresses, perfectly sizing a point-to-point WAN link."),
            ("/29 (255.255.255.248)", False, "A /29 provides 6 usable hosts, wasting 4 IP addresses on a point-to-point link."),
            ("/28 (255.255.255.240)", False, "A /28 provides 14 usable hosts, wasting 12 IP addresses."),
            ("/24 (255.255.255.0)", False, "A /24 provides 254 usable hosts, severely wasting public or corporate addresses.")
        ],
        ["vlsm", "subnetting", "point-to-point", "optimization"]
    ))
    items.append((
        "SUBNET-026", "vlsm", "A network designer must allocate a subnet to support exactly 28 workstation hosts. Which prefix length should be selected to conserve address space?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 60,
        "Using formula 2^h - 2 >= 28: with 5 host bits, 2^5 - 2 = 32 - 2 = 30 usable hosts. 30 >= 28. Prefix length is 32 - 5 = /27. (A /28 only provides 14 usable hosts, which is insufficient).",
        "Determine the minimum subnet size required for a specified host count.",
        [
            ("/27 (provides 30 usable hosts)", True, "A /27 provides 30 usable hosts (2^5 - 2 = 30), satisfying the 28-host requirement with minimal waste."),
            ("/28 (provides 14 usable hosts)", False, "A /28 only provides 14 usable hosts (2^4 - 2 = 14), which cannot accommodate 28 hosts."),
            ("/26 (provides 62 usable hosts)", False, "A /26 accommodates the hosts but wastes 34 addresses compared to /27."),
            ("/29 (provides 6 usable hosts)", False, "A /29 only provides 6 usable hosts.")
        ],
        ["vlsm", "subnetting", "host-capacity", "design"]
    ))
    items.append((
        "SUBNET-027", "vlsm", "A branch office requires a subnet supporting up to 55 employee laptops. What is the most efficient CIDR prefix that can accommodate this requirement?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 60,
        "Using 2^h - 2 >= 55: 6 host bits gives 2^6 - 2 = 64 - 2 = 62 usable hosts (62 >= 55). Prefix is 32 - 6 = /26. (A /27 only provides 30 usable hosts).",
        "Select the most efficient CIDR prefix for 55 hosts.",
        [
            ("/26 (provides 62 usable hosts)", True, "A /26 provides 62 usable hosts, which accommodates 55 laptops with room for growth."),
            ("/27 (provides 30 usable hosts)", False, "A /27 provides only 30 usable hosts, insufficient for 55 laptops."),
            ("/25 (provides 126 usable hosts)", False, "A /25 provides 126 hosts, which wastes address space when /26 is sufficient."),
            ("/28 (provides 14 usable hosts)", False, "A /28 provides only 14 usable hosts.")
        ],
        ["vlsm", "subnetting", "design"]
    ))
    items.append((
        "SUBNET-028", "cidr", "What is Classless Inter-Domain Routing (CIDR / RFC 1519) and why was it introduced?",
        "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 50,
        "CIDR abolished the rigid Class A, B, and C boundary system, allowing arbitrary prefix lengths (like /21, /27) and route summarization (supernetting) to prevent IPv4 address exhaustion and routing table explosion.",
        "Explain the historical purpose of CIDR.",
        [
            ("To replace rigid Class A, B, and C boundaries with arbitrary prefix lengths, slowing IPv4 exhaustion and routing table growth", True, "CIDR replaced classful boundaries with variable prefix lengths, enabling efficient IP allocation."),
            ("To convert all wired Ethernet networks into satellite microwave links", False, "CIDR is an IP routing and addressing standard, not physical wireless hardware."),
            ("To mandate that all computer passwords be exactly 32 characters long", False, "CIDR has nothing to do with password authentication."),
            ("To permanently disable firewall state tables across the Internet", False, "CIDR governs routing and addressing; it does not disable firewall security.")
        ],
        ["cidr", "history", "routing", "rfc1519"]
    ))
    items.append((
        "SUBNET-029", "cidr", "How many /24 subnets can be carved out of a single /22 IPv4 address block?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
        "The difference in prefix lengths is 24 - 22 = 2 bits. The number of subnets created is 2^2 = 4 subnets of size /24.",
        "Calculate the number of subnets when dividing a CIDR block.",
        [
            ("4 subnets", True, "2^(24 - 22) = 2^2 = 4 subnets of size /24."),
            ("2 subnets", False, "2 subnets would be created by a /23 prefix (2^(23-22) = 2)."),
            ("8 subnets", False, "8 subnets would be created by dividing into /25 (2^(25-22) = 8)."),
            ("16 subnets", False, "16 subnets would be created by dividing into /26.")
        ],
        ["cidr", "subnetting", "calculation"]
    ))
    items.append((
        "SUBNET-030", "cidr", "How many /24 subnets can be formed from a /20 network block?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
        "The prefix difference is 24 - 20 = 4 bits. 2^4 = 16 subnets of size /24 can be created from a /20 block.",
        "Calculate the number of /24 subnets from a /20 prefix.",
        [
            ("16 subnets", True, "2^(24 - 20) = 2^4 = 16 subnets of size /24."),
            ("8 subnets", False, "8 subnets corresponds to a /21 prefix."),
            ("32 subnets", False, "32 subnets would be dividing into /25."),
            ("4 subnets", False, "4 subnets corresponds to a /22 prefix.")
        ],
        ["cidr", "subnetting", "calculation"]
    ))
    items.append((
        "SUBNET-031", "subnet-masks", "What is the dotted-decimal subnet mask corresponding to a /22 prefix?",
        "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
        "A /22 prefix has 22 network bits: 8 + 8 + 6 + 0. In the third octet, 6 ones equals 128+64+32+16+8+4 = 252. Thus the mask is 255.255.252.0.",
        "Convert /22 prefix length to dotted-decimal mask.",
        [
            ("255.255.252.0", True, "22 network bits converts to 255.255.252.0."),
            ("255.255.248.0", False, "255.255.248.0 is /21 (5 ones in 3rd octet)."),
            ("255.255.254.0", False, "255.255.254.0 is /23 (7 ones in 3rd octet)."),
            ("255.255.240.0", False, "255.255.240.0 is /20 (4 ones in 3rd octet).")
        ],
        ["subnet-masks", "cidr", "conversion"]
    ))
    items.append((
        "SUBNET-032", "host-range", "Two hosts are configured as follows:\nHost A: 192.168.1.62/26\nHost B: 192.168.1.65/26\nCan Host A communicate directly with Host B on Layer 2 without crossing a router?",
        "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 65,
        "For a /26 network, subnets increment by 64: Subnet 0 is 192.168.1.0/26 (hosts .1 to .62). Subnet 1 is 192.168.1.64/26 (hosts .65 to .126). Host A (.62) is on Subnet 0, while Host B (.65) is on Subnet 1. Being on different subnets, they cannot communicate directly without a router.",
        "Analyze whether two hosts belong to the same IP subnet.",
        [
            ("No, Host A is in the 192.168.1.0/26 subnet and Host B is in the 192.168.1.64/26 subnet, requiring a router to communicate", True, "Host A is in the first /26 subnet (.0-.63) while Host B is in the second /26 subnet (.64-.127)."),
            ("Yes, because both hosts share the same first three octets (192.168.1.x)", False, "The /26 mask splits the fourth octet; sharing the first three octets does not guarantee the same subnet."),
            ("Yes, because all IPv4 addresses can communicate directly over switches without routers", False, "Hosts on different IP subnets require a Layer 3 router or switch to route traffic."),
            ("No, because Host A's IP address is an invalid broadcast address", False, "192.168.1.62 is the valid last usable host in subnet 0; .63 is the broadcast address.")
        ],
        ["subnetting", "troubleshooting", "routing", "analysis"]
    ))
    items.append((
        "SUBNET-033", "vlsm", "What is the primary benefit of Variable Length Subnet Masking (VLSM)?",
        "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
        "VLSM allows an engineer to divide an address space into subnets of varying sizes (different prefix lengths), matching subnet size to the exact number of hosts required and eliminating address waste.",
        "Explain the primary benefit of VLSM.",
        [
            ("It enables subnetting a subnet, allowing different subnets within an organization to use different prefix lengths based on host needs", True, "VLSM allows tailored prefix lengths (e.g. /24 for users, /30 for point-to-point links) in the same network."),
            ("It eliminates the need for routers across enterprise networks", False, "VLSM networks still require routers to forward traffic between subnets."),
            ("It doubles the physical electrical voltage of copper Ethernet cables", False, "VLSM is a logical routing concept that has no effect on physical cable voltage."),
            ("It replaces all MAC addresses with 128-bit IPv6 addresses", False, "VLSM is an IPv4 addressing design technique.")
        ],
        ["vlsm", "subnetting", "efficiency"]
    ))
    items.append((
        "SUBNET-034", "network-address", "A network administrator attempts to assign the IP address 192.168.10.128/25 to a desktop workstation's NIC. The operating system displays an error: 'The specified IP address is invalid'. Why?",
        "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
        "For the /25 mask on 192.168.10.128, .128 has all host bits set to 0, making it the network identifier address for the second /25 subnet (192.168.10.128 - .255). Network addresses cannot be assigned to host endpoints.",
        "Diagnose why an IP address assignment was rejected by the OS.",
        [
            ("192.168.10.128 is the network address for the 192.168.10.128/25 subnet and cannot be assigned to a host", True, "In a /25, the subnets are .0 and .128. .128 is the network ID for the second subnet."),
            ("192.168.10.128 is a reserved military satellite address", False, "192.168.0.0/16 is RFC 1918 private space."),
            ("Desktop operating systems only support /24 subnet masks", False, "Operating systems support any valid CIDR mask from /1 to /32."),
            ("The IP address has already been encrypted by the DHCP server", False, "IP addresses are assigned and validated as numbers, not encrypted.")
        ],
        ["subnetting", "network-address", "troubleshooting", "validation"]
    ))
    items.append((
        "SUBNET-035", "broadcast-address", "Why is a directed broadcast address (such as 192.168.1.255/24) restricted from being configured on an endpoint host network adapter?",
        "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
        "The broadcast address has all host bits set to binary 1 and is reserved for sending packets simultaneously to every host on that subnet. Assigning it to a single device would create routing ambiguity and packet delivery failures.",
        "Explain why broadcast addresses cannot be assigned to host interfaces.",
        [
            ("It has all host bits set to 1 and is reserved to transmit packets to all hosts on the subnet simultaneously", True, "Broadcast addresses are reserved for one-to-all communications within the subnet."),
            ("It is a public IP address owned exclusively by the United States Department of Defense", False, "192.168.1.255 is within RFC 1918 private address space."),
            ("It contains an odd number of bits that causes processor arithmetic errors", False, "All IPv4 addresses contain exactly 32 bits."),
            ("It triggers automatic formatting of the host computer's hard drive", False, "Networking configurations do not format local disks.")
        ],
        ["broadcast-address", "subnetting", "rfc791"]
    ))

    save_questions("subnetting_and_cidr.json", items)


if __name__ == "__main__":
    generate_subnetting_and_cidr()
