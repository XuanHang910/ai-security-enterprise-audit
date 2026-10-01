import os
import subprocess
import sys

def run_script(script_name):
    print(f"\n{'='*50}\nRunning {os.path.basename(script_name)}...\n{'='*50}")
    subprocess.run([sys.executable, script_name], check=False)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        "evasion_art.py",
        "data_poisoning.py",
        "membership_inference.py",
        "rag_security_test.py"
    ]
    
    for script in scripts:
        run_script(os.path.join(base_dir, script))
        
    print("\nAll assessments finished. Check audit_results.json for details.")
