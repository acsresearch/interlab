def strip_tree(obj, erase_error_details=False):
    if isinstance(obj, dict):
        t = obj.get("_type")
        if t == "Context":
            assert "uid" in obj
            assert isinstance(obj.pop("uid"), str)
            if "start_time" in obj:
                assert isinstance(obj.pop("start_time"), str)
            if "end_time" in obj:
                assert isinstance(obj.pop("end_time"), str)
        elif t == "$traceback":
            if erase_error_details:
                obj.pop("frames")
            else:
                for frame in obj.get("frames", []):
                    assert isinstance(frame.pop("lineno"), int)
        return {
            key: strip_tree(value, erase_error_details) for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [strip_tree(o, erase_error_details) for o in obj]
    return obj
