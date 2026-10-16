#!/bin/bash
# Khởi động sim PX4 + Gazebo (render GPU qua WSL D3D12) với MỘT NGƯỜI ĐI BỘ trong world.
#
# Giống ~/phao/chay_gpu.sh, thêm hai dòng mount:
#   1) default_nguoi.sdf ghi đè world mặc định (thêm người đi bộ, xem file đó);
#   2) thư mục ~/phao/fuel_cache lưu model đã tải từ Gazebo Fuel, để lần khởi động sau
#      không phải tải lại (sim chạy với --rm nên không có thư mục này thì cache mất).
#
# Chạy trong WSL Ubuntu. Điều kiện: Docker Desktop đang bật, file default_nguoi.sdf
# nằm CÙNG THƯ MỤC với script này.
#   cp "/mnt/d/Intern iVista/UAV/uav-target-following/sim/"{default_nguoi.sdf,chay_gpu_nguoi.sh} ~/phao/
#   chmod +x ~/phao/chay_gpu_nguoi.sh
#   ~/phao/chay_gpu_nguoi.sh
#
# Lần đầu có thể mất 1-2 phút để tải mesh người (Gazebo có thể đứng hình trong lúc tải).

THU_MUC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THU_MUC_CACHE="$HOME/phao/fuel_cache"
mkdir -p "$THU_MUC_CACHE"

docker run --rm -it --name px4-gazebo \
  --gpus all \
  --mount type=bind,src=/mnt/wslg/.X11-unix,dst=/tmp/.X11-unix,readonly \
  --mount type=bind,src=/usr/lib/wsl,dst=/usr/lib/wsl,readonly \
  --mount type=bind,src=$HOME/phao/model.sdf,dst=/opt/px4-gazebo/share/gz/models/x500_mono_cam_down/model.sdf,readonly \
  --mount "type=bind,src=$THU_MUC_SCRIPT/default_nguoi.sdf,dst=/opt/px4-gazebo/share/gz/worlds/default.sdf,readonly" \
  --mount "type=bind,src=$THU_MUC_CACHE,dst=/root/.gz/fuel" \
  -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
  -e GALLIUM_DRIVER=d3d12 \
  -e MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA \
  -e DISPLAY=:0 -e QT_QPA_PLATFORM=xcb \
  -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
  px4io/px4-sitl-gazebo:latest
