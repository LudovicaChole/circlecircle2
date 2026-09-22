def history_node_fields(line_raw):
    """Read eight 10-column history-node IDs, or a comma-separated card."""
    line = line_raw.split("$", 1)[0].rstrip("\r\n")
    if "," in line:
        return [value.strip() for value in line.split(",") if value.strip()]
    # Fixed-width cards may contain adjacent IDs without any separating space.
    fields = [line[i:i + 10].strip() for i in range(0, len(line), 10)]
    if all(not value or len(value.split()) == 1 for value in fields):
        return [value for value in fields if value]
    return line.split()
