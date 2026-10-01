import json
import os
from datetime import datetime
from typing import Any, Dict

class AuditLogger:
    def __init__(self, log_file: str = "audit_results.json"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump({"test_runs": []}, f, indent=4)

    def log_result(self, module_name: str, test_type: str, metrics: Dict[str, Any]):
        with open(self.log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "module": module_name,
            "test_type": test_type,
            "metrics": metrics
        }
        
        data["test_runs"].append(entry)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"[*] Logged result for {test_type} to {self.log_file}")
