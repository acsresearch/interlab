def strip_tree(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "Context":
            assert "uuid" in obj
            del obj["uuid"]
        if obj.get("_type") == "Event":
            assert "time" in obj
            del obj["time"]
        return {key: strip_tree(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [strip_tree(o) for o in obj]
    return obj
