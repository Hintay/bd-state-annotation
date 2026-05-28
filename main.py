"""Single entry point for the demo runners.

Usage: python main.py {single|trend|verify|deid}
"""
import sys
from dotenv import load_dotenv

load_dotenv()

from src.labeling import label_single, label_trend, verify_patients, deidentify

TASKS = {
    "single": label_single.main,
    "trend": label_trend.main,
    "verify": verify_patients.main,
    "deid": deidentify.main,
}

def dispatch(task: str):
    if task not in TASKS:
        print(f"Unknown task '{task}'. Choose one of: {', '.join(TASKS)}")
        raise SystemExit(2)
    TASKS[task]()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python main.py {{{'|'.join(TASKS)}}}")
        raise SystemExit(2)
    dispatch(sys.argv[1])
