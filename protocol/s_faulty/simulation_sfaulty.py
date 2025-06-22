import time
import csv
import yaml
import shutil
import os
from multiprocessing import Pool, cpu_count

import application as application
from application import SenderProgram, Receiver0Program, Receiver1Program
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

# Parameters
DEPOLAR_VALUES = [0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.0025, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
NUM_STATES = 280
TRIALS_PER_VALUE = 500
BASE_CONFIG = "config.yaml"
application.NUM_STATES = NUM_STATES

# Prepare Extra configuration files for parallel runs of the protocol
# Each run has a different configuration file
# This function will generate 12 configuration files similar to the original
# The only difference will be the 2-qubit depolarization probability
def prepare_config_files():
    for idx, prob in enumerate(DEPOLAR_VALUES):
        with open(BASE_CONFIG, "r") as f:
            config = yaml.safe_load(f)

        for stack in config.get("stacks", []):
            if stack.get("qdevice_typ") == "generic":
                qcfg = stack.setdefault("qdevice_cfg", {})
                qcfg["two_qubit_gate_depolar_prob"] = float(prob)

        config_path = f"config_{idx}.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

# Instance of a paralelization run
def run_for_depolarization(idx_and_prob):
    idx, p = idx_and_prob
    config_path = f"config_{idx}.yaml"
    output_csv = f"results_p={p:.8f}.csv"
    cfg = StackNetworkConfig.from_file(config_path)

    successes, failures = 0, 0
    total_time = 0.0
    # Additional values for correctness checks
    l1, l2, l3 = 0, 0, 0

    # Repeat for each trial
    for _ in range(TRIALS_PER_VALUE):
        # Typical protocol run, like in run_simulation.py
        sender = SenderProgram()
        r0 = Receiver0Program()
        r1 = Receiver1Program()
        start_time = time.time()
        result = run(config=cfg, programs={
            "Sender": sender,
            "Receiver0": r0,
            "Receiver1": r1,
        }, num_times=1)
        end_time = time.time()
        total_time += (end_time - start_time)
        
        # Obtain results - S faulty configuration
        sender_result = result[0][0]
        l1 = sender_result.get("l1")
        l2 = sender_result.get("l2")
        l3 = sender_result.get("l3")
        if sender_result.get("failed_to_apply_strategy", False):
            failures += 1
        else:
            y0  = result[1][0].get("y0")
            y1  = result[2][0].get("y1")
            if y0 != y1 and y0 != "abort" and y1 != "abort":
                failures += 1
            else:
                successes += 1

    avg_time = total_time / TRIALS_PER_VALUE
    fail_rate = failures / TRIALS_PER_VALUE

    # Output results
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Depolar_Prob", "Trials", "Successes", "Failures", "Avg_Time", "Failure_Rate"])
        writer.writerow([p, TRIALS_PER_VALUE, successes, failures,avg_time, fail_rate])
    return (p, output_csv)

if __name__ == "__main__":
    # Prepare extra configuration files
    prepare_config_files()

    # Parallelize the simulation runs, based on depolarization value
    with Pool(processes=min(cpu_count(), len(DEPOLAR_VALUES))) as pool:
        result_files = pool.map(run_for_depolarization, list(enumerate(DEPOLAR_VALUES)))

    # Debug print
    print("\nGenerated result files:")
    for p, file in result_files:
        print(f"  - p={p:.8f}: {file}")

    # Cleanup of extra configuration files
    for idx in range(len(DEPOLAR_VALUES)):
        try:
            os.remove(f"config_{idx}.yaml")
        except FileNotFoundError:
            pass
