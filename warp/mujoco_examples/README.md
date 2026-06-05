# Mujoco Examples



## Requirements
- CUDA-enabled NVIDIA GPU
- Python 3.10+
- Linux

## Mujoco Playground
[Mujoco Playground](https://github.com/google-deepmind/mujoco_playground/tree/main#) is a suite of GPU-accelerated environments for robot learning built with [MuJoCo MJX](https://github.com/google-deepmind/mujoco/tree/main/mjx), an implementation of the MuJoCo physics engine in JAX. Mujoco Playground (installed from source at [`/mujoco_playground`](/warp/mujoco_examples/mujoco_playground/)) supports both JAX and NVIDIA Warp based backends. While JAX is performant for small environments, the Warp backend leveraging [`mujoco_warp`](https://github.com/google-deepmind/mujoco_warp) enables efficient scaling to larger and more complex scenes. 

To build `mujoco_playground` from source:
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. From `warp/mujoco_examples`: `cd mujoco_playground`
3. Create a virtual environment: `uv venv --python 3.12`
4. Activate the venv: `source .venv/bin/activate`
5. Install CUDA 12 jax: `uv pip install -U "jax[cuda12]" --index-url https://pypi.org/simple`
    - Verify GPU backend: `python -c "import jax; print(jax.default_backend())"` should print gpu. `unset LD_LIBRARY_PATH` may need to be run before running this command.
6. Install playground from source: `uv --no-config sync --all-extras`
7. Verify installation: `uv --no-config run python -c "import mujoco_playground; print('Success')"`
    - Note: Menagerie assets will be downloaded automatically the first time you load a locomotion or manipulation environment. You can trigger this with:  uv --no-config run python -c "from mujoco_playground import locomotion; locomotion.load('G1JoystickFlatTerrain')"   



