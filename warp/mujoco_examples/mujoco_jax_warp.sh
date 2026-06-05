cd mujoco_playgrounds
source .venv/bin/activate

# Verify installation
uv --no-config run python -c "import mujoco_playground; print('Success')"

# Verify / trigger menagerie asset download
uv --no-config run python -c "from mujoco_playground import locomotion; locomotion.load('G1JoystickFlatTerrain'); print('Success')"

# Train Cartpole with JAX + Warp backends
# default 1024 envs
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl jax --num_timesteps=1000 --episode_length=500
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl warp --num_timesteps=1000 --episode_length=500

# 2048 envs
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl jax --num_timesteps=1000 --episode_length=500 --num_envs=2048
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl warp --num_timesteps=1000 --episode_length=500 --num_envs=2048

# 512 envs
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl jax --num_timesteps=1000 --episode_length=500 --num_envs=512
MUJOCO_GL=egl uv --no-config run train-jax-ppo --env_name CartpoleBalance --impl warp --num_timesteps=1000 --episode_length=500 --num_envs=512
