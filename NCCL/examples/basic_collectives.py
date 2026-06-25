"""
Basic Example with NCCL
For 4 GPUs, run with: torchrun --nproc_per_node=4 examples/basic_collectives.py
"""
import torch
import torch.distributed as dist
import os

def init_process():
    """
    Connects all GPU processes together. 
    """
    dist.init_process_group(backend="nccl") # make processes aware of each other and establish NCCL communication channels
    rank = dist.get_rank()
    world_size = dist.get_world_size()  # total number of processes
    torch.cuda.set_device(rank)     # pins each process to its own GPU
    return rank, world_size

def time_operation(op):
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    op()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end)

def bandwidth(data_size_bytes, latency_ms):
    return (data_size_bytes / 1e9) / (latency_ms / 1e3) # convert to GB/s

def print_result(name, before, after, latency_ms, bw, correct):
    rank = dist.get_rank()
    if rank == 0:
        print(f"\n=== {name} ===")
        print(f"Before: {before}")
        print(f"After:  {after}")
        print(f"Latency: {latency_ms:.3f} ms  |  Bandwidth: {bw:.2f} GB/s  |  Correct: {'✓' if correct else '✗'}")

def run_allreduce(rank, world_size):
    tensor = torch.ones(1, dtype=torch.float32).cuda(rank)  # GPUs start with [1.0]
    before = f"GPU{rank}=[{tensor.item():.2f}]"

    latency = time_operation(lambda: dist.all_reduce(tensor, op=dist.ReduceOp.SUM)) # allreduce op

    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = torch.allclose(tensor, torch.tensor([float(world_size)]).cuda(rank))  # verify correctness
    bw = bandwidth(tensor.element_size() * tensor.numel() * 2 * (world_size - 1) / world_size, latency)

    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before) # gather strings from all processors onto rank 0
    dist.all_gather_object(afters, after)
    print_result("AllReduce", "  ".join(befores), "  ".join(afters), latency, bw, correct)

def run_broadcast(rank, world_size):
    tensor = torch.tensor([5.0] if rank == 0 else [0.0]).cuda(rank) # rank 0 starts with [5.0], others have [0.0]
    before = f"GPU{rank}=[{tensor.item():.2f}]"

    latency = time_operation(lambda: dist.broadcast(tensor, src=0)) # broadcast op

    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = torch.allclose(tensor, torch.tensor([5.0]).cuda(rank))
    bw = bandwidth(tensor.element_size() * tensor.numel(), latency)

    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("Broadcast", "  ".join(befores), "  ".join(afters), latency, bw, correct)

def run_allgather(rank, world_size):
    tensor = torch.tensor([float(rank + 1)]).cuda(rank) # GPu 0 has [1.0], GPU 1 has [2.0], etc (unique values)
    before = f"GPU{rank}=[{tensor.item():.2f}]"

    gathered = [torch.zeros(1).cuda(rank) for _ in range(world_size)]   # list of empty tensors for NCCL to write to
    latency = time_operation(lambda: dist.all_gather(gathered, tensor)) # allgather op

    gathered_vals = [f"{t.item():.2f}" for t in gathered]
    after = f"GPU{rank}=[{', '.join(gathered_vals)}]"
    expected = list(range(1, world_size + 1))
    correct = all(torch.allclose(gathered[i], torch.tensor([float(expected[i])]).cuda(rank)) for i in range(world_size))
    bw = bandwidth(tensor.element_size() * tensor.numel() * (world_size - 1) / world_size, latency)

    dist.barrier()
    befores = [None] * world_size
    dist.all_gather_object(befores, before)
    print_result("AllGather", "  ".join(befores), after + " (all GPUs identical)", latency, bw, correct)

def run_reducescatter(rank, world_size):
    tensor = torch.tensor([float(rank + 1) * i for i in range(1, world_size + 1)]).cuda(rank) # GPUs start with unique full-length tensors
    before = f"GPU{rank}={[f'{v:.2f}' for v in tensor.tolist()]}"

    output = torch.zeros(1).cuda(rank)
    latency = time_operation(lambda: dist.reduce_scatter_tensor(output, tensor, op=dist.ReduceOp.SUM))

    after = f"GPU{rank}=[{output.item():.2f}]"
    bw = bandwidth(tensor.element_size() * tensor.numel() * (world_size - 1) / world_size, latency)
    correct = output.item() > 0

    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("ReduceScatter", "  ".join(befores), "  ".join(afters), latency, bw, correct)

def run_send_recv(rank, world_size):
    if world_size < 2:
        if rank == 0:
            print("\n=== Send/Recv ===")
            print("Skipped — requires 2+ GPUs")
        return

    tensor = torch.tensor([42.0] if rank == 0 else [0.0]).cuda(rank)
    before = f"GPU{rank}=[{tensor.item():.2f}]"

    def send_recv():    # send [42.0] from rank 0 to rank 1
        if rank == 0:
            dist.send(tensor, dst=1)
        elif rank == 1:
            dist.recv(tensor, src=0)

    latency = time_operation(send_recv)

    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = (rank != 1) or torch.allclose(tensor, torch.tensor([42.0]).cuda(rank))
    bw = bandwidth(tensor.element_size() * tensor.numel(), latency)

    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("Send/Recv", "  ".join(befores), "  ".join(afters), latency, bw, correct)

def main():
    rank, world_size = init_process()

    if rank == 0:
        print(f"\nNCCL Basic Collectives Demo")
        print(f"GPUs: {world_size}  |  NCCL version: {torch.cuda.nccl.version()}")
        print(f"NOTE: Bandwidth numbers are meaningful at 2+ GPUs only")

    run_allreduce(rank, world_size)
    run_broadcast(rank, world_size)
    run_allgather(rank, world_size)
    run_reducescatter(rank, world_size)
    run_send_recv(rank, world_size)

    if rank == 0:
        print("\nDone.")

    dist.destroy_process_group()    # close NCCL communication gracefully

if __name__ == "__main__":
    main()