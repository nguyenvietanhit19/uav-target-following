"""
Bước 2 – Bay plan thả phao và TỰ ĐỘNG nhả móc khi tới lệnh Gripper Action.

Script này đóng vai "người phiên dịch":
  - Nghe PX4 (qua MAVLink) xem drone đang làm tới bước nào của plan.
  - Khi tới bước Gripper Action -> gửi lệnh nhả móc cho Gazebo (kênh /phao/tha).

Chạy trên Windows, khi mô phỏng (chay_gpu.sh, có phao) đang chạy.
"""

import asyncio
import subprocess

try:
    from mavsdk_grpc import System          # tên mới của thư viện
except ImportError:
    from mavsdk import System               # tên cũ (mavsdk<4)

DIA_CHI_KET_NOI = "udpin://0.0.0.0:14540"
FILE_PLAN = "tha_phao_muc1.plan"            # file plan QGC, đặt cùng thư mục với script

# Mã số lệnh MAVLink -> tên dễ đọc (chỉ để in ra màn hình)
TEN_LENH = {
    16: "Waypoint",
    20: "Return To Launch",
    22: "Takeoff",
    211: "Gripper Action",
}
MA_GRIPPER = 211

LENH_NHA_MOC = [
    "docker", "exec", "px4-gazebo",
    "gz", "topic", "-t", "/phao/tha",
    "-m", "gz.msgs.Empty", "-p", "unused: true",
]


def nha_moc():
    """Gửi tin nhắn tới kênh /phao/tha để cái móc trong Gazebo nhả phao."""
    ket_qua = subprocess.run(LENH_NHA_MOC, capture_output=True, text=True)
    if ket_qua.returncode == 0:
        print("   >>> ĐÃ NHẢ PHAO <<<")
    else:
        print("   !!! Gửi lệnh nhả móc thất bại:", ket_qua.stderr.strip())


async def main():
    drone = System()

    print("1) Đang chờ kết nối với drone...")
    await drone.connect(system_address=DIA_CHI_KET_NOI)
    async for trang_thai in drone.core.connection_state():
        if trang_thai.is_connected:
            print("   -> Đã kết nối!")
            break

    print(f"2) Đọc plan từ file '{FILE_PLAN}'...")
    du_lieu = await drone.mission_raw.import_qgroundcontrol_mission(FILE_PLAN)
    cac_lenh = du_lieu.mission_items
    for i, lenh in enumerate(cac_lenh):
        print(f"   [{i}] {TEN_LENH.get(lenh.command, f'lệnh {lenh.command}')}")

    vi_tri_gripper = next(
        (i for i, lenh in enumerate(cac_lenh) if lenh.command == MA_GRIPPER), None
    )
    if vi_tri_gripper is None:
        print("   !!! Plan không có lệnh Gripper Action. Dừng lại.")
        return
    print(f"   -> Sẽ nhả phao khi drone tới bước [{vi_tri_gripper}]")

    print("3) Tải plan lên drone...")
    await drone.mission_raw.upload_mission(cac_lenh)

    print("4) Chờ drone xác định được vị trí...")
    async for suc_khoe in drone.telemetry.health():
        if suc_khoe.is_global_position_ok and suc_khoe.is_home_position_ok:
            print("   -> Vị trí OK")
            break

    print("5) Mở khóa động cơ và bắt đầu nhiệm vụ!")
    await drone.action.arm()
    await drone.mission_raw.start_mission()

    print("6) Theo dõi tiến trình...")
    da_nha = False
    buoc_truoc = -1
    async for tien_trinh in drone.mission_raw.mission_progress():
        if tien_trinh.current != buoc_truoc:
            buoc_truoc = tien_trinh.current
            if tien_trinh.current < len(cac_lenh):
                ten = TEN_LENH.get(cac_lenh[tien_trinh.current].command, "?")
                print(f"   Đang làm bước [{tien_trinh.current}/{tien_trinh.total}]: {ten}")

        # Tới (hoặc đã qua) bước Gripper Action mà chưa nhả -> nhả ngay
        if not da_nha and tien_trinh.current >= vi_tri_gripper:
            await asyncio.to_thread(nha_moc)
            da_nha = True

        if tien_trinh.current >= tien_trinh.total:
            print("   -> Đã xong các bước trong plan")
            break

    print("7) Chờ drone đáp đất...")
    async for dang_bay in drone.telemetry.in_air():
        if not dang_bay:
            print("   -> Đã đáp đất. Xong bài 2!")
            break


if __name__ == "__main__":
    asyncio.run(main())
