import json
import os

RESTART_RECORD_FILE = "./module/webui/restart_record.json"

def _load_restart_data():
    if not os.path.exists(RESTART_RECORD_FILE):
        return {}
    try:
        with open(RESTART_RECORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_restart_data(data):
    with open(RESTART_RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_restart_count(instance_name):
    data = _load_restart_data()
    return data.get(instance_name, 0)

def set_restart_count(instance_name, count):
    data = _load_restart_data()
    data[instance_name] = count
    _save_restart_data(data)

def reset_restart_count(instance_name):
    data = _load_restart_data()
    if instance_name in data:
        del data[instance_name]
        _save_restart_data(data)
