#!/usr/bin/env python3
"""
NexoraNet Intermediate Question Bank Generator - Part 3.
Generates:
4. routing_and_switching.json (35 questions)
5. firewalls_nat_and_troubleshooting.json (30 questions)
Completes the full 165-question Intermediate Bank!
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "intermediate"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_questions(filename, raw_items):
    questions = []
    for item in raw_items:
        code, topic_slug, q_text, q_type, diff, cog, pts, est_s, expl, obj, raw_opts, tags = item
        options = []
        for idx, (opt_text, is_corr, opt_expl) in enumerate(raw_opts):
            options.append({
                "option_text": opt_text,
                "is_correct": is_corr,
                "order_index": idx,
                "explanation": opt_expl
            })
        questions.append({
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
        })
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"Created {len(questions)} questions in {filename}")


def generate_routing_and_switching():
    items = [
        (
            "ROUT-001", "switching", "How does a Layer 2 switch dynamically populate its MAC address table (CAM table)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "A switch inspects the SOURCE MAC address of every incoming frame received on an ingress port, mapping that source MAC address to that specific physical switch port in its MAC table.",
            "Explain how Ethernet switches learn MAC addresses.",
            [
                ("By inspecting the SOURCE MAC address of incoming frames and recording the ingress switch port", True, "Switches learn dynamically from incoming source MAC addresses."),
                ("By querying the local DNS server for the host's domain name", False, "DNS resolves IP addresses to hostnames; it does not populate switch MAC tables."),
                ("By reading the destination IP address in the Layer 3 header", False, "Layer 2 switches do not evaluate Layer 3 IP headers for CAM table learning."),
                ("By measuring electrical copper resistance on the wire", False, "Switches read digital bit streams in frame headers, not cable resistance.")
            ],
            ["switching", "mac-address-table", "layer2", "learning"]
        ),
        (
            "ROUT-002", "switching", "What action does an Ethernet switch take when it receives a unicast frame destined for a MAC address that is NOT present in its MAC address table?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "When the destination MAC is unknown, the switch performs 'Unknown Unicast Flooding': it floods (broadcasts) the frame out of all active ports within that VLAN, except the port on which the frame was received.",
            "Explain unknown unicast flooding in Ethernet switches.",
            [
                ("It floods the frame out of all ports within the same VLAN, except the port where it arrived (Unknown Unicast Flooding)", True, "The switch floods unknown unicasts so the true destination can receive it and reply, allowing the switch to learn its port."),
                ("It drops the frame immediately and sends an ICMP Host Unreachable packet", False, "Layer 2 switches do not drop unknown unicasts or generate ICMP packets."),
                ("It transmits the frame across the Internet using satellite links", False, "Layer 2 frames do not route across the Internet."),
                ("It shuts down the switch power supply to prevent a network loop", False, "Flooding is normal, expected Layer 2 forwarding behavior.")
            ],
            ["switching", "unknown-unicast-flooding", "cam-table"]
        ),
        (
            "ROUT-003", "mac-address-table", "What happens to dynamic entries in a switch's MAC address table when no frames are observed from a host for the aging timer duration (typically 300 seconds)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "The aging timer ensures the CAM table does not retain stale entries when devices disconnect or move. If no frames are received from that MAC before the timer expires, the entry is deleted from the table.",
            "Explain MAC address table aging mechanics.",
            [
                ("The entry is aged out and deleted from the table to prevent stale port mappings", True, "Aging removes inactive device mappings so table space is preserved and moved devices can be relearned."),
                ("The switch permanently blacklists the MAC address from ever connecting again", False, "Aging out is normal maintenance; the MAC is relearned immediately when it transmits again."),
                ("The switch sends an automated email alert to the local police department", False, "Aging out is standard Layer 2 table maintenance."),
                ("The switch formats its internal flash firmware", False, "Flash memory is not formatted by CAM aging.")
            ],
            ["mac-address-table", "aging-timer", "switching"]
        ),
        (
            "ROUT-004", "vlan", "What is the primary architectural purpose of configuring Virtual Local Area Networks (VLANs) on enterprise switches?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "VLANs partition a physical switch into multiple isolated logical broadcast domains, improving network performance (limiting broadcast traffic), security (preventing unauthorized lateral access), and management.",
            "Explain the benefits of VLAN segmentation.",
            [
                ("To divide a physical local network into separate logical broadcast domains, improving performance and security", True, "VLANs isolate broadcast domains and segment departments logically on shared physical switches."),
                ("To allow computers to operate without needing physical network interface cards", False, "Computers still require physical NICs to connect to switch ports."),
                ("To automatically double the download speed of video files from YouTube", False, "VLANs manage broadcast domains, not Internet streaming bandwidth."),
                ("To eliminate the need for IP addressing entirely", False, "Each VLAN corresponds to a distinct IP subnet and requires IP addressing.")
            ],
            ["vlan", "broadcast-domain", "segmentation", "switching"]
        ),
        (
            "ROUT-005", "trunking", "What industry-standard protocol is used to tag Ethernet frames traversing a trunk link between switches with their originating VLAN ID?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "IEEE 802.1Q is the universal industry-standard trunking protocol that inserts a 4-byte VLAN tag (containing a 12-bit VLAN ID) into the Ethernet frame header between the Source MAC and EtherType fields.",
            "Identify the standard VLAN trunking protocol.",
            [
                ("IEEE 802.1Q", True, "IEEE 802.1Q inserts a 4-byte tag identifying the frame's VLAN ID over trunk links."),
                ("IEEE 802.11ac", False, "802.11ac is a Wi-Fi wireless standard."),
                ("IEEE 802.3af", False, "802.3af is a Power over Ethernet (PoE) standard."),
                ("Cisco ISL", False, "Inter-Switch Link (ISL) was a legacy proprietary Cisco encapsulation replaced by 802.1Q.")
            ],
            ["trunking", "vlan", "802.1q", "switching"]
        ),
        (
            "ROUT-006", "trunking", "What is the 'Native VLAN' on an IEEE 802.1Q trunk link?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "The Native VLAN is the single configured VLAN on an 802.1Q trunk that carries untagged traffic. Any frame that traverses the trunk without an 802.1Q tag is automatically treated as belonging to the Native VLAN.",
            "Explain the behavior of the Native VLAN on 802.1Q trunks.",
            [
                ("The specific VLAN designated to carry untagged frames across an 802.1Q trunk link", True, "Frames belonging to the native VLAN are sent across the trunk without an 802.1Q tag."),
                ("A VLAN that can only be accessed by wireless smartphones", False, "Native VLAN is a wired switch trunking concept."),
                ("The encrypted master VLAN where switch passwords are stored", False, "Native VLAN carries ordinary untagged traffic, not encrypted passwords."),
                ("A VLAN that deletes all packets passing through it", False, "Native VLAN forwards untagged traffic normally.")
            ],
            ["trunking", "native-vlan", "802.1q", "switching"]
        ),
        (
            "ROUT-007", "vlan", "Why can two computers on the same physical switch configured in different VLANs (e.g. VLAN 10 and VLAN 20) NOT communicate directly without a Layer 3 device?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "VLANs are separate Layer 2 broadcast domains and separate IP subnets. Switches enforce strict Layer 2 isolation between different VLANs; forwarding traffic between distinct subnets requires a Layer 3 router or multilayer switch.",
            "Explain the requirement for inter-VLAN routing.",
            [
                ("VLANs are isolated Layer 2 broadcast domains; forwarding traffic between different subnets requires Layer 3 routing", True, "A Layer 3 device (router or multilayer switch) is strictly required to route between distinct VLAN subnets."),
                ("VLAN 20 automatically encrypts all packets so VLAN 10 cannot read them", False, "Isolation is enforced by switch port tagging logic, not payload encryption."),
                ("Computers in VLAN 20 are physically located on a different planet", False, "Both VLANs can exist on the same physical switch in the same server rack."),
                ("Ethernet cables can only carry one letter of the alphabet at a time", False, "Cabling transmits binary bit streams.")
            ],
            ["vlan", "inter-vlan-routing", "layer2-vs-layer3"]
        ),
        (
            "ROUT-008", "vlan", "What is the 'Router-on-a-Stick' inter-VLAN routing topology?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "In Router-on-a-Stick, a single physical router interface connects to a switch trunk port using multiple logical sub-interfaces (e.g. g0/0.10, g0/0.20), routing traffic between VLANs over the shared trunk.",
            "Define the Router-on-a-Stick architectural model.",
            [
                ("A single physical router interface connects via an 802.1Q trunk to a switch, using logical sub-interfaces to route between VLANs", True, "Router-on-a-Stick uses sub-interfaces with dot1q encapsulation to route inter-VLAN traffic across a single link."),
                ("A wooden stick placed between two switches to prevent physical vibrations", False, "This is literal wordplay, not an engineering architecture."),
                ("A router mounted on a satellite dish orbiting the earth", False, "Router-on-a-stick is standard enterprise rack routing."),
                ("A wireless ad-hoc connection between two mobile smartphones", False, "It is a wired Ethernet trunk topology.")
            ],
            ["inter-vlan-routing", "router-on-a-stick", "sub-interfaces"]
        ),
        (
            "ROUT-009", "routing", "What fundamental rule governs how a router selects the winning route in its routing table when multiple matching routes exist for a destination IP?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "The Longest Prefix Match (most specific route) rule: the router always chooses the route with the longest prefix length (most network bits matching the destination IP, e.g. /28 beats /24, which beats /16).",
            "State the Longest Prefix Match rule in IP routing.",
            [
                ("Longest Prefix Match: the router always selects the route with the most specific prefix length matching the destination IP", True, "Longest prefix match dictates that more specific routes (higher prefix /N) always take precedence."),
                ("Shortest Prefix Match: the router always prefers the route with the fewest bits matching", False, "Shortest match is incorrect; more specific routes always win."),
                ("Alphabetical Match: the route whose interface name begins with the earliest letter", False, "Routing decisions are based on binary IP prefix matching, not interface names."),
                ("Random Choice: the router flips a digital coin to select a route", False, "IP forwarding is strictly deterministic based on longest prefix match.")
            ],
            ["routing", "longest-prefix-match", "routing-table"]
        ),
        (
            "ROUT-010", "default-routes", "What is the destination IP address and subnet mask notation for an IPv4 Default Route (the 'Gateway of Last Resort')?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "An IPv4 default route matches all destination addresses with a zero-length prefix: 0.0.0.0/0 (IP 0.0.0.0 with subnet mask 0.0.0.0).",
            "Identify the IPv4 default route syntax.",
            [
                ("0.0.0.0/0 (0.0.0.0 0.0.0.0)", True, "0.0.0.0/0 matches any IP address when no more specific route exists in the routing table."),
                ("255.255.255.255/32", False, "255.255.255.255/32 is the limited broadcast address."),
                ("127.0.0.1/8", False, "127.0.0.1/8 is the loopback network."),
                ("192.168.1.1/24", False, "192.168.1.1/24 is a specific Class C subnet.")
            ],
            ["routing", "default-routes", "gateway-of-last-resort"]
        ),
        (
            "ROUT-011", "static-routing", "What is a major operational advantage of static routing compared to dynamic routing protocols?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Static routes require zero CPU processing overhead for protocol calculation, consume zero network link bandwidth for routing updates, and provide predictable, administrator-controlled traffic paths.",
            "Identify advantages of static routing.",
            [
                ("Low CPU/memory overhead and zero routing update traffic traversing the network links", True, "Static routes do not consume router CPU or bandwidth for neighbor hellos and route recalculation."),
                ("Automatic rerouting around failed links without administrator intervention", False, "Static routes cannot automatically adapt to topology changes unless combined with IP SLA/tracking."),
                ("Automatic assignment of IP addresses to all office computers", False, "DHCP assigns IP addresses, not static routes."),
                ("Physical immunity against severed fiber-optic cables", False, "Cut cables break connectivity regardless of routing type.")
            ],
            ["routing", "static-routing", "dynamic-routing"]
        ),
        (
            "ROUT-012", "dynamic-routing-concepts", "What is the primary operational advantage of dynamic routing protocols (such as OSPF and BGP) over static routes?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Dynamic routing protocols automatically discover remote networks, share topology information between neighbor routers, and automatically calculate and reroute traffic around failed links without manual intervention.",
            "Explain the benefit of dynamic routing protocols.",
            [
                ("They automatically detect link failures and dynamically recalculate alternative paths around network outages", True, "Dynamic protocols provide automated convergence and fault-tolerant rerouting."),
                ("They eliminate the need for electrical power supplies in routers", False, "Routers require electrical power."),
                ("They encrypt all user files on Windows desktop workstations", False, "Routing protocols share network reachability data, not file encryption."),
                ("They increase the download speed of the Internet to infinity", False, "Throughput is bounded by physical link capacities.")
            ],
            ["routing", "dynamic-routing", "convergence", "ospf"]
        ),
        (
            "ROUT-013", "dynamic-routing-concepts", "In Cisco and standard routing architecture, what does 'Administrative Distance' (AD) represent?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Administrative Distance measures the trustworthiness or believability of a routing source when multiple routing protocols learn a route to the exact same destination prefix. Lower AD values indicate higher trustworthiness.",
            "Define Administrative Distance.",
            [
                ("A metric measuring the trustworthiness of a routing source; lower values indicate higher believability", True, "When multiple protocols offer routes to the same prefix, the router chooses the source with the lowest AD."),
                ("The physical distance in kilometers between two router server chassis", False, "AD is a logical believability ranking, not geographical distance."),
                ("The number of seconds before a router password expires", False, "AD has no relation to password management."),
                ("The amount of electricity consumed by the router power supply", False, "AD is a routing table selection metric.")
            ],
            ["routing", "administrative-distance", "routing-table"]
        ),
        (
            "ROUT-014", "dynamic-routing-concepts", "What is the default Administrative Distance (AD) of a directly connected network interface that is up and configured with an IP address?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "Directly connected networks have an Administrative Distance of 0, making them the most trusted routing source in the routing table.",
            "Recall AD for directly connected routes.",
            [
                ("0", True, "Directly connected routes have an AD of 0 (most trusted)."),
                ("1", False, "Static routes standardly have an AD of 1."),
                ("110", False, "110 is the default AD for OSPF on Cisco routers."),
                ("90", False, "90 is the default AD for internal EIGRP.")
            ],
            ["routing", "administrative-distance", "directly-connected"]
        ),
        (
            "ROUT-015", "dynamic-routing-concepts", "What is the default Administrative Distance (AD) of a standard static route pointing to a next-hop IP on Cisco routers?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "A standard static route configured with a next-hop IP has an Administrative Distance of 1.",
            "Recall AD for standard static routes.",
            [
                ("1", True, "Static routes standardly have an Administrative Distance of 1."),
                ("0", False, "0 is for directly connected interfaces."),
                ("110", False, "110 is OSPF."),
                ("120", False, "120 is RIP.")
            ],
            ["routing", "administrative-distance", "static-routes"]
        ),
        (
            "ROUT-016", "dynamic-routing-concepts", "What is a 'Floating Static Route' and how is it configured?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "A floating static route is an administrative backup static route configured with a higher Administrative Distance than the primary dynamic routing protocol (e.g. AD 120 vs OSPF 110). It remains dormant until the primary route fails.",
            "Explain floating static route configuration and purpose.",
            [
                ("A backup static route configured with a higher Administrative Distance that only becomes active if the primary dynamic route fails", True, "Floating static routes provide backup redundancy by having an intentionally worse AD than primary dynamic routes."),
                ("A route that moves dynamically between different Wi-Fi access points", False, "Floating static routes are manual static route configurations on routers."),
                ("A route designed to connect computers floating on marine boats", False, "The term 'floating' refers to AD precedence, not maritime operations."),
                ("A route that automatically changes its destination IP address every hour", False, "Static routes have fixed destination prefixes.")
            ],
            ["routing", "floating-static-route", "redundancy"]
        ),
        (
            "ROUT-017", "routing", "What is the Time to Live (TTL) field in the IPv4 header used for during packet forwarding?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "TTL is an 8-bit hop counter that prevents packets from looping endlessly through a network. Every router that forwards the packet decrements the TTL by 1. If TTL hits 0, the packet is dropped and an ICMP Time Exceeded is returned.",
            "Explain loop prevention via the IPv4 TTL field.",
            [
                ("It is decremented by 1 at each router hop; when it reaches 0, the packet is discarded to prevent infinite routing loops", True, "TTL bounds the lifetime of packets and terminates forwarding loops."),
                ("It specifies how many seconds the user has to read an email message", False, "TTL in IP headers is a hop counter, not an email countdown."),
                ("It measures the physical temperature of the copper cable in Celsius", False, "Network headers manage routing logic, not cable thermodynamics."),
                ("It forces the packet to travel in reverse order across the country", False, "TTL does not reverse packet trajectory.")
            ],
            ["routing", "ttl", "loop-prevention", "ipv4"]
        ),
        (
            "ROUT-018", "routing", "Which ICMP message is returned to the sending host when a router decrements a packet's TTL to zero?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "When a router decrements the TTL to 0, it drops the packet and generates an ICMP Type 11, Code 0 message: 'Time-to-Live exceeded in transit'. (This mechanism is what powers the 'traceroute' diagnostic tool).",
            "Identify the ICMP message sent upon TTL expiration.",
            [
                ("ICMP Time Exceeded (Type 11, Code 0)", True, "ICMP Time Exceeded notifies the sender that a packet exceeded its hop limit."),
                ("ICMP Echo Reply (Type 0)", False, "Echo Reply responds to ping."),
                ("ICMP Redirect (Type 5)", False, "Redirect informs a host of a better first-hop router."),
                ("TCP RST", False, "RST is a transport-layer flag, not an ICMP message.")
            ],
            ["icmp", "ttl", "time-exceeded", "traceroute"]
        ),
        (
            "ROUT-019", "switching", "What is a 'Broadcast Storm' on an Ethernet switch network and what causes it?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "A broadcast storm occurs when redundant Layer 2 links exist between switches without Spanning Tree Protocol (STP). Broadcast frames (like ARP requests) circulate and multiply indefinitely in an infinite loop, saturating CPU and switch links until the network collapses.",
            "Analyze the cause and impact of Layer 2 broadcast storms.",
            [
                ("An endless circulation and multiplication of broadcast frames caused by redundant Layer 2 links without Spanning Tree Protocol", True, "Layer 2 frames lack a TTL field; loops circulate broadcast frames forever, consuming 100% of bandwidth and switch CPU."),
                ("A sudden thunderstorm that physically strikes outdoor Wi-Fi towers", False, "A broadcast storm is a logical switching loop phenomenon, not meteorology."),
                ("A hacker sending 10,000 spam emails to employees", False, "Broadcast storms occur at Layer 2 inside the switch fabric, not in mailboxes."),
                ("A failure in the building's electrical power grid", False, "Broadcast storms happen while switches are fully powered and functional.")
            ],
            ["switching", "broadcast-storm", "layer2-loops", "troubleshooting"]
        ),
        (
            "ROUT-020", "switching", "Which protocol is standardly used on enterprise Ethernet switches to eliminate Layer 2 loops and prevent broadcast storms?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "Spanning Tree Protocol (STP / IEEE 802.1D or RSTP IEEE 802.1w) automatically detects redundant physical links, places designated redundant ports in a blocking state, and dynamically unblocks them if the primary link fails.",
            "Identify the protocol that prevents switching loops.",
            [
                ("Spanning Tree Protocol (STP / RSTP)", True, "STP blocks redundant paths to create a loop-free logical tree topology."),
                ("Border Gateway Protocol (BGP)", False, "BGP is an exterior gateway routing protocol for the Internet."),
                ("Dynamic Host Configuration Protocol (DHCP)", False, "DHCP assigns IP configurations."),
                ("Domain Name System (DNS)", False, "DNS resolves domain names.")
            ],
            ["switching", "stp", "rstp", "loop-prevention"]
        ),
        (
            "ROUT-021", "vlan", "What is 'VLAN Hopping' in network penetration testing and security assessment?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "VLAN Hopping is an attack technique (via Switch Spoofing using DTP or Double Tagging 802.1Q frames) where an adversary on one VLAN injects traffic into a different unauthorized VLAN, bypassing Layer 2 segmentation.",
            "Define the concept of a VLAN Hopping attack.",
            [
                ("An attack method (such as switch spoofing or double tagging) that allows an attacker on one VLAN to send traffic into an unauthorized target VLAN", True, "VLAN hopping exploits trunking misconfigurations or double 802.1Q tags to bypass VLAN boundaries."),
                ("A legitimate network optimization tool that increases switch throughput by 200%", False, "VLAN hopping is an adversarial attack technique."),
                ("A wireless feature that automatically switches between 2.4 GHz and 5 GHz Wi-Fi", False, "That is band steering, not VLAN hopping."),
                ("A protocol used to track stolen laptops across international borders", False, "VLAN hopping is a local Layer 2 attack.")
            ],
            ["vlan", "vlan-hopping", "switch-security", "attack-techniques"]
        ),
        (
            "ROUT-022", "vlan", "Which two configuration practices mitigate VLAN Hopping attacks on enterprise switch access ports?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
            "To prevent VLAN hopping: 1. Explicitly configure end-user ports as access ports (`switchport mode access`) and disable Dynamic Trunking Protocol (`switchport nonegotiate`), 2. Change the native VLAN on trunks away from default VLAN 1 to an unused dedicated VLAN.",
            "Apply defensive controls against VLAN hopping.",
            [
                ("Disable DTP negotiation on access ports and change the native VLAN on trunks away from default VLAN 1", True, "Disabling DTP prevents switch spoofing, and changing native VLAN neutralizes double tagging attacks."),
                ("Assign all employees to the same master administrator VLAN", False, "Consolidating everyone onto one VLAN destroys segmentation."),
                ("Remove all Ethernet switches and replace them with unmanaged hubs", False, "Hubs have no VLAN support and allow universal packet sniffing."),
                ("Disable passwords across all network administration portals", False, "Removing passwords severely compromises security.")
            ],
            ["vlan", "vlan-hopping-defense", "switch-hardening", "security"]
        ),
        (
            "ROUT-023", "switching", "What is the difference between a collision domain and a broadcast domain?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "A collision domain is a network segment where simultaneous packet transmissions can collide (each switch port is its own collision domain). A broadcast domain is the network scope where a broadcast frame reaches all nodes (delimited by routers or VLANs).",
            "Differentiate collision domains and broadcast domains.",
            [
                ("A collision domain is isolated to each switch port; a broadcast domain spans all ports in a VLAN and is bounded by routers", True, "Switches break up collision domains (microsegmentation); routers break up broadcast domains."),
                ("Collision domains only exist on Wi-Fi; broadcast domains only exist on copper", False, "Both concepts apply across wired and wireless network architectures."),
                ("Collision domains encrypt traffic; broadcast domains decrypt traffic", False, "Neither domain concept involves cryptographic encryption."),
                ("Collision domains are illegal under international telecommunication law", False, "They are fundamental networking topology concepts.")
            ],
            ["switching", "collision-domain", "broadcast-domain", "architecture"]
        ),
        (
            "ROUT-024", "switching", "How many collision domains and how many broadcast domains are created by a 24-port unmanaged Layer 2 Ethernet switch configured with default settings (all ports in default VLAN 1)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "On a standard Layer 2 switch, each individual port operates in full duplex as its own isolated collision domain (24 collision domains). Since all ports reside in a single VLAN without routers, there is exactly 1 broadcast domain.",
            "Calculate collision and broadcast domains on a 24-port switch.",
            [
                ("24 collision domains and 1 broadcast domain", True, "Each switch port is an independent collision domain (24), while VLAN 1 encompasses all 24 ports in 1 broadcast domain."),
                ("1 collision domain and 24 broadcast domains", False, "That would describe a 24-port router, not a switch."),
                ("1 collision domain and 1 broadcast domain", False, "That describes a legacy 24-port network hub."),
                ("24 collision domains and 24 broadcast domains", False, "That would require 24 separate VLANs or 24 routed interfaces.")
            ],
            ["switching", "collision-domain", "broadcast-domain", "calculation"]
        ),
        (
            "ROUT-025", "routing", "Given the following routing table entries:\n1. 10.0.0.0/8 via 192.168.1.1\n2. 10.1.0.0/16 via 192.168.1.2\n3. 10.1.1.0/24 via 192.168.1.3\n4. 0.0.0.0/0 via 192.168.1.254\nWhich next-hop router will receive a packet destined for 10.1.1.55?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "The destination 10.1.1.55 matches routes 1, 2, 3, and 4. Under Longest Prefix Match, route 3 (/24) has the longest prefix length (24 matching bits), so the packet is forwarded to next-hop 192.168.1.3.",
            "Apply longest prefix match to resolve forwarding next-hop.",
            [
                ("192.168.1.3 (matched by 10.1.1.0/24)", True, "10.1.1.0/24 is the longest prefix match (/24 beats /16, /8, and /0)."),
                ("192.168.1.2 (matched by 10.1.0.0/16)", False, "/16 is a shorter match than /24."),
                ("192.168.1.1 (matched by 10.0.0.0/8)", False, "/8 is a shorter match than /24."),
                ("192.168.1.254 (matched by 0.0.0.0/0)", False, "The default route is the least specific match.")
            ],
            ["routing", "longest-prefix-match", "routing-table", "analysis"]
        ),
        (
            "ROUT-026", "switching", "What is 'Port Security' on an enterprise switch access port?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Port Security restricts which devices can connect to a specific switch port by limiting the number of allowed MAC addresses and binding specific learned or static MACs to that port, dropping frames or disabling the port (err-disable) upon violation.",
            "Explain switch Port Security functionality.",
            [
                ("A feature that limits the MAC addresses permitted to transmit on a switch port, shutting down or dropping traffic from unauthorized MACs", True, "Port security prevents unauthorized devices from plugging into enterprise wall jacks."),
                ("A physical padlock that wraps around the RJ-45 cable", False, "Port security is a switch operating system software feature."),
                ("A password required by web browsers before opening Google", False, "Port security is a Layer 2 switch feature, not a web browser login."),
                ("An antivirus scanner that removes trojans from USB thumb drives", False, "Port security manages Ethernet frame source MACs on switch interfaces.")
            ],
            ["switching", "port-security", "defense", "layer2-security"]
        ),
        (
            "ROUT-027", "switching", "In switch Port Security, what occurs when a violation occurs under the 'shutdown' violation mode?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Under shutdown mode (the standard default), an unauthorized MAC address immediately puts the switch port into an 'err-disabled' state, turning off the port and logging an SNMP trap/syslog message until manually or automatically reset.",
            "Identify the behavior of port security shutdown mode.",
            [
                ("The port is immediately disabled and placed into the 'err-disabled' state, shutting off link light and logging the violation", True, "Shutdown mode disables the physical port until an administrator intervenes or err-disable recovery runs."),
                ("The switch explodes with a loud electrical spark", False, "Network devices do not physically detonate upon security violations."),
                ("The unauthorized device's hard drive is wiped automatically", False, "Switches cannot format endpoint hard drives over Ethernet."),
                ("The port permits the unauthorized device to access the executive network", False, "Shutdown mode strictly blocks all communication.")
            ],
            ["switching", "port-security", "err-disable", "security"]
        ),
        (
            "ROUT-028", "switching", "What is a 'MAC Flooding Attack' and what is the attacker's objective?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "In a MAC flooding attack (e.g. using macof), the attacker sends thousands of frames with randomized fake source MAC addresses to overflow the switch's CAM table. Once full, the switch enters fail-open hub mode, broadcasting all subsequent unicast traffic out of all ports, allowing sniffing.",
            "Analyze MAC table overflow (CAM flooding) attacks.",
            [
                ("Flooding the switch with thousands of fake source MACs to exhaust CAM memory, forcing the switch to act like a hub and broadcast all traffic for sniffing", True, "CAM exhaustion forces the switch into fail-open mode, broadcasting frames so the attacker can sniff traffic."),
                ("Water flooding into the server room through open windows", False, "MAC flooding is a network frame flood attack, not plumbing water damage."),
                ("A protocol used to synchronize time across Apple Mac computers", False, "NTP synchronizes time; MAC flooding is an adversarial attack."),
                ("An attack that doubles the user's internet bill", False, "MAC flooding targets local switch forwarding memory.")
            ],
            ["switching", "mac-flooding", "cam-table", "sniffing", "security"]
        ),
        (
            "ROUT-029", "switching", "What does 'Static MAC Binding' accomplish on a switch port?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "Static MAC binding manually associates a specific MAC address with a designated switch port, ensuring that only that specific pre-registered hardware device can transmit on that port.",
            "Explain static MAC binding.",
            [
                ("It permanently binds a specific hardware MAC address to an assigned switch port, preventing unauthorized replacement devices", True, "Static MAC binding enforces strict hardware-to-port mapping."),
                ("It automatically reboots the switch every 24 hours", False, "MAC binding does not trigger periodic reboots."),
                ("It converts copper cabling into optical fiber signals", False, "MAC binding is a Layer 2 configuration table entry."),
                ("It assigns a public IP address to the workstation", False, "IP address allocation is handled by IPAM/DHCP.")
            ],
            ["switching", "mac-address", "port-security"]
        ),
        (
            "ROUT-030", "routing", "What is a 'Routing Loop' in an IP network?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "A routing loop occurs when misconfigured routing tables or slow convergence cause two or more routers to forward packets for a destination back and forth to each other in a circle, consuming link bandwidth until TTL expires.",
            "Define the concept of an IP routing loop.",
            [
                ("A condition where packets are forwarded continuously in an endless circle between routers due to routing table inconsistencies", True, "Routing loops circulate packets until the IPv4 TTL or IPv6 Hop Limit reaches zero."),
                ("A circular optical fiber cable installed around a running track", False, "Routing loop is a logical forwarding defect, not physical athletics tracks."),
                ("A legitimate feature used to test the physical speed of light in fiber", False, "Routing loops are errors that degrade network performance."),
                ("An encryption technique that repeats passwords three times", False, "Routing loops are forwarding path flaws, not encryption algorithms.")
            ],
            ["routing", "routing-loops", "troubleshooting", "convergence"]
        ),
        (
            "ROUT-031", "dynamic-routing-concepts", "What is 'Convergence Time' in dynamic routing protocols?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Convergence time is the time required for all routers across an autonomous system or network to detect a topology change, share routing updates, recalculate best paths, and update their routing tables to agree on the new network state.",
            "Define routing protocol convergence time.",
            [
                ("The time taken for all routers in a network to learn of a topology change and establish consistent routing tables", True, "Faster convergence minimizes packet loss and blackholes during link failures."),
                ("The time required to install a physical router into a 19-inch equipment rack", False, "Hardware mounting time is physical installation, not protocol convergence."),
                ("The lifespan in years of an enterprise router's internal battery", False, "Convergence time is measured in seconds or milliseconds."),
                ("The time it takes for a user to log in with their password", False, "Authentication latency is unrelated to routing convergence.")
            ],
            ["dynamic-routing", "convergence", "routing-protocols"]
        ),
        (
            "ROUT-032", "dynamic-routing-concepts", "Which routing protocol metric is standardly used by Open Shortest Path First (OSPF)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "OSPF uses 'Cost' as its metric, which is inversely proportional to the bandwidth of the link (Cost = Reference Bandwidth / Interface Bandwidth), preferring higher-speed links over slower links.",
            "Recall the metric used by OSPF.",
            [
                ("Cost (inversely proportional to interface bandwidth)", True, "OSPF calculates cost based on link bandwidth, preferring faster links."),
                ("Hop Count (number of routers traversed)", False, "Hop count is the metric for Routing Information Protocol (RIP)."),
                ("Delay and Reliability only", False, "EIGRP uses a composite metric including bandwidth, delay, reliability, and load."),
                ("Financial cost in US dollars per gigabyte", False, "Routing metrics measure technical network parameters, not accounting bills.")
            ],
            ["routing", "ospf", "metric", "cost"]
        ),
        (
            "ROUT-033", "dynamic-routing-concepts", "What is the maximum hop count allowed by the legacy Routing Information Protocol (RIP) before a destination is marked as unreachable?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "RIP defines a maximum hop count of 15; a hop count of 16 represents infinity (unreachable), preventing infinite counting-to-infinity routing loops in small networks.",
            "Recall RIP maximum hop count.",
            [
                ("15 hops (16 is considered unreachable / infinite)", True, "RIP limits network diameter to 15 hops to prevent count-to-infinity loops."),
                ("255 hops", False, "255 is the maximum value of an 8-bit TTL field."),
                ("100 hops", False, "100 is the default hop limit for EIGRP."),
                ("65535 hops", False, "RIP cannot support networks of that diameter.")
            ],
            ["routing", "rip", "hop-count", "distance-vector"]
        ),
        (
            "ROUT-034", "static-routing", "What syntax on a Cisco router configures a static route to the 10.20.0.0/16 network via next-hop router IP 192.168.1.1?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "The standard Cisco command syntax is: 'ip route <destination-network> <subnet-mask> <next-hop-ip>': 'ip route 10.20.0.0 255.255.0.0 192.168.1.1'.",
            "Identify static route configuration syntax on Cisco IOS.",
            [
                ("ip route 10.20.0.0 255.255.0.0 192.168.1.1", True, "This follows the standard syntax: ip route <dest> <mask> <next-hop>."),
                ("route add 10.20.0.0 to 192.168.1.1 with mask 255.255.0.0", False, "This is not valid Cisco IOS syntax."),
                ("router ospf 10.20.0.0 192.168.1.1", False, "This is invalid OSPF configuration syntax."),
                ("ip default-gateway 10.20.0.0", False, "ip default-gateway is used for Layer 2 switch management, not static routing.")
            ],
            ["static-routing", "cisco", "cli", "syntax"]
        ),
        (
            "ROUT-035", "switching", "What is an 802.1Q 'Trunk Port' on a switch compared to an 'Access Port'?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "An Access Port belongs to exactly one VLAN and carries untagged frames for endpoint devices (PCs, printers). A Trunk Port carries traffic for multiple VLANs simultaneously, multiplexing them with 802.1Q tags between switches or routers.",
            "Compare switch access ports and trunk ports.",
            [
                ("An access port carries traffic for a single VLAN; a trunk port carries multiplexed traffic for multiple VLANs using 802.1Q tags", True, "Access ports connect end-user hosts; trunk ports interconnect switches and routers."),
                ("An access port only works at 10 Mbps; a trunk port works at 100 Gbps", False, "Both port types operate at whatever physical speed the switch hardware supports."),
                ("An access port encrypts traffic; a trunk port decrypts traffic", False, "Port operational modes do not govern cryptographic encryption."),
                ("A trunk port can only be installed in the trunk of a car", False, "Trunk is a telecommunications term for a shared aggregate multiplexed link.")
            ],
            ["switching", "access-port", "trunk-port", "vlan"]
        ),
    ]
    save_questions("routing_and_switching.json", items)


def generate_firewalls_nat_troubleshooting():
    items = [
        (
            "FW-001", "nat", "What is the primary function of Network Address Translation (NAT / RFC 1631)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "NAT modifies IP address information in packet headers while they are in transit across a boundary router, translating private non-routable IP addresses (RFC 1918) into public globally routable IP addresses to access the Internet.",
            "Explain the core purpose of Network Address Translation.",
            [
                ("To translate private non-routable IPv4 addresses into public globally routable IP addresses for Internet access", True, "NAT conserves public IPv4 addresses and enables private networks to reach the public Internet."),
                ("To convert optical fiber pulses into acoustic sound waves", False, "NAT is a network layer packet translation protocol, not an audio conversion tool."),
                ("To encrypt all hard drives across the corporate domain", False, "NAT translates IP headers; it does not encrypt storage drives."),
                ("To force all computers to reboot at midnight", False, "NAT has nothing to do with scheduled reboots.")
            ],
            ["nat", "rfc1918", "routing", "internet-access"]
        ),
        (
            "FW-002", "nat", "What form of NAT maps thousands of internal private IP addresses to a SINGLE public IP address by tracking unique Layer 4 source port numbers?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Port Address Translation (PAT), also known as NAT Overload (or NAPT), tracks internal source IP and port combinations to map multiple private hosts to a single public IP address using distinct dynamic public ports.",
            "Identify Port Address Translation (NAT Overload).",
            [
                ("Port Address Translation (PAT / NAT Overload)", True, "PAT multiplexes many private IPs onto one public IP using source port tracking."),
                ("Static NAT (One-to-One NAT)", False, "Static NAT maps one private IP permanently to one public IP."),
                ("Dynamic NAT without overload", False, "Dynamic NAT maps from a pool of public IPs on a one-to-one basis until the pool is exhausted."),
                ("Border Gateway Protocol (BGP)", False, "BGP is a routing protocol, not address translation.")
            ],
            ["nat", "pat", "nat-overload", "ports"]
        ),
        (
            "FW-003", "nat", "In which scenario is 'Static NAT' (one-to-one mapping) standardly deployed?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "Static NAT is deployed for inbound access to internal servers (such as a public web server or mail server hosted in a DMZ) that must be reachable by external Internet users at a constant, consistent public IP address.",
            "Identify appropriate deployment scenarios for Static NAT.",
            [
                ("When an internal server (such as an enterprise web or mail server) must be reachable at a dedicated static public IP address", True, "Static NAT provides a permanent bidirectional 1:1 mapping so external clients can reach an internal server."),
                ("When an office has 500 mobile laptops browsing web pages simultaneously", False, "Outbound client browsing uses PAT (NAT Overload) to share a public IP."),
                ("When an Ethernet cable is shorter than 1 meter", False, "Cable lengths do not dictate NAT architecture."),
                ("When all computers must be disconnected from the network permanently", False, "NAT provides connectivity, not permanent isolation.")
            ],
            ["nat", "static-nat", "dmz", "servers"]
        ),
        (
            "FW-004", "nat-security", "Why is NAT considered an architectural security barrier for inbound unsolicited connections, even though it is not a dedicated firewall?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Under PAT, inbound packets from the Internet are dropped by default unless they match an existing entry in the router's active translation table that was initiated by an internal host, shielding internal endpoints from unsolicited incoming scans.",
            "Explain the incidental security shielding provided by PAT.",
            [
                ("External Internet hosts cannot initiate direct connections to internal private IPs unless a stateful translation mapping exists", True, "PAT rejects unsolicited inbound connection attempts because no corresponding entry exists in the translation table."),
                ("NAT physically melts any rogue cable that connects to the router", False, "NAT is software translation logic."),
                ("NAT encrypts all payloads with 4096-bit RSA keys", False, "NAT alters IP/port headers; it does not encrypt data payloads."),
                ("NAT blocks all web browsing on weekends", False, "NAT does not enforce calendar access schedules.")
            ],
            ["nat", "nat-security", "pat", "defense"]
        ),
        (
            "FW-005", "firewall-rules", "In what order are firewall Access Control List (ACL) rules evaluated when a packet arrives at an interface?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Firewall rules are evaluated sequentially from Top to Bottom (First Match). Once a packet matches a rule's criteria (permit or deny), that action is executed immediately, and evaluation stops without checking subsequent rules.",
            "Explain sequential top-down firewall rule evaluation.",
            [
                ("Top to bottom sequentially; once a packet matches a rule, that rule is applied and evaluation stops (First Match)", True, "Sequential first-match evaluation means rule order is critically important."),
                ("Bottom to top in reverse chronological order", False, "Firewalls evaluate rules from the top down."),
                ("Randomly chosen each time by the firewall processor", False, "Rule evaluation is strictly deterministic."),
                ("All rules are executed simultaneously, and the packet is permitted if any rule says yes", False, "Simultaneous execution would defeat specific drop rules placed above broad permit rules.")
            ],
            ["firewall", "firewall-rules", "acl", "rule-order"]
        ),
        (
            "FW-006", "firewall-rules", "A firewall administrator accidentally places the rule 'DENY ip any any' at line 1 of the inbound firewall policy. What will happen to inbound traffic?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 50,
            "Because rules are evaluated top-down with first-match semantics, 'DENY ip any any' at line 1 will match 100% of all incoming packets, immediately dropping all inbound traffic and rendering every rule below it useless.",
            "Analyze the impact of misordered firewall rules.",
            [
                ("All inbound traffic will be dropped immediately; all rules beneath line 1 will never be evaluated (Shadowed Rules)", True, "Placing a broad deny rule at the top shadows all subsequent permit rules, causing complete service outage."),
                ("The firewall will ignore line 1 and execute line 2 instead", False, "Firewalls strictly enforce rules in order."),
                ("The firewall will double the internet speed of the building", False, "Dropping all packets stops all network communication."),
                ("The router will automatically order a replacement firewall from Amazon", False, "Firewalls do not perform automated commercial purchases.")
            ],
            ["firewall", "firewall-rules", "shadowed-rules", "troubleshooting"]
        ),
        (
            "FW-007", "firewall-rules", "In firewall terminology, what is a 'Shadowed' or 'Redundant' rule?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "A shadowed rule is a rule located further down the ACL that can never be reached or executed because a preceding rule higher up in the list matches all the traffic that the lower rule would have matched.",
            "Define shadowed firewall rules.",
            [
                ("A rule that can never be evaluated because a broader rule preceding it in the list already matches all applicable traffic", True, "Shadowed rules are dead rules that represent administrative misconfigurations."),
                ("A rule that only works during a solar eclipse", False, "Shadowed is an access control list optimization term, not astronomical."),
                ("A rule created by an unauthenticated hacker in the shadows", False, "Shadowed rules are accidental administrative ordering mistakes."),
                ("A rule that encrypts web pages in black-and-white color", False, "Firewall rules govern packet permitting/blocking.")
            ],
            ["firewall", "firewall-rules", "shadowed-rules", "acl-audit"]
        ),
        (
            "FW-008", "firewall-rules", "Why is it important to place specific host rules (e.g. permit host 10.1.1.5) ABOVE broad subnet rules (e.g. deny 10.1.0.0/16) in a firewall policy?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
            "Because firewalls use first-match logic, if the broad deny rule were placed first, the specific host would be blocked along with the rest of the subnet. Placing the specific exception first allows it to be permitted before the general rule denies the rest.",
            "Apply rule ordering principles for specific exceptions.",
            [
                ("To allow the specific exception to match and be permitted before the broader rule denies the rest of the subnet", True, "Specific exceptions must always precede general broad policies in top-down rule evaluation."),
                ("Because firewalls can only read rules whose IP addresses end in an odd number", False, "Firewalls process all valid IP syntax."),
                ("To prevent the firewall from consuming too much electrical power", False, "Rule ordering impacts policy logic, not electrical power wattage."),
                ("To ensure that Google Chrome can update automatically", False, "Rule ordering applies to all network traffic.")
            ],
            ["firewall", "firewall-rules", "rule-ordering", "acl"]
        ),
        (
            "FW-009", "ids", "Where is a network Intrusion Detection System (NIDS) sensor standardly connected to monitor traffic without sitting in-line?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Passive NIDS sensors connect out-of-band to a switch SPAN (Switched Port Analyzer / Port Mirroring) port or a physical Network TAP (Test Access Point), which sends a copy of all passing frames to the sensor for deep packet inspection.",
            "Identify passive NIDS connection points.",
            [
                ("To a switch SPAN/mirror port or a physical Network TAP that provides a mirrored copy of network traffic", True, "SPAN ports and TAPs copy frames to passive monitoring tools without introducing in-line latency."),
                ("In-line between the CPU and the computer's RAM memory", False, "That would be a memory bus, not a network monitoring connection."),
                ("Directly to the building's electrical circuit breaker box", False, "NIDS sensors connect to network switches, not building electrical panels."),
                ("Inside the telephone handset receiver", False, "NIDS monitors Ethernet and IP network traffic.")
            ],
            ["ids", "nids", "span-port", "network-tap", "monitoring"]
        ),
        (
            "FW-010", "ips", "What is the primary risk of deploying an Intrusion Prevention System (IPS) in-line in 'blocking' mode?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "A False Positive (an alert erroneously classifying legitimate business traffic as malicious) in an in-line IPS will cause the IPS to actively drop legitimate business communications, potentially causing unexpected service outages.",
            "Analyze the operational risks of in-line IPS deployments.",
            [
                ("False Positives will result in legitimate business traffic being actively dropped, disrupting business operations", True, "In-line IPS actions must be carefully tuned to prevent dropping critical legitimate traffic."),
                ("The IPS will permanently delete the operating system from all client computers", False, "An IPS drops network packets; it does not delete client operating systems."),
                ("The IPS will cause copper Ethernet cables to dissolve into dust", False, "Software packet inspection does not damage physical cabling."),
                ("The IPS will force all web browsers to switch to Swedish language", False, "IPS does not modify web browser language localization.")
            ],
            ["ips", "false-positives", "inline", "risk-analysis", "soc"]
        ),
        (
            "FW-011", "network-segmentation", "In network architecture, what is a 'Microsegmentation' strategy?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "Microsegmentation creates granular, isolated security zones within data centers and cloud networks, restricting lateral (east-west) traffic between individual workloads, virtual machines, or containers to enforce Zero Trust.",
            "Define microsegmentation in modern enterprise networks.",
            [
                ("Granular security isolation that restricts lateral (east-west) communication between individual servers, VMs, or workloads", True, "Microsegmentation confines compromised workloads and blocks east-west lateral movement inside datacenters."),
                ("Cutting Ethernet cables into pieces smaller than one millimeter", False, "Microsegmentation is a logical security policy architecture, not cable cutting."),
                ("Allowing all devices on the network to share a single unencrypted password", False, "Sharing passwords destroys authentication."),
                ("Replacing all corporate servers with portable handheld calculators", False, "Microsegmentation applies to enterprise servers and cloud workloads.")
            ],
            ["network-segmentation", "microsegmentation", "zero-trust", "defense"]
        ),
        (
            "FW-012", "ping", "A network technician can successfully ping 127.0.0.1, but cannot ping their local default gateway (192.168.1.1). What does this diagnose?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "Pinging 127.0.0.1 proves that the local computer's TCP/IP stack software and protocol driver are operational. Failing to ping the default gateway points to a local Layer 1/2 physical link problem (cable unplugged, wrong VLAN, Wi-Fi disconnected, or gateway router down).",
            "Diagnose network faults using ping isolation.",
            [
                ("The local TCP/IP stack is functional, but there is a physical/data-link failure or network connectivity issue reaching the local gateway", True, "127.0.0.1 tests local protocol drivers; gateway failure isolates the fault to the local link or router interface."),
                ("The Internet has ceased to exist worldwide", False, "The issue is localized to the workstation's connection to its local gateway."),
                ("The computer's central processor has melted", False, "The OS is executing ping commands normally."),
                ("The DNS root server is rejecting the user's credit card", False, "Ping tested raw IP connectivity without using DNS or payments.")
            ],
            ["ping", "troubleshooting", "localhost", "default-gateway"]
        ),
        (
            "FW-013", "traceroute", "How does the 'traceroute' (or Windows 'tracert') command discover each intermediate router hop along a network path?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "Traceroute sends packets with incrementally increasing IP Time to Live (TTL) values, starting at TTL=1. Each intermediate router decrements TTL, expires it, and sends back an ICMP Time Exceeded message, revealing its IP address.",
            "Explain the technical mechanism of traceroute.",
            [
                ("It sends packets with incrementally increasing TTL values (TTL=1, 2, 3...), collecting ICMP Time Exceeded messages from each hop", True, "Each hop router drops the expired packet and reveals its identity via ICMP Time Exceeded (Type 11)."),
                ("It queries Google Maps for the geographical GPS coordinates of underground cables", False, "Traceroute uses IP TTL expiration, not mapping APIs."),
                ("It uses satellite imagery to take photos of router antenna towers", False, "Traceroute is a Layer 3 network diagnostic protocol."),
                ("It forces all routers to shut down and reboot in sequence", False, "Traceroute sends ordinary low-overhead diagnostic packets.")
            ],
            ["traceroute", "tracert", "ttl", "icmp", "troubleshooting"]
        ),
        (
            "FW-014", "traceroute", "In a traceroute output, what does an asterisk (*) displayed for a specific hop typically indicate?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "An asterisk (*) indicates that the traceroute probe timed out without receiving a response, commonly because the intermediate router is configured to drop ICMP/UDP probes or firewall rate-limiting is active.",
            "Interpret asterisks in traceroute output.",
            [
                ("The probe timed out without receiving a response (often due to firewall filtering or rate-limiting of ICMP)", True, "Many enterprise and carrier routers drop ICMP generation to prioritize routing traffic."),
                ("The router at that hop has physically exploded", False, "A timeout is standard router security/rate-limiting behavior."),
                ("The packet has traveled faster than the speed of light", False, "Physics limits transmission speed."),
                ("The user's computer screen has dead pixels", False, "Asterisks are text characters printed in terminal output.")
            ],
            ["traceroute", "icmp", "timeouts", "firewalls"]
        ),
        (
            "FW-015", "netstat-ss", "A cybersecurity analyst suspects a host is infected with command-and-control (C2) malware. Which command and flag combination reveals which executable process owns each active network connection on Windows?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "On Windows, 'netstat -anob' displays all active connections (a), numeric IP/ports (n), listening status (o: Process ID), and (b) displays the actual executable component name involved in creating each connection.",
            "Recall netstat flags to identify processes owning connections.",
            [
                ("netstat -anob", True, "The -b flag displays the executable program name associated with each connection (requires admin privilege)."),
                ("ping -t 127.0.0.1", False, "Ping sends continuous ICMP echo requests."),
                ("tracert -h 30", False, "Tracert maps router hops."),
                ("nslookup -type=mx", False, "Nslookup queries mail server records.")
            ],
            ["netstat", "incident-investigation", "process-tracking", "windows", "soc"]
        ),
        (
            "FW-016", "nslookup-dig-concepts", "Which command-line utility on Linux is standardly preferred over nslookup for performing detailed DNS queries and inspecting flags and authoritative authority sections?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "'dig' (Domain Information Groper) is the preferred diagnostic DNS tool on Linux/Unix, providing detailed query responses, TTL values, response flags, and root traversal options (+trace).",
            "Identify advanced DNS diagnostic command-line tools.",
            [
                ("dig", True, "dig provides comprehensive output for inspecting DNS records, response flags, and authority sections."),
                ("ipconfig", False, "Ipconfig displays local interface IP configurations on Windows."),
                ("fdisk", False, "fdisk partitions hard drives."),
                ("chown", False, "chown changes file ownership on Linux.")
            ],
            ["dns", "dig", "nslookup", "cli", "troubleshooting"]
        ),
        (
            "FW-017", "firewall-basics", "What is an Application Layer Firewall (Layer 7 / WAF / Web Application Firewall) and how does it differ from a standard Layer 4 firewall?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "A Layer 7 Web Application Firewall (WAF) inspects the actual application payload (HTTP headers, cookies, POST bodies, parameters) to detect application-level attacks like SQL Injection and Cross-Site Scripting (XSS), which Layer 4 firewalls cannot see.",
            "Contrast Layer 7 firewalls with Layer 4 packet filters.",
            [
                ("It inspects application payloads (HTTP requests, parameters) to detect application attacks like SQL Injection and XSS", True, "A WAF inspects Layer 7 data, whereas Layer 4 firewalls only examine IP addresses and port numbers."),
                ("It physically accelerates the rotational speed of server cooling fans", False, "Firewalls filter network packets."),
                ("It formats all incoming emails into Comic Sans font", False, "WAF inspects web security exploits."),
                ("It requires all users to write their passwords in cursive handwriting", False, "WAF does not alter human authentication handwriting.")
            ],
            ["firewall", "waf", "layer7", "sql-injection", "xss"]
        ),
        (
            "FW-018", "firewall-basics", "What is the security risk of leaving an administrative service (such as SSH on port 22 or RDP on port 3389) directly exposed to the public Internet without IP restriction or VPN?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "Publicly exposed administrative ports are subjected to continuous automated credential brute-force attacks, dictionary attacks, and immediate exploitation whenever zero-day or unpatched remote code execution vulnerabilities arise.",
            "Analyze risks of exposing administrative ports to the public Internet.",
            [
                ("Automated threat actor bots will continually launch brute-force password attacks and exploit unpatched vulnerabilities", True, "Internet-facing management ports are relentlessly scanned and attacked within minutes of exposure."),
                ("The operating system will automatically delete the user's web browser", False, "Administrative services do not delete web browsers."),
                ("The server will begin broadcasting FM radio music across the office", False, "Server network ports do not transmit commercial FM radio."),
                ("The local router will run out of physical Ethernet jacks", False, "Port exposure does not alter hardware jack counts.")
            ],
            ["security", "remote-access", "ssh", "rdp", "brute-force", "soc"]
        ),
        (
            "FW-019", "nat", "What is 'Hairpinning' (or NAT Loopback) in enterprise network routing?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "Hairpinning is a NAT feature that allows an internal LAN client to access an internal server (in the DMZ/LAN) using the server's public external IP address, with the router translating and looping the packet back internally.",
            "Explain NAT hairpinning.",
            [
                ("A feature that allows internal hosts to communicate with an internal server using the server's public IP address", True, "Hairpinning loops internal requests addressed to the public IP back into the local network."),
                ("A physical tool used by technicians to tie back long hair in server rooms", False, "Hairpinning is a routing and NAT loopback translation concept."),
                ("A security vulnerability that causes routers to overheat and catch fire", False, "Hairpinning is a legitimate routing feature."),
                ("A protocol used to download video files across BitTorrent", False, "Hairpinning is a router NAT policy.")
            ],
            ["nat", "hairpinning", "nat-loopback", "routing"]
        ),
        (
            "FW-020", "network-segmentation", "In network security architecture, what is 'East-West' traffic compared to 'North-South' traffic?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "North-South traffic flows in and out of the datacenter/enterprise perimeter (between internal hosts and the external Internet). East-West traffic flows laterally between servers and workstations inside the internal network.",
            "Contrast North-South and East-West network traffic.",
            [
                ("North-South flows between internal networks and the external Internet; East-West flows laterally between internal servers and workstations", True, "Perimeter firewalls filter North-South; microsegmentation filters East-West lateral movement."),
                ("North-South runs over copper; East-West runs over satellite", False, "Both traffic patterns use standard datacenter switching and cabling."),
                ("North-South is unencrypted; East-West is permanently deleted", False, "Both flows can be encrypted and monitored."),
                ("North-South applies only in the Northern Hemisphere", False, "These are topological directional metaphors independent of compass geography.")
            ],
            ["network-segmentation", "east-west", "north-south", "traffic-flows"]
        ),
        (
            "FW-021", "ping", "Why do many enterprise boundary firewalls and public web servers intentionally disable or rate-limit incoming ICMP Echo Requests (ping)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Disabling ICMP ping responses conceals hosts from casual network discovery scans, prevents ICMP flood Denial of Service attacks, and reduces unnecessary reconnaissance visibility to external adversaries.",
            "Explain why perimeter firewalls often block incoming ICMP ping.",
            [
                ("To conceal internal hosts from casual reconnaissance scans and mitigate ICMP flood DoS attacks", True, "Blocking inbound ICMP reduces attack surface discovery and prevents ping floods."),
                ("Because ICMP packets destroy the physical glass fibers inside optical cables", False, "ICMP packets are standard digital frames with no physical cable damage."),
                ("Because pinging a server causes it to automatically delete its database", False, "Ping does not modify server databases."),
                ("Because ICMP is strictly forbidden by federal law", False, "ICMP is a standard IETF protocol (RFC 792).")
            ],
            ["ping", "icmp", "firewall", "reconnaissance", "security"]
        ),
        (
            "FW-022", "traceroute", "A network analyst runs 'traceroute 8.8.8.8' on Linux and 'tracert 8.8.8.8' on Windows. What transport protocol does each operating system standardly use for its outgoing probes by default?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 2, 50,
            "By default, Windows 'tracert' sends ICMP Echo Request messages, while Linux/Unix 'traceroute' sends high-numbered UDP packets (typically ports 33434-33534).",
            "Compare Windows and Linux traceroute transport mechanisms.",
            [
                ("Windows uses ICMP Echo Requests; Linux standardly uses high-numbered UDP packets", True, "Windows sends ICMP by default; Linux sends UDP packets (though -I flag enables ICMP on Linux)."),
                ("Windows uses encrypted SSH; Linux uses unencrypted Telnet", False, "Traceroute does not use terminal management protocols."),
                ("Both use TCP SYN packets on port 443 exclusively", False, "Standard traceroute uses ICMP or UDP, though tcptraceroute exists as an alternative."),
                ("Both use Bluetooth radio transmissions", False, "Traceroute runs over IP networks.")
            ],
            ["traceroute", "windows", "linux", "icmp", "udp"]
        ),
        (
            "FW-023", "netstat-ss", "In netstat output, what does the socket state 'ESTABLISHED' signify?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 35,
            "'ESTABLISHED' indicates that the TCP three-way handshake completed successfully and the connection is currently open for bidirectional data transmission between client and server.",
            "Interpret the ESTABLISHED TCP socket state.",
            [
                ("The TCP three-way handshake completed and the connection is actively open for data transfer", True, "ESTABLISHED indicates an active, ongoing TCP session."),
                ("The connection has been aborted due to network failure", False, "Aborted connections enter CLOSED or generate RST."),
                ("The server is waiting for an Initial Sequence Number", False, "That would be SYN_RECEIVED."),
                ("The client has unplugged its physical Ethernet cable", False, "Connection states track protocol communication, not physical disconnects.")
            ],
            ["netstat", "tcp-states", "established"]
        ),
        (
            "FW-024", "netstat-ss", "In netstat output, what does the socket state 'LISTENING' signify?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 35,
            "'LISTENING' signifies that a local server application process has bound to a specific port and is waiting to accept incoming connection requests from remote clients.",
            "Interpret the LISTENING socket state.",
            [
                ("A local service process has bound to the port and is actively waiting to accept incoming connections", True, "LISTENING indicates an open service port ready to receive client handshakes."),
                ("The computer is eavesdropping on all office telephone calls", False, "LISTENING is a standard TCP socket state for local server daemons."),
                ("The hard drive is playing an audio podcast through the speakers", False, "Socket listening refers to network port readiness."),
                ("The network card has stopped working permanently", False, "Listening sockets demonstrate an active, operational protocol stack.")
            ],
            ["netstat", "tcp-states", "listening", "sockets"]
        ),
        (
            "FW-025", "firewall-basics", "What is an 'Egress Filtering' policy on an enterprise perimeter firewall?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Egress filtering inspects and restricts OUTBOUND traffic originating from internal networks destined for the Internet, preventing malware from communicating with C2 servers, blocking unauthorized protocol tunnels, and stopping data exfiltration.",
            "Explain the purpose of egress filtering.",
            [
                ("Restricting outbound traffic leaving the internal network to prevent malware C2 communication and data exfiltration", True, "Egress filtering stops internal compromised hosts from beaconing to malicious external command-and-control servers."),
                ("Filtering incoming spam emails from external marketing companies", False, "Inbound email inspection is ingress spam filtering."),
                ("Preventing users from turning off their office computer monitors", False, "Power settings are managed by OS group policies."),
                ("Cleaning dust out of physical ventilation fans", False, "Filtering in cybersecurity refers to network packet inspection.")
            ],
            ["firewall", "egress-filtering", "defense", "c2", "data-exfiltration"]
        ),
        (
            "FW-026", "firewall-rules", "An enterprise policy requires that all internal servers synchronize time via an external NTP pool (pool.ntp.org) over UDP port 123. What firewall rule should be configured on the outbound interface?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
            "The outbound rule must permit internal server source IPs to reach external destination IPs with protocol UDP and destination port 123: 'PERMIT udp <internal_servers> any eq 123'.",
            "Construct an outbound firewall access rule for NTP.",
            [
                ("PERMIT udp internal_servers any destination-port 123", True, "NTP uses UDP destination port 123 for network time synchronization."),
                ("PERMIT tcp internal_servers any destination-port 80", False, "TCP port 80 is HTTP, not NTP."),
                ("DENY udp any any destination-port 123", False, "This rule would block NTP synchronization."),
                ("PERMIT icmp any any type echo-request", False, "ICMP is ping, not time synchronization.")
            ],
            ["firewall-rules", "ntp", "acl", "configuration"]
        ),
        (
            "FW-027", "nat-security", "What is 'Double NAT' and why does it cause problems for peer-to-peer applications, VoIP, and gaming?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Double NAT occurs when two routers in series both perform NAT (e.g. an ISP gateway router connected to a customer's personal Wi-Fi router). This creates two private address tiers, breaking port forwarding, UPnP, and direct peer-to-peer connectivity.",
            "Explain the complications caused by Double NAT.",
            [
                ("Two cascading routers both perform address translation, breaking inbound port forwarding, UPnP, and VoIP/P2P sessions", True, "Double NAT creates two private subnets in sequence, preventing direct inbound routing and breaking session tracking."),
                ("The user is charged twice as much money by their Internet provider", False, "Double NAT is a routing/translation topology problem, not an ISP billing rate."),
                ("The computer downloads two copies of every file simultaneously", False, "Double NAT does not duplicate file downloads."),
                ("The Wi-Fi signals turn completely invisible", False, "Wi-Fi radio waves are naturally invisible.")
            ],
            ["nat", "double-nat", "troubleshooting", "voip"]
        ),
        (
            "FW-028", "ids-ips-advanced", "What is a 'False Negative' in intrusion detection systems, and why is it considered the most dangerous outcome for a security operations center (SOC)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "A False Negative occurs when a genuine attack or malicious activity occurs on the network, but the IDS/IPS fails to detect it and generates NO alert. It is the most dangerous condition because an attacker breaches the network completely undetected.",
            "Analyze the threat of False Negatives in security monitoring.",
            [
                ("A real attack occurs but the security system fails to detect it and generates zero alerts, leaving the breach undetected", True, "False negatives mean active intrusions proceed silently without security analyst awareness."),
                ("The security system generates 5,000 alerts for normal user web browsing", False, "That is a high False Positive rate."),
                ("The firewall power supply fails during a lightning storm", False, "That is a hardware power failure."),
                ("A user types an incorrect password into their email client", False, "That is an ordinary authentication failure.")
            ],
            ["ids", "soc", "false-negative", "detection-engineering", "risk"]
        ),
        (
            "FW-029", "ping", "What does the output 'Destination Host Unreachable' from a router indicate compared to 'Request Timed Out' during a ping test?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "'Destination Host Unreachable' is an ICMP message sent by a router indicating it has no route to the destination network or cannot resolve the host's MAC via ARP. 'Request Timed Out' means the packet was routed, but the destination never responded before the timer expired.",
            "Distinguish Host Unreachable from Request Timed Out.",
            [
                ("'Host Unreachable' is an explicit error from a router stating it cannot route to or find the host; 'Timed Out' means packets were sent but no reply was received before timeout", True, "Host Unreachable indicates routing or ARP failure at the gateway; Timed Out indicates the target or firewall dropped the packet silently."),
                ("'Host Unreachable' means the computer has no screen; 'Timed Out' means the computer has no keyboard", False, "These are IP network diagnostic messages independent of peripheral hardware."),
                ("Both messages mean the exact same thing with zero difference", False, "They indicate fundamentally different network failure modes."),
                ("'Timed Out' only occurs on computers running Windows 95", False, "Timeout is a universal network diagnostic response.")
            ],
            ["ping", "icmp", "troubleshooting", "host-unreachable", "timed-out"]
        ),
        (
            "FW-030", "nslookup-dig-concepts", "A user can ping external servers by their IP address (e.g. ping 8.8.8.8 succeeds), but typing 'ping google.com' returns 'Ping request could not find host google.com'. What is the root cause?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "Because IP ping succeeds, physical cabling, Layer 2 switching, Layer 3 routing, and default gateway configurations are all working. The inability to resolve 'google.com' isolates the root cause to a DNS resolution failure (misconfigured or unreachable DNS server).",
            "Isolate DNS resolution failure from underlying IP connectivity.",
            [
                ("DNS resolution failure: the host cannot resolve domain names, though underlying IP routing and gateway connectivity are functional", True, "Successful IP ping proves Layer 1-3 connectivity; name failure isolates the issue to DNS (Layer 7)."),
                ("The physical Ethernet cable has been severed in half", False, "If the cable were cut, pinging 8.8.8.8 would fail immediately."),
                ("The user's computer monitor has overheated", False, "The user is actively viewing terminal error messages on screen."),
                ("The default gateway router has crashed and stopped forwarding all packets", False, "Pinging 8.8.8.8 succeeded through the gateway.")
            ],
            ["dns", "ping", "troubleshooting", "dns-failure"]
        ),
    ]
    save_questions("firewalls_nat_and_troubleshooting.json", items)


if __name__ == "__main__":
    generate_routing_and_switching()
    generate_firewalls_nat_troubleshooting()
