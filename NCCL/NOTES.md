# Notes about NCCL

## NCCL's Core Operations

### AllReduce
Every GPU has it's own array. All arrays get summed (or max'd, min'd, etc.) together, and every GPU ends up with the same final result.
1. ReduceScatter: each GPU accumulates a slice
2. AllGather: everyone shares their slice
This is bandwidth-optimal.
In distributed training, each GPU computes gradients on its own batch of data. AllReduce sums the gradients across all GPUs so every GPU has the global gradient and can update weights identically.
Another use case is averaging model weights across nodes (term: federated averaging).

### Broadcast
One GPU (the "root") has data. It sends the data to all other GPUs.
In training startup, the initial model weights are broadcast to all GPUs. In HPC, boundary conditions or global parameters in simulations are broadcast to all GPUs. 

### Reduce
This is like AllReduce, but only the root GPU gets the final result. Everyone else's copy is discarded.
In distributing training, sometimes one node is the dedicated "parameter server" whose only job is to store the master copy of the model weights (older/less common approach). 
In HPC, Reduce can compute a global sum/max for convergence checks (i.e., has the solution converged yet/has the error gotten small enough to stop?) without needeing the result everywhere. 

### AllGather
Each GPU holds a unique chunk. After AllGather, every GPU has all chunks connected together.
In AI/ML, this is seen in tensor parallelism, where a model layer is split across GPUs, so each GPU holds part of the weight matrix. Before computing, GPUs need the full weight.
Sometimes, model parameters are sharded across GPUs to same memory, then have to be reconstructed just in time for the forward pass.

### ReduceScatter
All GPUs contribute data, it gets reduced (summed), and each GPU only gets one chunk of the result. Opposite of AllGather.
In AI/ML, sometimes each GPU only stores and updates its shard of the gradients, which reduces memory usage. This is how 100B+ parameter models are trained.
Used in the AllReduce operation.

### AllToAll
Each GPU sends a different chunk to each other GPU. Full personalized exchange (GPU 0 sends slice 0 to GPU 0, slice 1 to GPU 1, slice 2 to GPU 2, etc.).
The biggest current use case is Mixture of Experts (MoE), where tokens are routed to different expert layers on different GPUs, then results are shipped back.
In Fast Fourier Transform (FFT) at scale, FFTs are decomposed across nodes. In training, AllToAll is required to combine data, tensor, and pipeline parallelism for expert routing.

### Send / Recv
Direct GPU-to-GPU transfer. GPU A sends data to GPU B.
For AI/ML pipeline parallelism, where a model is split across GPUs, so GPU 0 runs layers 1-4, sends activations to GPU 1 which runs layers 5-8, etc. Each stage sends to the next via Send/Recv.
Any scenario where the communication is irregular and not a clean collective.

### Fun Applications outisde AI/ML!
- Molecular dynamics: forces on atoms are computed locally then AllReduced to get global forces across the whole system
- Climate modeling: atmosphere grid is split across GPUs and AllReduce computes global statistics like total energy, mass conservation checks. 
- Graph analytics: AllReduce for propagating vertex values across partitions in distributed graph algorithms
