"""
Bước 1 – Kết nối với drone trong Gazebo, cất cánh lên 10 m, giữ một lúc rồi hạ cánh.

Chạy trên Windows (cùng máy với QGroundControl), khi mô phỏng PX4 + Gazebo đang chạy.
"""

import asyncio
from mavsdk_grpc import System

# PX4 trong container gửi "kênh dành cho chương trình" (API) tới cổng 14540 của máy Windows.
# QGroundControl dùng cổng 14550, nên hai bên không giành nhau.
DIA_CHI_KET_NOI = "udpin://0.0.0.0:14540"
DO_CAO_CAT_CANH = 10  # mét


async def in_do_cao(drone, so_lan):
    """In độ cao so với điểm cất cánh, mỗi giây một lần."""
    for _ in range(so_lan):
        async for vi_tri in drone.telemetry.position():
            print(f"   Độ cao: {vi_tri.relative_altitude_m:5.1f} m")
            break
        await asyncio.sleep(1)


async def main():
    drone = System()

    print("1) Đang chờ kết nối với drone...")
    await drone.connect(system_address=DIA_CHI_KET_NOI)
    async for trang_thai in drone.core.connection_state():
        if trang_thai.is_connected:
            print("   -> Đã kết nối!")
            break

    print("2) Đang chờ drone xác định được vị trí (GPS + điểm Home)...")
    async for suc_khoe in drone.telemetry.health():
        if suc_khoe.is_global_position_ok and suc_khoe.is_home_position_ok:
            print("   -> Vị trí OK, sẵn sàng bay")
            break

    print(f"3) Đặt độ cao cất cánh = {DO_CAO_CAT_CANH} m")
    await drone.action.set_takeoff_altitude(DO_CAO_CAT_CANH)

    print("4) Mở khóa động cơ (arm)...")
    await drone.action.arm()

    print("5) Cất cánh!")
    await drone.action.takeoff()
    await in_do_cao(drone, 20)

    print("6) Hạ cánh...")
    await drone.action.land()
    async for dang_bay in drone.telemetry.in_air():
        if not dang_bay:
            print("   -> Đã đáp đất. Xong bài 1!")
            break


if __name__ == "__main__":
    asyncio.run(main())
