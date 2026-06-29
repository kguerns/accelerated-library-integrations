"""
Basic Example with NCCL
For 4 GPUs, run with: torchrun --nproc_per_node=4 examples/basic_collectives.py
"""
import torch
import torch.distributed as dist

def init_process():
    """
    Connects all GPU processes together.
    """
    dist.init_process_group(backend="nccl")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    return rank, world_size

def time_operation(op):
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    op()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end)

def print_result(name, before, after, latency_ms, correct):
    if dist.get_rank() == 0:
        print(f"\n=== {name} ===")
        print(f"Before: {before}")
        print(f"After:  {after}")
        print(f"Latency: {latency_ms:.3f} ms  |  Correct: {'✓' if correct else '✗'}")

def run_allreduce(rank, world_size):
    tensor = torch.ones(1, dtype=torch.float32).cuda(rank)
    before = f"GPU{rank}=[{tensor.item():.2f}]"
    latency = time_operation(lambda: dist.all_reduce(tensor, op=dist.ReduceOp.SUM))
    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = torch.allclose(tensor, torch.tensor([float(world_size)]).cuda(rank))
    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("AllReduce", "  ".join(befores), "  ".join(afters), latency, correct)

def run_broadcast(rank, world_size):
    tensor = torch.tensor([5.0] if rank == 0 else [0.0]).cuda(rank)
    before = f"GPU{rank}=[{tensor.item():.2f}]"
    latency = time_operation(lambda: dist.broadcast(tensor, src=0))
    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = torch.allclose(tensor, torch.tensor([5.0]).cuda(rank))
    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("Broadcast", "  ".join(befores), "  ".join(afters), latency, correct)

def run_allgather(rank, world_size):
    tensor = torch.tensor([float(rank + 1)]).cuda(rank)
    before = f"GPU{rank}=[{tensor.item():.2f}]"
    gathered = [torch.zeros(1).cuda(rank) for _ in range(world_size)]
    latency = time_operation(lambda: dist.all_gather(gathered, tensor))
    gathered_vals = [f"{t.item():.2f}" for t in gathered]
    after = f"GPU{rank}=[{', '.join(gathered_vals)}]"
    expected = list(range(1, world_size + 1))
    correct = all(torch.allclose(gathered[i], torch.tensor([float(expected[i])]).cuda(rank)) for i in range(world_size))
    dist.barrier()
    befores = [None] * world_size
    dist.all_gather_object(befores, before)
    print_result("AllGather", "  ".join(befores), after + " (all GPUs identical)", latency, correct)

def run_reducescatter(rank, world_size):
    tensor = torch.tensor([float(rank + 1) * i for i in range(1, world_size + 1)]).cuda(rank)
    before = f"GPU{rank}={[f'{v:.2f}' for v in tensor.tolist()]}"
    output = torch.zeros(1).cuda(rank)
    latency = time_operation(lambda: dist.reduce_scatter_tensor(output, tensor, op=dist.ReduceOp.SUM))
    after = f"GPU{rank}=[{output.item():.2f}]"
    correct = output.item() > 0
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("ReduceScatter", "  ".join(befores), "  ".join(afters), latency, correct)

def run_send_recv(rank, world_size):
    if world_size < 2:
        if rank == 0:
            print("\n=== Send/Recv ===")
            print("Skipped — requires 2+ GPUs")
        return
    tensor = torch.tensor([42.0] if rank == 0 else [0.0]).cuda(rank)
    before = f"GPU{rank}=[{tensor.item():.2f}]"
    def send_recv():
        if rank == 0:
            dist.send(tensor, dst=1)
        elif rank == 1:
            dist.recv(tensor, src=0)
    latency = time_operation(send_recv)
    after = f"GPU{rank}=[{tensor.item():.2f}]"
    correct = (rank != 1) or torch.allclose(tensor, torch.tensor([42.0]).cuda(rank))
    dist.barrier()
    befores = [None] * world_size
    afters = [None] * world_size
    dist.all_gather_object(befores, before)
    dist.all_gather_object(afters, after)
    print_result("Send/Recv", "  ".join(befores), "  ".join(afters), latency, correct)

def main():
    rank, world_size = init_process()

    if rank == 0:
        print(f"\nNCCL Basic Collectives Demo")
        print(f"GPUs: {world_size}  |  NCCL version: {torch.cuda.nccl.version()}")

    run_allreduce(rank, world_size)
    run_broadcast(rank, world_size)
    run_allgather(rank, world_size)
    run_reducescatter(rank, world_size)
    run_send_recv(rank, world_size)

    if rank == 0:
        print("\nDone.")

    dist.destroy_process_group()

if __name__ == "__main__":
    main()