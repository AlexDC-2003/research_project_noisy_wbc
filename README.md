# Noisy Byzantine Agreement in Quantum Networks  
**Simulation Framework for the Weak Broadcast Protocol**

This repository contains the code for simulation and analysis on the impact of gate-level depolarizing noise on the Weak Broadcast Protocol (WBC(3,1)), based on the implementation described in the Bachelor thesis _"Noisy Byzantine Agreement in Quantum Networks: Impact of Gate Errors on a Weak Broadcast Protocol"_.

The goal of this code is to evaluate how hardware-level imperfections (specifically two-qubit gate depolarizing noise) affect the failure probability of the protocol under three adversarial models: no faulty, sender (S) faulty, and receiver (R0) faulty.

---

## 📦 Repository Structure

All simulations are organized in the `protocol/` directory. Each adversary configuration has its own subfolder containing the full SquidASM simulation stack.

```
protocol/
├── no_faulty/
│   ├── application.py
│   ├── config.yaml
│   ├── run_simulation.py
│   ├── simulation_nofaulty.py
│   └── plot_nofaulty.py
├── s_faulty/
│   ├── application.py
│   ├── config.yaml
│   ├── run_simulation.py
│   ├── simulation_sfaulty.py
│   └── plot_sfaulty.py
└── r0_faulty/
    ├── application.py
    ├── config.yaml
    ├── run_simulation.py
    ├── simulation_r0faulty.py
    └── plot_r0faulty.py
```


### File Descriptions

- **application.py** — Implements the WBC(3,1) protocol logic for the three participating nodes.
- **config.yaml** — Describes the network configuration (node layout, noise settings, number of qubits, etc.).
- **run_simulation.py** — Entry point for launching the simulation with SquidASM.
- **simulation_<strategy>.py** — Manages batch simulations for different depolarizing noise levels using parallelization.
- **plot_<strategy>.py** — Generates the final failure probability plots used in the thesis.

---

## 🚀 Installation

To run the simulations, follow these steps:

### 1. Install NetSquid

NetSquid is a closed-source simulator that requires registration.

- Visit the [NetSquid website](https://www.netsquid.org/) and request access.

### 2. Install SquidASM

SquidASM is an open-source Python package that wraps NetSquid to simplify network simulations.

- GitHub repository: [SquidASM](https://github.com/QuTech-Delft/squidasm)
- Follow installation instructions in their [documentation](https://squidasm.readthedocs.io/en/latest/installation.html).

### 3. Install Python Dependencies

The code was developed in Python, alongside these following packages:

```bash
pip install matplotlib numpy pandas pyyaml
```

---

## 🛠️ Usage

Each strategy can be simulated independently by navigating into its folder and running the `simulation_<strategy>.py` file. Example:

```bash
cd protocol/no_faulty
python simulation_nofaulty.py
```

This will generate output data and plots showing the failure probability of the protocol at various depolarization levels. Note that the data will need to be manually aggregated and introduced in the plot files.

To generate the corresponding plot separately:

```bash
python plot_nofaulty.py
```

Repeat the same steps for the `s_faulty` and `r0_faulty` directories.

---

## 📘 Documentation and References

- SquidASM Documentation: https://github.com/QuTech-Delft/squidasm  
- NetSquid Forum: https://forum.netsquid.org/  
- Bachelor Thesis: `Noisy Byzantine Agreement in Quantum Networks: Impact of Gate Errors on a Weak Broadcast Protocol` (link pending)

---

## 🧹 Clean-up Notice

All unused or outdated scripts have been removed. Some debug data has been left to facilitate a better understanding of the protocol's mechanics. Each file in this repository is part of the final simulation and analysis pipeline used to produce the results cited in the accompanying thesis.

---
