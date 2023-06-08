def strip_tree(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "Context":
            assert "uuid" in obj
            assert isinstance(obj.pop("uuid"), str)
            if "start_time" in obj:
                assert isinstance(obj.pop("start_time"), str)
            if "end_time" in obj:
                assert isinstance(obj.pop("end_time"), str)
        if obj.get("_type") == "Event":
            assert "time" in obj
            assert isinstance(obj.pop("time"), str)
        return {key: strip_tree(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [strip_tree(o) for o in obj]
    return obj
