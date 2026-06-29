# NCCL — NVIDIA Collective Communications Library


## Purpose & Prerequisites

NCCL (pronounced "nickel") is NVIDIA's high-performance communication
library for multi-GPU and multi-node collective operations. It provides
the communication backbone for distributed deep learning and HPC
workloads, enabling GPUs to efficiently share data across NVLink,
NVSwitch, and InfiniBand interconnects.

### Core Collective Operations

| Operation     | What it does                                           | Primary use case                      |
|---------------|--------------------------------------------------------|---------------------------------------|
| AllReduce     | Reduce across all GPUs, every GPU gets the result      | Gradient sync in distributed training |
| Broadcast     | One GPU sends identical data to all others             | Weight initialization, hyperparams    |
| AllGather     | Each GPU contributes a chunk, all GPUs get full result | Tensor parallelism, ZeRO optimizer    |
| ReduceScatter | Reduce across GPUs, each GPU gets one slice of result  | ZeRO Stage 2/3, pipeline parallelism  |
| Send/Recv     | Direct point-to-point transfer between two GPUs        | Pipeline parallelism, halo exchange   |

### Prerequisites

- NVIDIA GPU (Volta architecture or newer recommended)
- CUDA 11.0+
- Python 3.10+
- PyTorch 2.0+ (built with NCCL support — included in standard builds)
- 2+ GPUs required for multi-GPU examples


## Installation & Basic Functionality

See **Environment Setup** section for detailed installation instructions.

`examples/basic_collectives.py` demonstrates NCCL's five core collective
operations using PyTorch's distributed communication package, which uses
NCCL as its backend. Each operation is shown with explicit before/after
tensor values so the data movement pattern is visible, along with latency
and correctness measurements.

The demo is framed around distributed training: each GPU represents a
worker that has computed gradients on its local data batch. The collectives
show how those gradients are synchronized across workers before a weight
update step.


### Run

```bash
# Requires 2+ GPUs
torchrun --nproc_per_node=2 examples/basic_collectives.py

# With 4 GPUs
torchrun --nproc_per_node=4 examples/basic_collectives.py
```

### What to expect

```
NCCL Basic Collectives Demo
GPUs: 4  |  NCCL version: (2, 28, 9)

=== AllReduce ===
Before: GPU0=[1.00]  GPU1=[1.00]  GPU2=[1.00]  GPU3=[1.00]
After:  GPU0=[4.00]  GPU1=[4.00]  GPU2=[4.00]  GPU3=[4.00]
Latency: 0.243 ms  |  Correct: ✓

=== Broadcast ===
Before: GPU0=[5.00]  GPU1=[0.00]  GPU2=[0.00]  GPU3=[0.00]
After:  GPU0=[5.00]  GPU1=[5.00]  GPU2=[5.00]  GPU3=[5.00]
Latency: 0.198 ms  |  Correct: ✓

=== AllGather ===
Before: GPU0=[1.00]  GPU1=[2.00]  GPU2=[3.00]  GPU3=[4.00]
After:  GPU0=[1.00, 2.00, 3.00, 4.00] (all GPUs identical)
Latency: 0.187 ms  |  Correct: ✓

=== ReduceScatter ===
Before: GPU0=['1.00', '2.00', '3.00', '4.00']  GPU1=['2.00', '4.00', '6.00', '8.00']  GPU2=['3.00', '6.00', '9.00', '12.00']  GPU3=['4.00', '8.00', '12.00', '16.00']
After:  GPU0=[10.00]  GPU1=[20.00]  GPU2=[30.00]  GPU3=[40.00]
Latency: 0.202 ms  |  Correct: ✓

=== Send/Recv ===
Before: GPU0=[42.00]  GPU1=[0.00]  GPU2=[0.00]  GPU3=[0.00]
After:  GPU0=[42.00]  GPU1=[42.00]  GPU2=[0.00]  GPU3=[0.00]
Latency: 0.165 ms  |  Correct: ✓

Done.
```

## Relevant Use Case - Climate Simulation on Multi-GPU

`examples/climate_simulation.py` demonstrates NCCL in a simplified
atmospheric heat diffusion simulation — the same class of workload used
in real climate models like GFDL's FV3 and ECMWF's IFS.

### The Problem

Climate simulations discretize the atmosphere into a 2D (or 3D) grid.
At scale, this grid is too large for one GPU's memory — it must be
partitioned across many GPUs. Each GPU owns a horizontal slab of the
grid and must:

1. Compute local physics (heat diffusion) on its slab each time step
2. Exchange boundary rows with neighboring GPUs so physics is continuous
   across partition boundaries (halo exchange)
3. Periodically compute global diagnostics — total energy, max temperature,
   convergence — to monitor simulation health

This maps directly onto NCCL primitives:

| Simulation need        | NCCL operation  |
|------------------------|-----------------|
| Boundary row exchange  | Send / Recv     |
| Global max temperature | AllReduce (max) |
| Total energy check     | AllReduce (sum) |
| Convergence check      | AllReduce (max) |

### Run

```bash
# Requires 2+ GPUs
torchrun --nproc_per_node=2 examples/climate_simulation.py

# With 4 GPUs
torchrun --nproc_per_node=4 examples/climate_simulation.py
```

### What to expect

```
Atmospheric Heat Diffusion Simulation
Grid: 1024x1024  |  GPUs: 4  |  Slab per GPU: 1024x256
Steps: 100  |  Diffusivity (alpha): 0.1
----------------------------------------------------------------------
Step   10/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 7.08e-01  |  Comm: 6.16ms
Step   20/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 3.81e-01  |  Comm: 3.09ms
Step   30/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 2.47e-01  |  Comm: 2.07ms
Step   40/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 1.91e-01  |  Comm: 1.56ms
Step   50/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 1.52e-01  |  Comm: 1.25ms
Step   60/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 1.26e-01  |  Comm: 1.05ms
Step   70/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 1.09e-01  |  Comm: 0.90ms
Step   80/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 9.56e-02  |  Comm: 0.79ms
Step   90/100  |  Max Temp: 288.0 K  |  Total Energy: 2.8451e+08  |  Convergence: 8.45e-02  |  Comm: 0.71ms
Step  100/100  |  Max Temp: 287.9 K  |  Total Energy: 2.8451e+08  |  Convergence: 7.59e-02  |  Comm: 0.64ms
----------------------------------------------------------------------
Avg step time:  0.84 ms
Avg comm time:  0.37 ms
Comm overhead:  43.8%
Converged:      No (final delta: 7.59e-02)
```

The comm overhead percentage is the key metric — it shows how much of
each time step is spent on NCCL communication vs actual computation.
In real climate codes, keeping this below ~15% is the goal. The high
overhead here reflects how compute-light the stencil is relative to
A100 throughput. Larger grids bring this down significantly.

### Grid Scaling Experiment

`examples/climate_experiment.py` runs the simulation across multiple grid
sizes to show how communication overhead changes as compute load increases.

```bash
torchrun --nproc_per_node=4 examples/climate_experiment.py 2>&1 | tee outputs/experiments.txt
```

Results on 4x A100 80GB:

```
Grid  |  Overhead  |  Step (ms)  |  Comm (ms)
----------------------------------------------
1024  |     38.9%  |       0.89  |       0.35
2048  |     46.0%  |       0.81  |       0.37
4096  |     37.0%  |       1.03  |       0.38
8192  |     14.2%  |       2.56  |       0.36
```

NCCL communication time stays nearly flat (~0.36ms) across all grid sizes
because halo exchange only transfers boundary rows, which scale as O(N)
while the grid grows as O(N²). Compute time grows with the grid, bringing
overhead down to 14.2% at 8192×8192 — within the real-world target range.

Figures generated by the experiment script:
- `outputs/fig1_convergence.png` — convergence curve over steps
- `outputs/fig2_grid_scaling.png` — comm overhead and compute vs comm time by grid size


## Environment Setup

### Step 1 — Verify your GPU and CUDA version

```bash
nvidia-smi
```

Look for the CUDA Version in the top right corner of the output. Note it —
you'll need it to pick the right PyTorch wheel.

```bash
# Also check your CUDA toolkit version
nvcc --version
```

### Step 2 — Verify Python version

PyTorch 2.7+ requires Python 3.10 or later.

```bash
python3 --version
```

If below 3.10, install a newer version or use a conda environment (Step 3b).

### Step 3a — Set up a virtual environment (recommended)

```bash
python3 -m venv nccl-env
source nccl-env/bin/activate       # Linux/Mac
# nccl-env\Scripts\activate        # Windows
```

If you get an ensurepip error on Ubuntu, run first:
```bash
sudo apt install python3.10-venv -y
```

### Step 3b — Or use conda (alternative)

```bash
conda create -n nccl-env python=3.11
conda activate nccl-env
```

### Step 4 — Install PyTorch with NCCL

NCCL is bundled inside PyTorch — no separate NCCL install needed for
Python usage. Pick the command matching your CUDA version from Step 1:

```bash
# CUDA 12.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# CUDA 12.6
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Not sure which to pick? Match the CUDA version shown by `nvidia-smi`,
rounding down to the nearest available wheel (e.g. CUDA 12.7 → use cu126).
NCCL also supports CUDA versions newer than the latest wheel — CUDA 13.0
can use cu128.

### Step 5 — Install remaining dependencies

```bash
pip install -r requirements.txt
```

### Step 6 — Verify everything works

```bash
# Check PyTorch and CUDA are connected
python3 -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('NCCL available:', torch.distributed.is_nccl_available())"

# Check how many GPUs are visible
python3 -c "import torch; print('GPUs found:', torch.cuda.device_count())"

# Check NCCL version bundled with PyTorch
python3 -c "import torch; print('NCCL version:', torch.cuda.nccl.version())"
```

Expected output:
```
PyTorch: 2.7.0+cu128
CUDA available: True
NCCL available: True
GPUs found: 4
NCCL version: (2, 28, 9)
```

### Note on system-level NCCL (optional)

If you want to install NCCL system-wide for C/CUDA development outside
of Python, use the NVIDIA network repository on Ubuntu:

```bash
# Add CUDA keyring (if not already added)
sudo apt-get install -y cuda-keyring

# Install NCCL
sudo apt-get install -y libnccl2 libnccl-dev
```

This is not required for running the examples in this project.


## Helpful Links

- [Official Documentation](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html)
- [GitHub Repository](https://github.com/NVIDIA/nccl)
- [NVIDIA Developer Page](https://developer.nvidia.com/nccl)

## Contributor

Kristen Guernsey

