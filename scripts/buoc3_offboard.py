"""
Bước 3 – Offboard mode: script tự gửi lệnh VẬN TỐC cho drone.

Cách chạy (trên Windows, khi mô phỏng PX4 + Gazebo đang chạy, QGC đang mở):
    python buoc3_offboard.py A     # thí nghiệm A: tiến thẳng 1 m/s trong 3 giây
    python buoc3_offboard.py B     # thí nghiệm B: bay về Bắc, mũi quay về Đông
    python buoc3_offboard.py C     # thí nghiệm C: đứng yên, xoay 30 độ/giây trong 3 giây

Mỗi lần chạy: kết nối -> cất cánh 10 m -> làm thí nghiệm -> in kết quả -> hạ cánh.
"""

import asyncio
import math
import sys

from mavsdk_grpc import System
from mavsdk_grpc.offboard import OffboardError, VelocityBodyYawspeed, VelocityNedYaw

DIA_CHI_KET_NOI = "udpin://0.0.0.0:14540"
DO_CAO_CAT_CANH = 10  # mét

# Gửi lệnh mỗi 0,1 giây = 10 lần/giây (an toàn, vì PX4 chỉ thoát offboard
# khi im lặng quá khoảng 0,5 giây).
CHU_KY_GUI = 0.1  # giây


# ---------------------------------------------------------------------------
# Các hàm phụ: đọc dữ liệu từ drone
# ---------------------------------------------------------------------------
async def doc_vi_tri(drone):
    """Trả về (bắc, đông) tính bằng mét, so với điểm Home."""
    async for pv in drone.telemetry.position_velocity_ned():
        return pv.position.north_m, pv.position.east_m


async def doc_huong_mui(drone):
    """Trả về yaw (hướng mũi) bằng độ, 0 = Bắc, 90 = Đông."""
    async for h in drone.telemetry.heading():
        return h.heading_deg


async def doc_do_cao(drone):
    async for vt in drone.telemetry.position():
        return vt.relative_altitude_m


# ---------------------------------------------------------------------------
# Cất cánh (giống bài 1, nhưng chờ tới khi gần đủ độ cao thay vì chờ cố định)
# ---------------------------------------------------------------------------
async def ket_noi_va_cat_canh(drone):
    print("1) Đang chờ kết nối với drone...")
    await drone.connect(system_address=DIA_CHI_KET_NOI)
    async for trang_thai in drone.core.connection_state():
        if trang_thai.is_connected:
            print("   -> Đã kết nối!")
            break

    print("2) Đang chờ drone xác định được vị trí (GPS + điểm Home)...")
    async for suc_khoe in drone.telemetry.health():
        if suc_khoe.is_global_position_ok and suc_khoe.is_home_position_ok:
            print("   -> Vị trí OK")
            break

    print(f"3) Cất cánh lên {DO_CAO_CAT_CANH} m...")
    await drone.action.set_takeoff_altitude(DO_CAO_CAT_CANH)
    await drone.action.arm()
    await drone.action.takeoff()

    # Chờ tới khi đạt ít nhất 90% độ cao mong muốn
    while True:
        do_cao = await doc_do_cao(drone)
        print(f"   Độ cao: {do_cao:5.1f} m")
        if do_cao >= DO_CAO_CAT_CANH * 0.9:
            break
        await asyncio.sleep(1)

    print("   -> Đang lơ lửng, chờ 3 giây cho ổn định...")
    await asyncio.sleep(3)


# ---------------------------------------------------------------------------
# Hàm lõi: gửi một lệnh vận tốc LIÊN TỤC trong một khoảng thời gian
# ---------------------------------------------------------------------------
async def gui_lenh_lien_tuc(ham_gui, lenh, so_giay):
    """
    ham_gui: drone.offboard.set_velocity_body hoặc drone.offboard.set_velocity_ned
    lenh:    đối tượng lệnh vận tốc
    so_giay: gửi lệnh này trong bao lâu
    """
    so_lan = int(so_giay / CHU_KY_GUI)
    for _ in range(so_lan):
        await ham_gui(lenh)
        await asyncio.sleep(CHU_KY_GUI)


async def vao_offboard(drone):
    """Luật 1: gửi lệnh 'đứng yên' trước. Luật 2: rồi mới bật offboard."""
    dung_yen = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
    await drone.offboard.set_velocity_body(dung_yen)
    try:
        await drone.offboard.start()
    except OffboardError as loi:
        print(f"   !!! Không vào được offboard: {loi}")
        print("   -> Hạ cánh để an toàn.")
        await drone.action.land()
        raise SystemExit(1)
    print("   -> Đã vào offboard mode (script đang cầm lái)")


async def thoat_offboard(drone):
    """Gửi 'đứng yên' vài giây cho drone dừng hẳn, rồi trả lái lại cho PX4."""
    dung_yen = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
    await gui_lenh_lien_tuc(drone.offboard.set_velocity_body, dung_yen, 2)
    try:
        await drone.offboard.stop()
    except OffboardError as loi:
        print(f"   !!! Lỗi khi thoát offboard: {loi}")
    print("   -> Đã thoát offboard (PX4 lái lại)")


# ---------------------------------------------------------------------------
# Ba thí nghiệm
# ---------------------------------------------------------------------------
async def thi_nghiem_A(drone):
    """Tiến thẳng 1 m/s trong 3 giây (body frame). Kỳ vọng: đi ~3 m theo hướng mũi."""
    print("== THÍ NGHIỆM A: tiến 1 m/s trong 3 giây (body frame) ==")
    lenh = VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0)  # (tiến, phải, xuống, yaw rate)
    ham = drone.offboard.set_velocity_body
    return lenh, ham, 3


async def thi_nghiem_B(drone):
    """Bay về Bắc 1 m/s trong khi mũi quay về Đông (NED). Kỳ vọng: đi ~3 m về Bắc."""
    print("== THÍ NGHIỆM B: bay về Bắc 1 m/s, mũi hướng Đông (NED) ==")
    lenh = VelocityNedYaw(1.0, 0.0, 0.0, 90.0)  # (bắc, đông, xuống, yaw tuyệt đối)
    ham = drone.offboard.set_velocity_ned
    return lenh, ham, 3


async def thi_nghiem_C(drone):
    """Đứng yên, xoay 30 độ/giây trong 3 giây. Kỳ vọng: mũi xoay thêm ~90 độ."""
    print("== THÍ NGHIỆM C: xoay 30 độ/giây trong 3 giây (body frame) ==")
    lenh = VelocityBodyYawspeed(0.0, 0.0, 0.0, 30.0)
    ham = drone.offboard.set_velocity_body
    return lenh, ham, 3


THI_NGHIEM = {"A": thi_nghiem_A, "B": thi_nghiem_B, "C": thi_nghiem_C}


async def main():
    ten = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
    if ten not in THI_NGHIEM:
        print("Dùng: python buoc3_offboard.py A | B | C")
        return

    drone = System()
    await ket_noi_va_cat_canh(drone)

    lenh, ham_gui, so_giay = await THI_NGHIEM[ten](drone)

    # Đo trước khi làm thí nghiệm
    bac0, dong0 = await doc_vi_tri(drone)
    yaw0 = await doc_huong_mui(drone)
    print(f"   Trước: vị trí (bắc {bac0:6.2f}, đông {dong0:6.2f}) m, hướng mũi {yaw0:6.1f}°")

    await vao_offboard(drone)
    print(f"   Đang gửi lệnh liên tục trong {so_giay} giây...")
    await gui_lenh_lien_tuc(ham_gui, lenh, so_giay)

    # Đo ngay sau khi gửi lệnh (trước khi dừng hẳn)
    bac1, dong1 = await doc_vi_tri(drone)
    yaw1 = await doc_huong_mui(drone)

    await thoat_offboard(drone)

    # Đo lại sau khi đã dừng hẳn
    bac2, dong2 = await doc_vi_tri(drone)
    yaw2 = await doc_huong_mui(drone)

    quang_duong = math.hypot(bac2 - bac0, dong2 - dong0)
    # Góc xoay thực tế, tính theo đường ngắn nhất trong khoảng -180..180
    goc_xoay = (yaw2 - yaw0 + 180) % 360 - 180

    print("\n--- KẾT QUẢ ---")
    print(f"Sau khi gửi lệnh: vị trí (bắc {bac1:6.2f}, đông {dong1:6.2f}) m, hướng mũi {yaw1:6.1f}°")
    print(f"Sau khi dừng hẳn: vị trí (bắc {bac2:6.2f}, đông {dong2:6.2f}) m, hướng mũi {yaw2:6.1f}°")
    print(f"Quãng đường đã đi (từ lúc bắt đầu): {quang_duong:.2f} m")
    print(f"Thay đổi bắc: {bac2 - bac0:+.2f} m, thay đổi đông: {dong2 - dong0:+.2f} m")
    print(f"Mũi xoay thêm: {goc_xoay:+.1f}°")

    print("\nSo với kỳ vọng:")
    if ten == "A":
        print("  Kỳ vọng: ~3 m theo hướng mũi (vận tốc 1 m/s x 3 giây).")
        print("  Gợi ý: vận tốc không tức thì đạt 1 m/s nên có thể hơi lệch vài chục cm.")
    elif ten == "B":
        print("  Kỳ vọng: ~+3 m về Bắc, đông ~0, hướng mũi gần 90° (Đông).")
    else:
        print("  Kỳ vọng: vị trí gần như không đổi, mũi xoay ~+90°.")

    print("\n4) Hạ cánh...")
    await drone.action.land()
    async for dang_bay in drone.telemetry.in_air():
        if not dang_bay:
            print("   -> Đã đáp đất. Xong thí nghiệm!")
            break


if __name__ == "__main__":
    asyncio.run(main())
