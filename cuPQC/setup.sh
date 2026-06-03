#!/usr/bin/env bash
# setup.sh — one-step cuPQC environment setup for a Brev (x86_64 Linux) instance
# Run once after spinning up a new instance: bash setup.sh
set -euo pipefail

CUPQC_VERSION="0.4.1"
CUPQC_SDK_URL="https://developer.download.nvidia.com/compute/cupqc/redist/cupqc/cupqc-sdk-${CUPQC_VERSION}-x86_64.tar.gz"
INSTALL_DIR="/usr/local/cupqc-sdk"
TARBALL="cupqc-sdk-${CUPQC_VERSION}-x86_64.tar.gz"

# ── 1. Check CUDA ────────────────────────────────────────────────────────────
echo "==> Checking CUDA..."
if ! command -v nvcc &>/dev/null; then
    echo "ERROR: nvcc not found. Ensure this instance has CUDA 12.8+ installed."
    echo "       On Brev, select a container image with CUDA 12.8 or later."
    exit 1
fi

CUDA_VER=$(nvcc --version | grep -oP 'release \K[0-9]+\.[0-9]+')
CUDA_MAJOR=$(echo "$CUDA_VER" | cut -d. -f1)
CUDA_MINOR=$(echo "$CUDA_VER" | cut -d. -f2)

if [[ "$CUDA_MAJOR" -lt 12 ]] || { [[ "$CUDA_MAJOR" -eq 12 ]] && [[ "$CUDA_MINOR" -lt 8 ]]; }; then
    echo "ERROR: CUDA 12.8+ required, found ${CUDA_VER}."
    exit 1
fi
echo "    CUDA ${CUDA_VER} ✓"

# ── 2. Check GPU architecture ────────────────────────────────────────────────
echo "==> Checking GPU..."
if ! command -v nvidia-smi &>/dev/null; then
    echo "ERROR: nvidia-smi not found. Is a GPU attached to this instance?"
    exit 1
fi
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader | head -1
SM_VER=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | tr -d '.')
SUPPORTED_SMS=(70 75 80 86 87 89 90)
if [[ ! " ${SUPPORTED_SMS[*]} " =~ " ${SM_VER} " ]]; then
    echo "WARNING: SM ${SM_VER} may not be supported. Supported: ${SUPPORTED_SMS[*]}"
fi
echo "    SM_${SM_VER} ✓"

# ── 3. CMake 3.20+ ───────────────────────────────────────────────────────────
echo "==> Checking CMake..."
if command -v cmake &>/dev/null; then
    CMAKE_VER=$(cmake --version | head -1 | grep -oP '[0-9]+\.[0-9]+')
    CMAKE_MAJOR=$(echo "$CMAKE_VER" | cut -d. -f1)
    CMAKE_MINOR=$(echo "$CMAKE_VER" | cut -d. -f2)
    if [[ "$CMAKE_MAJOR" -gt 3 ]] || { [[ "$CMAKE_MAJOR" -eq 3 ]] && [[ "$CMAKE_MINOR" -ge 20 ]]; }; then
        echo "    CMake ${CMAKE_VER} ✓"
    else
        echo "    CMake ${CMAKE_VER} too old, upgrading via pip..."
        pip install --upgrade cmake --break-system-packages -q
    fi
else
    echo "    CMake not found, installing via pip..."
    pip install cmake --break-system-packages -q
fi

# ── 4. Build tools ───────────────────────────────────────────────────────────
echo "==> Installing build tools (git, wget, g++)..."
sudo apt-get update -qq
sudo apt-get install -y -qq git wget build-essential

# ── 5. Download and install cuPQC SDK ────────────────────────────────────────
echo "==> Installing cuPQC SDK ${CUPQC_VERSION}..."
if [[ -d "$INSTALL_DIR" ]]; then
    echo "    ${INSTALL_DIR} already exists, skipping download."
else
    TMP=$(mktemp -d)
    echo "    Downloading SDK..."
    wget -q --show-progress -O "${TMP}/${TARBALL}" "$CUPQC_SDK_URL"
    echo "    Extracting..."
    tar -xzf "${TMP}/${TARBALL}" -C "$TMP"
    sudo mv "${TMP}/cupqc-sdk-${CUPQC_VERSION}-x86_64" "$INSTALL_DIR"
    rm -rf "$TMP"
    echo "    Installed to ${INSTALL_DIR} ✓"
fi

# ── 6. Set environment variable ──────────────────────────────────────────────
echo "==> Configuring CUPQC_SDK_DIR..."
EXPORT_LINE="export CUPQC_SDK_DIR=${INSTALL_DIR}"
if ! grep -qF "$EXPORT_LINE" ~/.bashrc; then
    echo "$EXPORT_LINE" >> ~/.bashrc
fi
export CUPQC_SDK_DIR="$INSTALL_DIR"
echo "    CUPQC_SDK_DIR=${CUPQC_SDK_DIR} ✓"

# ── 7. Clone NVIDIA/cuPQC examples (if not already present) ─────────────────
echo "==> Cloning NVIDIA/cuPQC examples..."
EXAMPLES_DIR="$HOME/workspace/cuPQC-examples"
if [[ -d "$EXAMPLES_DIR" ]]; then
    echo "    Already cloned at ${EXAMPLES_DIR}, pulling latest..."
    git -C "$EXAMPLES_DIR" pull -q
else
    git clone -q https://github.com/NVIDIA/cuPQC.git "$EXAMPLES_DIR"
    echo "    Cloned to ${EXAMPLES_DIR} ✓"
fi

# ── 8. Verify installation ───────────────────────────────────────────────────
echo "==> Verifying installation..."
ls "$CUPQC_SDK_DIR/include" | grep -E "pk.hpp|hash.hpp" | sed 's/^/    /'
ls "$CUPQC_SDK_DIR/lib"     | grep -E "\.a$"            | sed 's/^/    /'

# ── 9. Build bundled examples to confirm compiler chain works ────────────────
echo "==> Building SDK examples (smoke test)..."
BUILD_DIR="${EXAMPLES_DIR}/build"
mkdir -p "$BUILD_DIR"
cmake -S "$EXAMPLES_DIR" -B "$BUILD_DIR" \
    -DCMAKE_PREFIX_PATH="${CUPQC_SDK_DIR}/cmake" \
    -DCUPQC_SDK_DIR="$CUPQC_SDK_DIR" \
    -DCMAKE_CUDA_ARCHITECTURES="$SM_VER" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_VERBOSE_MAKEFILE=OFF \
    > /dev/null 2>&1
cmake --build "$BUILD_DIR" --parallel "$(nproc)" > /dev/null 2>&1
echo "    Examples built successfully ✓"

echo ""
echo "══════════════════════════════════════════════"
echo "  cuPQC setup complete."
echo "  SDK:      ${CUPQC_SDK_DIR}"
echo "  Examples: ${EXAMPLES_DIR}"
echo "  SM arch:  sm_${SM_VER}"
echo ""
echo "  To compile your own .cu file:"
echo "    nvcc -std=c++17 -dlto -arch=sm_${SM_VER} \\"
echo "         -I\${CUPQC_SDK_DIR}/include \\"
echo "         -L\${CUPQC_SDK_DIR}/lib -lcupqc-pk \\"
echo "         your_file.cu -o your_program"
echo "══════════════════════════════════════════════"
