import torch
import torch.distributed as dist
import os
import time

def init_process():
    dist.init_process_group(backend="nccl")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    device = torch.device(f"cuda:{rank}")
    return rank, world_size, device

def laplacian(field):
    """Finite difference heat diffusion stencil."""
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

def run_simulation(rank, world_size, grid_size=1024, num_steps=100, alpha=0.1, diag_interval=10):
    slab_height = grid_size // world_size

    # Initialize temperature field — warm equator, cold poles
    field = torch.zeros(slab_height, grid_size, dtype=torch.float32).cuda(rank)
    global_row_start = rank * slab_height
    for local_row in range(slab_height):
        global_row = global_row_start + local_row
        latitude = (global_row / grid_size - 0.5) * 180.0
        field[local_row, :] = 288.0 - 50.0 * (latitude / 90.0) ** 2

    if rank == 0:
        print(f"\nAtmospheric Heat Diffusion Simulation")
        print(f"Grid: {grid_size}x{grid_size}  |  GPUs: {world_size}  |  Slab per GPU: {grid_size}x{slab_height}")
        print(f"Steps: {num_steps}  |  Diffusivity (alpha): {alpha}")
        print("-" * 70)

    comm_time_total = 0.0
    step_time_total = 0.0
    convergence = float("inf")
    prev_field = field.clone()

    for step in range(1, num_steps + 1):
        step_start = time.perf_counter()

        # Halo exchange — sync boundary rows with neighboring GPUs
        comm_start = time.perf_counter()
        field = halo_exchange(field, rank, world_size)
        torch.cuda.synchronize()
        comm_time_total += time.perf_counter() - comm_start

        # Local physics — heat diffusion equation
        field = field + alpha * laplacian(field)
        field.clamp_(200.0, 350.0)

        # Convergence — max change in field since last step
        local_diff = (field - prev_field).abs().max().unsqueeze(0)
        dist.all_reduce(local_diff, op=dist.ReduceOp.MAX)
        convergence = local_diff.item()
        prev_field = field.clone()

        torch.cuda.synchronize()
        step_time_total += time.perf_counter() - step_start

        # Global diagnostics via AllReduce every diag_interval steps
        if step % diag_interval == 0:
            local_max = field.max().unsqueeze(0)
            local_sum = field.sum().unsqueeze(0)
            dist.all_reduce(local_max, op=dist.ReduceOp.MAX)
            dist.all_reduce(local_sum, op=dist.ReduceOp.SUM)

            global_max_temp = local_max.item()
            total_energy = local_sum.item()
            avg_comm_ms = (comm_time_total / step) * 1000

            if rank == 0:
                print(
                    f"Step {step:4d}/{num_steps}  |  "
                    f"Max Temp: {global_max_temp:.1f} K  |  "
                    f"Total Energy: {total_energy:.4e}  |  "
                    f"Convergence: {convergence:.2e}  |  "
                    f"Comm: {avg_comm_ms:.2f}ms"
                )

    # Final summary
    dist.barrier()
    avg_step_ms = (step_time_total / num_steps) * 1000
    avg_comm_ms = (comm_time_total / num_steps) * 1000
    comm_pct = (comm_time_total / step_time_total) * 100 if step_time_total > 0 else 0

    if rank == 0:
        print("-" * 70)
        print(f"Avg step time:  {avg_step_ms:.2f} ms")
        print(f"Avg comm time:  {avg_comm_ms:.2f} ms")
        print(f"Comm overhead:  {comm_pct:.1f}%")
        converged = convergence < 1e-3
        print(f"Converged:      {'Yes' if converged else 'No'} (final delta: {convergence:.2e})")


def main():
    rank, world_size, device = init_process()
    run_simulation(rank, world_size)
    dist.destroy_process_group()

if __name__ == "__main__":
    main()