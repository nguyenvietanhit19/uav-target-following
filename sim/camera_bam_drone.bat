@echo off
REM Bat lai che do camera bam theo drone trong Gazebo.
REM Bam dup file nay tren Windows. Dieu kien: Docker Desktop dang bat va sim dang chay (container px4-gazebo).
REM Ten model drone (x500_mono_cam_down_0) lay tu danh sach vat the trong Gazebo.
REM Muon camera tu do tro lai thi bam dup camera_tu_do.bat.
REM (File nay viet khong dau vi cua so cmd cua Windows de loi font tieng Viet.)

set TEN_CONTAINER=px4-gazebo
set TEN_DRONE=x500_mono_cam_down_0

echo Dang bat che do camera bam theo drone %TEN_DRONE%...
docker exec %TEN_CONTAINER% gz service -s /gui/follow --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 3000 --req "data: \"%TEN_DRONE%\""
if errorlevel 1 (
  echo.
  echo LOI: khong gui duoc lenh. Kiem tra Docker Desktop dang bat va sim dang chay, container %TEN_CONTAINER%.
) else (
  echo.
  echo Neu thay "data: true" o tren thi camera dang bam theo drone.
)
echo.
if not defined KHONG_DUNG pause
