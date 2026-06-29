import torch
import torch.distributed as dist
import os
import time
import json
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def init_process():
    dist.init_process_group(backend="nccl")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    return rank, world_size

def laplacian(field):
    return (
        torch.roll(field, 1, dims=0) +
        torch.roll(field, -1, dims=0) +
        torch.roll(field, 1, dims=1) +
        torch.roll(field, -1, dims=1) -
        4 * field
    )

def halo_exchange(slab, rank, world_size):
    top_neighbor = (rank - 1) % world_size
    bottom_neighbor = (rank + 1) % world_size

    send_top = slab[0].contiguous()
    send_bottom = slab[-1].contiguous()
    recv_top = torch.zeros_like(send_top)
    recv_bottom = torch.zeros_like(send_bottom)

    ops = [
        dist.P2POp(dist.isend, send_bottom, bottom_neighbor),
        dist.P2POp(dist.isend, send_top,    top_neighbor),
        dist.P2POp(dist.irecv, recv_top,    top_neighbor),
        dist.P2POp(dist.irecv, recv_bottom, bottom_neighbor),
    ]
    reqs = dist.batch_isend_irecv(ops)
    for req in reqs:
        req.wait()

    slab[0]  = recv_top
    slab[-1] = recv_bottom
    return slab

def run_experiment(rank, world_size, grid_size, num_steps, alpha=0.1, diag_interval=10):
    slab_height = grid_size // world_size

    field = torch.zeros(slab_height, grid_size, dtype=torch.float32).cuda(rank)
    global_row_start = rank * slab_height
    for local_row in range(slab_height):
        global_row = global_row_start + local_row
        latitude = (global_row / grid_size - 0.5) * 180.0
        field[local_row, :] = 288.0 - 50.0 * (latitude / 90.0) ** 2

    if rank == 0:
        print(f"\nGrid: {grid_size}x{grid_size} | Steps: {num_steps} | Slab: {grid_size}x{slab_height}")
        print("-" * 60)

    comm_times = []
    step_times = []
    convergence_history = []
    max_temp_history = []
    energy_history = []
    comm_overhead_history = []

    comm_time_total = 0.0
    step_time_total = 0.0
    convergence = float("inf")
    prev_field = field.clone()

    for step in range(1, num_steps + 1):
        step_start = time.perf_counter()

        comm_start = time.perf_counter()
        field = halo_exchange(field, rank, world_size)
        torch.cuda.synchronize()
        comm_elapsed = time.perf_counter() - comm_start
        comm_time_total += comm_elapsed

        field = field + alpha * laplacian(field)
        field.clamp_(200.0, 350.0)

        local_diff = (field - prev_field).abs().max().unsqueeze(0)
        dist.all_reduce(local_diff, op=dist.ReduceOp.MAX)
        convergence = local_diff.item()
        prev_field = field.clone()

        torch.cuda.synchronize()
        step_elapsed = time.perf_counter() - step_start
        step_time_total += step_elapsed

        comm_times.append(comm_elapsed * 1000)
        step_times.append(step_elapsed * 1000)
        convergence_history.append(convergence)
        overhead = (comm_elapsed / step_elapsed * 100) if step_elapsed > 0 else 0
        comm_overhead_history.append(overhead)

        if step % diag_interval == 0:
            local_max = field.max().unsqueeze(0)
            local_sum = field.sum().unsqueeze(0)
            dist.all_reduce(local_max, op=dist.ReduceOp.MAX)
            dist.all_reduce(local_sum, op=dist.ReduceOp.SUM)

            max_temp_history.append((step, local_max.item()))
            energy_history.append((step, local_sum.item()))

            avg_comm_ms = (comm_time_total / step) * 1000
            avg_overhead = (comm_time_total / step_time_total) * 100

            if rank == 0:
                print(
                    f"Step {step:4d}/{num_steps} | "
                    f"Max Temp: {local_max.item():.1f} K | "
                    f"Convergence: {convergence:.2e} | "
                    f"Comm: {avg_comm_ms:.2f}ms | "
                    f"Overhead: {avg_overhead:.1f}%"
                )

    dist.barrier()
    avg_step_ms = (step_time_total / num_steps) * 1000
    avg_comm_ms = (comm_time_total / num_steps) * 1000
    avg_overhead = (comm_time_total / step_time_total) * 100

    if rank == 0:
        converged = convergence < 1e-3
        print(f"\nAvg step: {avg_step_ms:.2f}ms | Avg comm: {avg_comm_ms:.2f}ms | "
              f"Overhead: {avg_overhead:.1f}% | Converged: {'Yes' if converged else 'No'}")

    return {
        "grid_size": grid_size,
        "num_steps": num_steps,
        "comm_times": comm_times,
        "step_times": step_times,
        "convergence_history": convergence_history,
        "max_temp_history": max_temp_history,
        "energy_history": energy_history,
        "comm_overhead_history": comm_overhead_history,
        "avg_step_ms": avg_step_ms,
        "avg_comm_ms": avg_comm_ms,
        "avg_overhead": avg_overhead,
        "final_convergence": convergence,
        "converged": convergence < 1e-3,
    }

def plot_convergence_experiment(results_500, results_1000, save_dir="outputs"):
    """Figure 1: Convergence over steps for 1024x1024 at 500 and 1000 steps."""
    os.makedirs(save_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Figure 1: Climate Simulation Convergence — 1024×1024 Grid on 4× A100", fontsize=13, fontweight="bold")

    for ax, results, label in zip(axes, [results_500, results_1000], ["500 steps", "1000 steps"]):
        steps = list(range(1, len(results["convergence_history"]) + 1))
        ax.semilogy(steps, results["convergence_history"], color="#76b900", linewidth=1.5)
        ax.axhline(y=1e-3, color="red", linestyle="--", linewidth=1.2, label="Convergence threshold (1e-3)")
        converged_step = next((i + 1 for i, v in enumerate(results["convergence_history"]) if v < 1e-3), None)
        if converged_step:
            ax.axvline(x=converged_step, color="orange", linestyle=":", linewidth=1.5, label=f"Converged at step {converged_step}")
        ax.set_title(f"{label} | Final delta: {results['final_convergence']:.2e}")
        ax.set_xlabel("Step")
        ax.set_ylabel("Max temperature change (K)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_facecolor("#f9f9f9")

    plt.tight_layout()
    path = os.path.join(save_dir, "fig1_convergence.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

def plot_grid_scaling(all_results, save_dir="outputs"):
    """Figure 2: Comm overhead and step time vs grid size."""
    os.makedirs(save_dir, exist_ok=True)
    grid_sizes = [r["grid_size"] for r in all_results]
    overheads = [r["avg_overhead"] for r in all_results]
    step_times = [r["avg_step_ms"] for r in all_results]
    comm_times = [r["avg_comm_ms"] for r in all_results]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Figure 2: Communication Overhead vs Grid Size — 4× A100 with NCCL", fontsize=13, fontweight="bold")

    # Left: overhead %
    ax = axes[0]
    bars = ax.bar([str(g) for g in grid_sizes], overheads, color="#76b900", alpha=0.85, edgecolor="black", linewidth=0.5)
    ax.axhspan(5, 15, alpha=0.15, color="blue", label="Real-world target (5–15%)")
    ax.set_xlabel("Grid Size")
    ax.set_ylabel("Comm overhead (%)")
    ax.set_title("NCCL Communication Overhead")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    for bar, val in zip(bars, overheads):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=9)
    ax.set_facecolor("#f9f9f9")

    # Right: step time breakdown
    ax = axes[1]
    x = np.arange(len(grid_sizes))
    width = 0.35
    compute_times = [s - c for s, c in zip(step_times, comm_times)]
    ax.bar(x - width/2, compute_times, width, label="Compute", color="#1f77b4", alpha=0.85, edgecolor="black", linewidth=0.5)
    ax.bar(x + width/2, comm_times, width, label="NCCL Comm", color="#76b900", alpha=0.85, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([str(g) for g in grid_sizes])
    ax.set_xlabel("Grid Size")
    ax.set_ylabel("Time per step (ms)")
    ax.set_title("Compute vs Communication Time per Step")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_facecolor("#f9f9f9")

    plt.tight_layout()
    path = os.path.join(save_dir, "fig2_grid_scaling.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

def main():
    rank, world_size = init_process()

    if rank == 0:
        print("=" * 60)
        print("EXPERIMENT 1: Convergence study — 1024x1024")
        print("=" * 60)

    r_500 = run_experiment(rank, world_size, grid_size=1024, num_steps=500)

    dist.barrier()
    if rank == 0:
        print("\n" + "=" * 60)
        print("EXPERIMENT 2: Convergence study — 1024x1024 extended")
        print("=" * 60)

    r_1000 = run_experiment(rank, world_size, grid_size=1024, num_steps=1000)

    dist.barrier()
    if rank == 0:
        print("\n" + "=" * 60)
        print("EXPERIMENT 3: Grid scaling — overhead vs grid size")
        print("=" * 60)

    scaling_results = []
    for grid_size in [1024, 2048, 4096, 8192]:
        dist.barrier()
        if rank == 0:
            print(f"\n--- Grid: {grid_size}x{grid_size} ---")
        r = run_experiment(rank, world_size, grid_size=grid_size, num_steps=50)
        scaling_results.append(r)

    dist.barrier()

    if rank == 0:
        print("\n" + "=" * 60)
        print("Generating figures...")
        plot_convergence_experiment(r_500, r_1000)
        plot_grid_scaling(scaling_results)
        print("\nGrid scaling summary:")
        print(f"{'Grid':>8} | {'Overhead':>10} | {'Step (ms)':>10} | {'Comm (ms)':>10}")
        print("-" * 48)
        for r in scaling_results:
            print(f"{r['grid_size']:>8} | {r['avg_overhead']:>9.1f}% | {r['avg_step_ms']:>10.2f} | {r['avg_comm_ms']:>10.2f}")

    dist.destroy_process_group()

if __name__ == "__main__":
    main()
