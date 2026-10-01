"""Safe educational display-filter tokenizer, AST parser, and SQLAlchemy expression builder.

Strictly avoids eval(), exec(), or arbitrary dynamic execution.
Validates fields against an educational whitelist and generates SQL filter criteria.
"""

import re

from sqlalchemy import ColumnElement, and_, not_, or_

from app.models.pcap import ParsedPacket


class FilterValidationError(Exception):
    """Raised when display filter has syntax errors or unsupported fields."""



# Token types
TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_AND = "AND"
TOKEN_OR = "OR"
TOKEN_NOT = "NOT"
TOKEN_OP = "OP"
TOKEN_TERM = "TERM"

# Whitelisted protocol keywords
PROTOCOL_KEYWORDS = {
    "tcp", "udp", "icmp", "arp", "dns", "http", "tls", "dhcp",
    "ip", "ipv4", "ipv6", "ethernet"
}

# Whitelisted filter field prefixes
SUPPORTED_FIELDS = {
    "ip.src", "ip.dst", "ip.addr",
    "ip6.src", "ip6.dst", "ip6.addr",
    "tcp.port", "tcp.srcport", "tcp.dstport",
    "udp.port", "udp.srcport", "udp.dstport",
    "tcp.flags.syn", "tcp.flags.ack", "tcp.flags.rst", "tcp.flags.fin",
    "http.request", "http.response",
    "dns.query", "dns.response", "dns.name",
    "frame.len", "frame.number"
}


class Token:
    def __init__(self, token_type: str, value: str, position: int = 0):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"


class ASTNode:
    pass


class BinaryOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right


class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand


class ComparisonNode(ASTNode):
    def __init__(self, field: str, op: str, value: str):
        self.field = field.lower()
        self.op = op
        self.value = value.strip('"\'')


class KeywordNode(ASTNode):
    def __init__(self, keyword: str):
        self.keyword = keyword.lower()


class PacketFilterService:
    """Deterministic, safe parser and validator for packet display filters."""

    def tokenize(self, text: str) -> list[Token]:
        """Convert filter text into structured tokens."""
        tokens: list[Token] = []
        scanner = re.finditer(
            r"""
            \s*(
                (?P<LPAREN>\()|
                (?P<RPAREN>\))|
                (?P<OP>==|!=|<=|>=|<|>|contains)|
                (?P<AND>&&|\band\b)|
                (?P<OR>\|\||\bor\b)|
                (?P<NOT>!|\bnot\b)|
                (?P<TERM>"[^"]*"|'[^']*'|[^\s()=!<>|&]+)
            )
            """,
            text,
            re.VERBOSE | re.IGNORECASE,
        )

        for match in scanner:
            for kind, val in match.groupdict().items():
                if val is not None:
                    if kind in {"AND", "OR", "NOT"}:
                        tokens.append(Token(kind, val.upper(), match.start()))
                    else:
                        tokens.append(Token(kind, val, match.start()))
                    break

        return tokens

    def parse(self, text: str) -> ASTNode | None:
        """Parse raw filter text into an AST."""
        cleaned = text.strip()
        if not cleaned:
            return None

        tokens = self.tokenize(cleaned)
        if not tokens:
            return None

        pos = 0

        def peek() -> Token | None:
            return tokens[pos] if pos < len(tokens) else None

        def consume(expected_type: str | None = None) -> Token:
            nonlocal pos
            current = peek()
            if not current:
                raise FilterValidationError("Unexpected end of filter expression")
            if expected_type and current.type != expected_type:
                raise FilterValidationError(
                    f"Expected {expected_type} at position {current.position}, got {current.value}"
                )
            pos += 1
            return current

        # Recursive descent parser: Expression -> OrExpr -> AndExpr -> NotExpr -> Primary
        def parse_expression() -> ASTNode:
            return parse_or()

        def parse_or() -> ASTNode:
            node = parse_and()
            while peek() and peek().type == TOKEN_OR:
                consume(TOKEN_OR)
                right = parse_and()
                node = BinaryOpNode("OR", node, right)
            return node

        def parse_and() -> ASTNode:
            node = parse_not()
            while peek() and peek().type == TOKEN_AND:
                consume(TOKEN_AND)
                right = parse_not()
                node = BinaryOpNode("AND", node, right)
            return node

        def parse_not() -> ASTNode:
            if peek() and peek().type == TOKEN_NOT:
                consume(TOKEN_NOT)
                operand = parse_not()
                return UnaryOpNode("NOT", operand)
            return parse_primary()

        def parse_primary() -> ASTNode:
            tok = peek()
            if not tok:
                raise FilterValidationError("Incomplete filter expression")

            if tok.type == TOKEN_LPAREN:
                consume(TOKEN_LPAREN)
                sub_expr = parse_expression()
                consume(TOKEN_RPAREN)
                return sub_expr

            if tok.type == TOKEN_TERM:
                first = consume(TOKEN_TERM)
                lower_term = first.value.lower()

                # Check if followed by an operator (comparison)
                next_tok = peek()
                if next_tok and next_tok.type == TOKEN_OP:
                    op_tok = consume(TOKEN_OP)
                    val_tok = consume(TOKEN_TERM)
                    # Validate field name
                    if lower_term not in SUPPORTED_FIELDS:
                        raise FilterValidationError(f"Unsupported filter field: {first.value}")
                    return ComparisonNode(lower_term, op_tok.value, val_tok.value)

                # Standalone field / flag or protocol keyword
                if lower_term in PROTOCOL_KEYWORDS:
                    return KeywordNode(lower_term)
                if lower_term in SUPPORTED_FIELDS:
                    return ComparisonNode(lower_term, "==", "true")

                # If the field resembles a dotted key not in whitelist (e.g. ip.xyz)
                if "." in lower_term:
                    raise FilterValidationError(f"Unsupported filter field: {first.value}")

                # General search fallback keyword
                return KeywordNode(lower_term)

            raise FilterValidationError(f"Unexpected token '{tok.value}' at position {tok.position}")

        root = parse_expression()
        if pos < len(tokens):
            remaining = tokens[pos]
            raise FilterValidationError(f"Extra token '{remaining.value}' at position {remaining.position}")
        return root

    def build_sql_criterion(self, ast: ASTNode) -> ColumnElement[bool]:
        """Translate parsed AST node into a safe SQLAlchemy column expression."""
        if isinstance(ast, BinaryOpNode):
            left_sql = self.build_sql_criterion(ast.left)
            right_sql = self.build_sql_criterion(ast.right)
            if ast.op == "OR":
                return or_(left_sql, right_sql)
            return and_(left_sql, right_sql)

        if isinstance(ast, UnaryOpNode):
            child_sql = self.build_sql_criterion(ast.operand)
            return not_(child_sql)

        if isinstance(ast, KeywordNode):
            kw = ast.keyword
            if kw in {"tcp", "udp"}:
                return or_(
                    ParsedPacket.protocol == kw.upper(),
                    ParsedPacket.transport_protocol == kw.upper(),
                )
            if kw in {"ip", "ipv4"}:
                return or_(
                    ParsedPacket.protocol == "IPv4",
                    ParsedPacket.source_ip.isnot(None),
                )
            if kw == "ipv6":
                return or_(
                    ParsedPacket.protocol == "IPv6",
                    ParsedPacket.source_ip.like("%:%"),
                )
            if kw in {"dns", "http", "tls", "dhcp", "arp", "icmp"}:
                return or_(
                    ParsedPacket.protocol == kw.upper(),
                    ParsedPacket.application_protocol == kw.upper(),
                )
            # General term search across info, source_ip, destination_ip, protocol
            return or_(
                ParsedPacket.info.ilike(f"%{kw}%"),
                ParsedPacket.source_ip.ilike(f"%{kw}%"),
                ParsedPacket.destination_ip.ilike(f"%{kw}%"),
                ParsedPacket.protocol.ilike(f"%{kw}%"),
            )

        if isinstance(ast, ComparisonNode):
            field = ast.field
            val = ast.value
            op = ast.op

            # IP filtering
            if field == "ip.addr":
                if op == "!=":
                    return and_(ParsedPacket.source_ip != val, ParsedPacket.destination_ip != val)
                return or_(ParsedPacket.source_ip == val, ParsedPacket.destination_ip == val)
            if field == "ip.src":
                return ParsedPacket.source_ip != val if op == "!=" else ParsedPacket.source_ip == val
            if field == "ip.dst":
                return ParsedPacket.destination_ip != val if op == "!=" else ParsedPacket.destination_ip == val

            # Port filtering
            if field in {"tcp.port", "udp.port"}:
                try:
                    port_num = int(val)
                except ValueError:
                    raise FilterValidationError(f"Invalid integer port value: {val}")
                proto = "TCP" if "tcp" in field else "UDP"
                port_match = or_(ParsedPacket.source_port == port_num, ParsedPacket.destination_port == port_num)
                proto_match = or_(ParsedPacket.protocol == proto, ParsedPacket.transport_protocol == proto)
                if op == "!=":
                    return not_(and_(proto_match, port_match))
                return and_(proto_match, port_match)

            if field in {"tcp.srcport", "udp.srcport"}:
                try:
                    port_num = int(val)
                except ValueError:
                    raise FilterValidationError(f"Invalid integer port value: {val}")
                return ParsedPacket.source_port == port_num if op == "==" else ParsedPacket.source_port != port_num

            if field in {"tcp.dstport", "udp.dstport"}:
                try:
                    port_num = int(val)
                except ValueError:
                    raise FilterValidationError(f"Invalid integer port value: {val}")
                return ParsedPacket.destination_port == port_num if op == "==" else ParsedPacket.destination_port != port_num

            # TCP flags
            if field == "tcp.flags.syn":
                clause = ParsedPacket.tcp_flags.like('%"SYN"%')
                return not_(clause) if val.lower() == "false" else clause
            if field == "tcp.flags.ack":
                clause = ParsedPacket.tcp_flags.like('%"ACK"%')
                return not_(clause) if val.lower() == "false" else clause
            if field == "tcp.flags.rst":
                clause = ParsedPacket.tcp_flags.like('%"RST"%')
                return not_(clause) if val.lower() == "false" else clause
            if field == "tcp.flags.fin":
                clause = ParsedPacket.tcp_flags.like('%"FIN"%')
                return not_(clause) if val.lower() == "false" else clause

            # HTTP / DNS predicates
            if field == "http.request":
                return and_(
                    ParsedPacket.protocol == "HTTP",
                    not_(ParsedPacket.info.like("HTTP/%")),
                )
            if field == "http.response":
                return and_(
                    ParsedPacket.protocol == "HTTP",
                    ParsedPacket.info.like("HTTP/%"),
                )
            if field == "dns.query":
                return and_(
                    ParsedPacket.protocol == "DNS",
                    ParsedPacket.info.like("Standard query 0x%"),
                )
            if field == "dns.response":
                return and_(
                    ParsedPacket.protocol == "DNS",
                    ParsedPacket.info.like("Standard query response%"),
                )
            if field == "dns.name":
                return and_(
                    ParsedPacket.protocol == "DNS",
                    ParsedPacket.info.ilike(f"%{val}%"),
                )

            # Frame length and number
            if field == "frame.len":
                try:
                    length_val = int(val)
                except ValueError:
                    raise FilterValidationError(f"Invalid integer length value: {val}")
                if op == ">":
                    return ParsedPacket.captured_length > length_val
                if op == "<":
                    return ParsedPacket.captured_length < length_val
                if op == ">=":
                    return ParsedPacket.captured_length >= length_val
                if op == "<=":
                    return ParsedPacket.captured_length <= length_val
                return ParsedPacket.captured_length == length_val

            if field == "frame.number":
                try:
                    num_val = int(val)
                except ValueError:
                    raise FilterValidationError(f"Invalid packet number: {val}")
                return ParsedPacket.packet_number == num_val

            raise FilterValidationError(f"Unsupported filter field: {field}")

        return and_(True)


packet_filter_service = PacketFilterService()
