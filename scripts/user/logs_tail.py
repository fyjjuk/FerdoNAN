#!/usr/bin/env python
import os
import time
import sys

def tail_log(log_file="logs/ferdonan.log", lines=20):
    if not os.path.exists(log_file):
        print(f"Log no encontrado: {log_file}")
        return
    os.system(f"tail -n {lines} -f {log_file}")

if __name__ == "__main__":
    tail_log()
