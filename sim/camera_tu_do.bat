@echo off
REM Tat che do camera bam theo drone trong Gazebo -> camera tu do (keo chuot de di chuyen, lan chuot de zoom).
REM Bam dup file nay tren Windows. Dieu kien: Docker Desktop dang bat va sim dang chay (container px4-gazebo).
REM Dung chuoi rong cho dich vu /gui/follow nghia la "khong bam theo vat nao".
REM (File nay viet khong dau vi cua so cmd cua Windows de loi font tieng Viet.)

set TEN_CONTAINER=px4-gazebo

echo Dang tat che do camera bam theo drone...
docker exec %TEN_CONTAINER% gz service -s /gui/follow --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 3000 --req "data: \"\""
if errorlevel 1 (
  echo.
  echo LOI: khong gui duoc lenh. Kiem tra Docker Desktop dang bat va sim dang chay, container %TEN_CONTAINER%.
) else (
  echo.
  echo Neu thay "data: true" o tren thi camera da tu do. Thu keo chuot trong cua so Gazebo.
)
echo.
if not defined KHONG_DUNG pause
