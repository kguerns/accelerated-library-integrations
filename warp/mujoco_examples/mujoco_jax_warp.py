#!/usr/bin/env python3
"""Run the MuJoCo JAX/Warp training sweep and save terminal output per run."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

PLAYGROUND_DIR = Path(__file__).resolve().parent / "mujoco_playground"
LOGDIR_PATTERN = re.compile(r"Logs are being stored in: (.+)")
OUTPUT_FILENAME = "terminal_output.txt"

VERIFY_COMMANDS = [
    ["uv", "--no-config", "run", "python", "-c", "import mujoco_playground; print('Success')"],
    [
        "uv",
        "--no-config",
        "run",
        "python",
        "-c",
        "from mujoco_playground import locomotion; "
        "locomotion.load('G1JoystickFlatTerrain'); print('Success')",
    ],
]

TRAINING_SWEEP = [
    # vary num_envs for PPO training
    {"env_name": "CartpoleBalance", "impl": "jax", "num_timesteps": 1000, "episode_length": 500, "num_envs": 1024}, # default 1024 envs
    {"env_name": "CartpoleBalance", "impl": "warp", "num_timesteps": 1000, "episode_length": 500, "num_envs": 1024}, # default 1024 envs
    {
        "env_name": "CartpoleBalance",
        "impl": "jax",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 2048,
    },
    {
        "env_name": "CartpoleBalance",
        "impl": "warp",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 2048,
    },
    {
        "env_name": "CartpoleBalance",
        "impl": "jax",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 512,
    },
    {
        "env_name": "CartpoleBalance",
        "impl": "warp",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 512,
    },
    {
        "env_name": "CartpoleBalance",
        "impl": "jax",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 4096,
    },
    {
        "env_name": "CartpoleBalance",
        "impl": "warp",
        "num_timesteps": 1000,
        "episode_length": 500,
        "num_envs": 4096,
    },
]


def build_train_command(config: dict[str, object]) -> list[str]:
    cmd = ["uv", "--no-config", "run", "train-jax-ppo"]
    for key, value in config.items():
        cmd.append(f"--{key}={value}")
    return cmd


def run_command(cmd: list[str], *, env: dict[str, str], cwd: Path) -> tuple[int, Path | None]:
    """Run a command, echo output live, and tee to the run log folder when known."""
    print(f"\n>>> {' '.join(cmd)}\n", flush=True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        cwd=cwd,
    )

    log_file = None
    log_path: Path | None = None
    buffered: list[str] = []

    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()

        if log_file is None:
            buffered.append(line)
            match = LOGDIR_PATTERN.search(line)
            if match:
                log_path = Path(match.group(1).strip()) / OUTPUT_FILENAME
                log_path.parent.mkdir(parents=True, exist_ok=True)
                log_file = log_path.open("w", encoding="utf-8")
                log_file.writelines(buffered)
                log_file.flush()
        else:
            log_file.write(line)
            log_file.flush()

    returncode = process.wait()
    if log_file is not None:
        log_file.close()
        print(f"Saved terminal output to: {log_path}", flush=True)
    elif returncode == 0:
        print(
            "Warning: command succeeded but no log directory was detected in output.",
            flush=True,
        )

    return returncode, log_path


def main() -> int:
    if not PLAYGROUND_DIR.is_dir():
        print(f"Expected playground directory at {PLAYGROUND_DIR}", file=sys.stderr)
        return 1

    env = {**os.environ, "MUJOCO_GL": "egl"}

    for cmd in VERIFY_COMMANDS:
        returncode, _ = run_command(cmd, env=env, cwd=PLAYGROUND_DIR)
        if returncode != 0:
            print(f"Verification failed: {' '.join(cmd)}", file=sys.stderr)
            return returncode

    for config in TRAINING_SWEEP:
        cmd = build_train_command(config)
        returncode, _ = run_command(cmd, env=env, cwd=PLAYGROUND_DIR)
        if returncode != 0:
            print(f"Training run failed: {' '.join(cmd)}", file=sys.stderr)
            return returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
