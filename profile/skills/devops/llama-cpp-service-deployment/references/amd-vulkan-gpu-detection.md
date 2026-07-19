# AMD GPU Detection & Vulkan Verification

## Hardware Detection

```bash
# PCI device identification
lspci -nn | grep -i -E "(vga|display|3d)"
# Output: 03:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] HawkPoint2 [1002:1901] rev c8

# GPU details
lspci -v -s 03:00.0
# Kernel driver: amdgpu
# Kernel modules: amdgpu

# DRM devices
ls -la /dev/dri/
# card1, renderD128 present

# OpenGL renderer
glxinfo | grep -i "opengl renderer"
# AMD Radeon 740M Graphics (radeonsi, phoenix2, LLVM 18.1.8)

# Vulkan devices
vulkaninfo | grep -A5 "deviceName"
# deviceName = AMD Radeon 740M Graphics (RADV PHOENIX2)
```

## Vulkan ICD Configuration

```bash
# ICD files
ls /usr/share/vulkan/icd.d/
# radeon_icd.x86_64.json  (provided by mesa-vulkan-drivers)

# Verify ICD loads
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json vulkaninfo --summary
```

## llama.cpp Vulkan Backend Verification

```bash
# Check linked libraries
ldd /path/to/llama-server | grep -i vulkan
# libggml-vulkan.so.0 => /path/to/build-vulkan/bin/libggml-vulkan.so.0

# Runtime log signature (journalctl)
# ggml_vk_init: found 1 Vulkan devices
# Vulkan0 : AMD Radeon 740M Graphics (RADV PHOENIX2) (12800 MiB, 11827 MiB free)
```

## Key Facts for AMD 740M (HawkPoint2 / Phoenix2)

| Property | Value |
|----------|-------|
| PCI ID | 1002:1901 |
| Architecture | RDNA 3 (GFX1103) |
| Compute Units | 4 |
| Max Frequency | ~2.8 GHz |
| Shared VRAM | 12.8 GB (system RAM) |
| Vulkan Driver | RADV (Mesa) |
| OpenCL | rusticl (Mesa) — experimental |
| ROCm | Not supported on Phoenix2 APU |

## Required Packages (Debian/Ubuntu)

```bash
sudo apt install -y \
    mesa-vulkan-drivers \
    vulkan-tools \
    libvulkan1 \
    libdrm-amdgpu1 \
    firmware-amd-graphics
```