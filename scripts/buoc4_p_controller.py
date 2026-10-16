"""
Bước 4 – Bộ điều khiển P: drone bám theo một MỤC TIÊU ẢO đi theo ĐƯỜNG THẲNG.

Làm gì:
    Code tự tạo một điểm "mục tiêu ảo" chuyển động thẳng đều. Mỗi 0,1 giây script đọc
    vị trí drone, tính sai số so với "khoảng cách giữ", rồi gửi lệnh vận tốc:
        vận_tốc_lệnh = [vận_tốc_mục_tiêu nếu bật feedforward] + Kp × sai_số
    (chỉ điều khiển 2 chiều bắc/đông; vận tốc xuống = 0 để giữ độ cao, xem docs/05 mục 9).
    Mục tiêu ảo được vẽ thành một quả cầu đỏ trong Gazebo để quan sát (HIEN_THI_GAZEBO,
    xem hien_thi_gazebo.py; cần docker dùng được và container px4-gazebo đang chạy).

Cách chạy (trên Windows, khi mô phỏng PX4 + Gazebo đang chạy, QGC đang mở):
    python buoc4_p_controller.py              # dùng các hằng số ở đầu file
    python buoc4_p_controller.py 0.5 p        # Kp = 0,5, chỉ dùng P thuần
    python buoc4_p_controller.py 0.5 ff       # Kp = 0,5, P + feedforward
    python buoc4_p_controller.py 0.2 ff       # đổi Kp để so sánh (thử 0,2 / 0,5 / 1,0)
    python buoc4_p_controller.py 0.5 ff khong_cau   # không vẽ quả cầu trong Gazebo (sim nhẹ hơn)

Điều kiện cần:
    - Sim đang chạy; nên KHỞI ĐỘNG LẠI sim giữa các lần chạy để vị trí bắt đầu lại từ (0, 0).
    - Lưu ý RTF (tốc độ sim so với thời gian thật) khoảng 0,6 làm vòng điều khiển trễ hơn,
      nên Kp tốt trong sim có thể nhỏ hơn dự kiến. Mục tiêu ảo đi theo đồng hồ THẬT,
      còn drone bay theo thời gian SIM, nên mục tiêu có thể "chạy nhanh hơn" drone nhìn thấy.
"""

import asyncio
import math
import sys
import time
from collections import deque

from mavsdk_grpc import System
from mavsdk_grpc.offboard import OffboardError, VelocityNedYaw

from hien_thi_gazebo import MucTieuGazebo

# ---------------------------------------------------------------------------
# Hằng số cấu hình (sửa ở đây để thử nghiệm)
# ---------------------------------------------------------------------------
DIA_CHI_KET_NOI = "udpin://0.0.0.0:14540"
DO_CAO_CAT_CANH = 10  # mét

# Gửi lệnh mỗi 0,1 giây = 10 lần/giây (PX4 chỉ thoát offboard khi im lặng quá khoảng 0,5 giây).
CHU_KY_GUI = 0.1  # giây
TAN_SO_TELEMETRY = 10.0  # lần/giây, xin PX4 báo vị trí nhanh hơn mặc định
TOI_DA_TUOI_TELEMETRY = 2.0  # giây; dữ liệu vị trí cũ hơn mức này thì cho drone đứng yên
CUA_SO_RTF = 2.0  # giây; ước lượng RTF theo từng khoảng thời gian này (RTF thay đổi liên tục)

# Bộ điều khiển
KP = 0.5  # đơn vị 1/giây: mỗi 1 m sai số thì lệnh bao nhiêu m/s
DUNG_FEEDFORWARD = False  # True: cộng sẵn vận tốc mục tiêu vào lệnh (docs/05 mục 7.3)
VAN_TOC_TOI_DA = 3.0  # m/s, giới hạn độ lớn vận tốc lệnh (docs/05 mục 6)
KHOANG_CACH_GIU = 5.0  # mét, khoảng cách NGANG muốn giữ với mục tiêu

# Mục tiêu ảo (đường thẳng, vận tốc không đổi)
KHOANG_CACH_DAU = 10.0  # mét, lúc đầu mục tiêu cách drone bao xa (theo HUONG_MUC_TIEU)
HUONG_MUC_TIEU = 0.0  # độ la bàn: 0 = Bắc, 90 = Đông
TOC_DO_MUC_TIEU = 1.0  # m/s

HIEN_THI_GAZEBO = True  # True: vẽ mục tiêu ảo thành quả cầu đỏ trong Gazebo (chỉ để quan sát)

SO_GIAY_THI_NGHIEM = 30  # giây
CHU_KY_IN = 0.5  # giây, cứ bao lâu thì in sai số một lần


# ---------------------------------------------------------------------------
# Phần tính toán thuần túy (không cần drone, có thể kiểm tra riêng)
# ---------------------------------------------------------------------------
def tinh_muc_tieu(goc_bac, goc_dong, t):
    """
    Mục tiêu ảo đi thẳng đều. Công thức: vị_trí = vị_trí_đầu + vận_tốc × t.
    goc_bac, goc_dong: vị trí drone lúc bắt đầu (mục tiêu xuất phát cách đó KHOANG_CACH_DAU).
    Trả về ((bắc, đông), (v_bắc, v_đông)) tại thời điểm t (giây).
    """
    huong = math.radians(HUONG_MUC_TIEU)
    don_vi_bac = math.cos(huong)
    don_vi_dong = math.sin(huong)
    quang_duong = KHOANG_CACH_DAU + TOC_DO_MUC_TIEU * t
    vi_tri = (goc_bac + quang_duong * don_vi_bac, goc_dong + quang_duong * don_vi_dong)
    van_toc = (TOC_DO_MUC_TIEU * don_vi_bac, TOC_DO_MUC_TIEU * don_vi_dong)
    return vi_tri, van_toc


def tinh_van_toc_lenh(vi_tri_drone, vi_tri_muc_tieu, van_toc_muc_tieu, kp, dung_feedforward):
    """
    Bộ điều khiển P 2 chiều (docs/05 mục 9.5).
    Trả về (v_bắc, v_đông, sai_số, khoảng_cách_ngang).
    """
    d_bac = vi_tri_muc_tieu[0] - vi_tri_drone[0]
    d_dong = vi_tri_muc_tieu[1] - vi_tri_drone[1]
    khoang_cach = math.hypot(d_bac, d_dong)  # Pytago: √(Δbắc² + Δđông²)
    sai_so = khoang_cach - KHOANG_CACH_GIU  # dương = xa hơn mức muốn giữ

    # Hướng từ drone tới mục tiêu (độ dài bằng 1); tránh chia cho 0 khi trùng nhau
    if khoang_cach > 1e-6:
        huong_bac, huong_dong = d_bac / khoang_cach, d_dong / khoang_cach
    else:
        huong_bac, huong_dong = 0.0, 0.0

    toc_do_p = kp * sai_so
    v_bac = toc_do_p * huong_bac
    v_dong = toc_do_p * huong_dong
    if dung_feedforward:
        v_bac += van_toc_muc_tieu[0]
        v_dong += van_toc_muc_tieu[1]

    # Giới hạn độ lớn vận tốc, giữ nguyên hướng
    toc_do = math.hypot(v_bac, v_dong)
    if toc_do > VAN_TOC_TOI_DA:
        he_so = VAN_TOC_TOI_DA / toc_do
        v_bac *= he_so
        v_dong *= he_so
    return v_bac, v_dong, sai_so, khoang_cach


def trung_binh(danh_sach):
    return sum(danh_sach) / len(danh_sach) if danh_sach else float("nan")


# ---------------------------------------------------------------------------
# Đọc dữ liệu từ drone
# ---------------------------------------------------------------------------
async def doc_huong_mui(drone):
    """Trả về yaw (hướng mũi) bằng độ, 0 = Bắc, 90 = Đông."""
    async for h in drone.telemetry.heading():
        return h.heading_deg


async def cap_nhat_telemetry(drone, tt):
    """Chạy nền: liên tục ghi vị trí và vận tốc mới nhất của drone vào từ điển tt."""
    async for pv in drone.telemetry.position_velocity_ned():
        tt["bac"] = pv.position.north_m
        tt["dong"] = pv.position.east_m
        tt["xuong"] = pv.position.down_m  # D dương là xuống, bay lên là D âm
        tt["v_bac"] = pv.velocity.north_m_s
        tt["v_dong"] = pv.velocity.east_m_s
        tt["luc_nhan"] = time.monotonic()
        tt["so_lan"] += 1


# ---------------------------------------------------------------------------
# Kết nối, cất cánh, vào/thoát offboard (giống bài 3)
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
        async for vt in drone.telemetry.position():
            do_cao = vt.relative_altitude_m
            break
        print(f"   Độ cao: {do_cao:5.1f} m")
        if do_cao >= DO_CAO_CAT_CANH * 0.9:
            break
        await asyncio.sleep(1)

    print("   -> Đang lơ lửng, chờ 3 giây cho ổn định...")
    await asyncio.sleep(3)


async def gui_dung_yen(drone, yaw, so_giay):
    """Gửi lệnh 'đứng yên' liên tục trong so_giay giây (giữ nguyên hướng mũi yaw)."""
    for _ in range(int(so_giay / CHU_KY_GUI)):
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw))
        await asyncio.sleep(CHU_KY_GUI)


async def vao_offboard(drone, yaw):
    """Luật 1: gửi lệnh 'đứng yên' trước. Luật 2: rồi mới bật offboard."""
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw))
    try:
        await drone.offboard.start()
    except OffboardError as loi:
        print(f"   !!! Không vào được offboard: {loi}")
        raise SystemExit(1)
    print("   -> Đã vào offboard mode (script đang cầm lái)")


async def thoat_offboard(drone, yaw):
    """Gửi 'đứng yên' 2 giây cho drone dừng hẳn, rồi trả lái lại cho PX4."""
    await gui_dung_yen(drone, yaw, 2)
    try:
        await drone.offboard.stop()
    except OffboardError as loi:
        print(f"   !!! Lỗi khi thoát offboard: {loi}")
    print("   -> Đã thoát offboard (PX4 lái lại)")


# ---------------------------------------------------------------------------
# Vòng điều khiển
# ---------------------------------------------------------------------------
async def vong_dieu_khien(drone, tt, yaw, goc_bac, goc_dong, kp, dung_ff, hien_thi=None):
    """Chạy SO_GIAY_THI_NGHIEM giây. Trả về danh sách mẫu đo (mỗi mẫu là một từ điển)."""
    mau = []
    t0 = time.monotonic()
    lan_in_cuoi = -CHU_KY_IN
    cua_so = deque()  # các cặp (thời điểm, số lần telemetry đã nhận) trong CUA_SO_RTF giây gần nhất
    while True:
        t = time.monotonic() - t0
        if t >= SO_GIAY_THI_NGHIEM:
            break

        # RTF trong cửa sổ gần nhất: số lần telemetry nhận được mỗi giây THẬT / số lần đặt mỗi giây SIM
        cua_so.append((t, tt["so_lan"]))
        while t - cua_so[0][0] > CUA_SO_RTF:
            cua_so.popleft()
        rtf_cua_so = float("nan")
        if t - cua_so[0][0] >= 0.5:
            rtf_cua_so = (tt["so_lan"] - cua_so[0][1]) / (t - cua_so[0][0]) / TAN_SO_TELEMETRY

        vi_tri_mt, van_toc_mt = tinh_muc_tieu(goc_bac, goc_dong, t)
        if hien_thi is not None:
            hien_thi.dat_vi_tri(vi_tri_mt[0], vi_tri_mt[1])  # chỉ ghi nhớ, không chờ gì cả
        tuoi =time.monotonic() - tt["luc_nhan"]  # dữ liệu vị trí cũ bao nhiêu giây
        if tuoi > TOI_DA_TUOI_TELEMETRY:
            # Mất dữ liệu: thà đứng yên còn hơn bay theo số đo cũ
            v_bac, v_dong, sai_so, khoang_cach = 0.0, 0.0, float("nan"), float("nan")
            print(f"   !!! Telemetry cũ {tuoi:.1f} s, cho drone đứng yên")
        else:
            v_bac, v_dong, sai_so, khoang_cach = tinh_van_toc_lenh(
                (tt["bac"], tt["dong"]), vi_tri_mt, van_toc_mt, kp, dung_ff
            )

        # Luật 2: gửi liên tục. Vận tốc xuống = 0 để PX4 giữ độ cao hiện tại.
        await drone.offboard.set_velocity_ned(VelocityNedYaw(v_bac, v_dong, 0.0, yaw))

        toc_do_lenh = math.hypot(v_bac, v_dong)
        toc_do_thuc = math.hypot(tt["v_bac"], tt["v_dong"])
        do_cao = -tt["xuong"]
        mau.append({"t": t, "sai_so": sai_so, "khoang_cach": khoang_cach,
                    "toc_do_lenh": toc_do_lenh, "toc_do_thuc": toc_do_thuc, "do_cao": do_cao,
                    "rtf": rtf_cua_so})

        if t - lan_in_cuoi >= CHU_KY_IN:
            lan_in_cuoi = t
            print(f"   t={t:5.1f}s  khoảng cách {khoang_cach:6.2f} m  sai số {sai_so:+6.2f} m  "
                  f"lệnh {toc_do_lenh:4.2f} m/s  thực {toc_do_thuc:4.2f} m/s  cao {do_cao:5.1f} m  "
                  f"RTF~{rtf_cua_so:4.2f}")

        await asyncio.sleep(CHU_KY_GUI)
    return mau


def in_ket_qua(mau, kp, dung_ff, so_lan_telemetry, tong_giay):
    sai_so = [m["sai_so"] for m in mau if not math.isnan(m["sai_so"])]
    nua_sau = [m for m in mau if m["t"] >= SO_GIAY_THI_NGHIEM / 2 and not math.isnan(m["sai_so"])]
    sai_so_nua_sau = [m["sai_so"] for m in nua_sau]

    # Kỳ vọng theo mô hình lý tưởng (docs/05 mục 7.2 và 8): drone đạt đúng vận tốc lệnh,
    # số đo luôn mới nhất, không có độ trễ.
    if dung_ff:
        sai_so_ky_vong = 0.0
    else:
        sai_so_ky_vong = TOC_DO_MUC_TIEU / kp

    print("\n--- KẾT QUẢ ---")
    print(f"Cấu hình: Kp = {kp}, {'P + feedforward' if dung_ff else 'P thuần'}, "
          f"giữ {KHOANG_CACH_GIU} m, mục tiêu đi {TOC_DO_MUC_TIEU} m/s")
    print(f"Sai số trung bình (giá trị tuyệt đối, cả bài):   {trung_binh([abs(x) for x in sai_so]):.2f} m")
    print(f"Sai số trung bình (nửa sau, khi đã ổn định):     {trung_binh(sai_so_nua_sau):+.2f} m")
    print(f"Sai số cuối bài:                                 {sai_so[-1]:+.2f} m")
    print(f"Khoảng cách cuối bài:                            {mau[-1]['khoang_cach']:.2f} m")
    print(f"Tốc độ lệnh trung bình (nửa sau):                {trung_binh([m['toc_do_lenh'] for m in nua_sau]):.2f} m/s")
    print(f"Tốc độ thực trung bình (nửa sau, từ telemetry):  {trung_binh([m['toc_do_thuc'] for m in nua_sau]):.2f} m/s")
    print(f"Độ cao trung bình / nhỏ nhất / lớn nhất:         "
          f"{trung_binh([m['do_cao'] for m in mau]):.1f} / {min(m['do_cao'] for m in mau):.1f} / "
          f"{max(m['do_cao'] for m in mau):.1f} m")
    tan_so_telemetry = so_lan_telemetry / tong_giay
    # PX4 gửi TAN_SO_TELEMETRY lần/giây THEO THỜI GIAN SIM, còn ta đếm theo thời gian THẬT,
    # nên tần số đo được / tần số đặt = RTF (chỉ đúng khi đặt được tần số telemetry).
    rtf = tan_so_telemetry / TAN_SO_TELEMETRY
    print(f"Tần số telemetry đo được:                        {tan_so_telemetry:.1f} lần/giây")
    print(f"RTF ước lượng (tần số đo được / tần số đặt):     {rtf:.2f}")
    rtf_cac_cua_so = [m["rtf"] for m in mau if not math.isnan(m.get("rtf", float("nan")))]
    if rtf_cac_cua_so:
        print(f"RTF theo từng cửa sổ {CUA_SO_RTF:.0f} s (nhỏ nhất / lớn nhất):      "
              f"{min(rtf_cac_cua_so):.2f} / {max(rtf_cac_cua_so):.2f}")

    # Kỳ vọng khi có RTF = r: mục tiêu đi theo đồng hồ thật, drone bay theo thời gian sim.
    #   P thuần:      sai_số = v / (Kp × r)
    #   P + feedforward: sai_số = v × (1/r - 1) / Kp
    if dung_ff:
        sai_so_theo_rtf = TOC_DO_MUC_TIEU * (1 / rtf - 1) / kp
    else:
        sai_so_theo_rtf = TOC_DO_MUC_TIEU / (kp * rtf)

    print("\nSo với kỳ vọng:")
    print(f"  Mô hình lý tưởng (RTF = 1): sai số {sai_so_ky_vong:+.2f} m "
          f"(khoảng cách ~ {KHOANG_CACH_GIU + sai_so_ky_vong:.2f} m), tốc độ thực ~{TOC_DO_MUC_TIEU:.2f} m/s")
    print(f"  Tính theo RTF ước lượng:    sai số {sai_so_theo_rtf:+.2f} m "
          f"(khoảng cách ~ {KHOANG_CACH_GIU + sai_so_theo_rtf:.2f} m), tốc độ thực ~{TOC_DO_MUC_TIEU / rtf:.2f} m/s")
    print("  Gợi ý: nếu số đo gần dòng 'theo RTF ước lượng' hơn dòng 'lý tưởng' thì sim đang chạy chậm hơn thời gian thật.")


async def main():
    kp = KP
    dung_ff = DUNG_FEEDFORWARD
    ve_qua_cau = HIEN_THI_GAZEBO
    cach_dung = "Dùng: python buoc4_p_controller.py [Kp] [p | ff] [khong_cau]"
    if len(sys.argv) > 1:
        kp = float(sys.argv[1])
    if len(sys.argv) > 2:
        if sys.argv[2].lower() not in ("p", "ff"):
            print(cach_dung)
            return
        dung_ff = sys.argv[2].lower() == "ff"
    if len(sys.argv) > 3:
        if sys.argv[3].lower() != "khong_cau":
            print(cach_dung)
            return
        ve_qua_cau = False

    drone = System()
    tt = {"bac": None, "dong": None, "xuong": None, "v_bac": 0.0, "v_dong": 0.0,
          "luc_nhan": 0.0, "so_lan": 0}
    tac_vu = None
    hien_thi = None
    da_cat_canh = False
    try:
        await ket_noi_va_cat_canh(drone)
        da_cat_canh = True

        print("4) Chuẩn bị đọc vị trí liên tục...")
        try:
            await drone.telemetry.set_rate_position_velocity_ned(TAN_SO_TELEMETRY)
        except Exception as loi:  # không bắt buộc, chỉ để telemetry nhanh hơn
            print(f"   (Không đặt được tần số telemetry: {loi})")
        tac_vu = asyncio.create_task(cap_nhat_telemetry(drone, tt))
        while tt["bac"] is None:
            await asyncio.sleep(0.1)
        goc_bac, goc_dong = tt["bac"], tt["dong"]
        yaw = await doc_huong_mui(drone)
        print(f"   -> Vị trí bắt đầu (bắc {goc_bac:.2f}, đông {goc_dong:.2f}) m, hướng mũi {yaw:.1f}° (giữ nguyên)")
        if ve_qua_cau:
            hien_thi = MucTieuGazebo()
            vi_tri_dau, _ = tinh_muc_tieu(goc_bac, goc_dong, 0.0)
            await hien_thi.bat_dau(vi_tri_dau[0], vi_tri_dau[1])

        print("5) Vào offboard...")
        await vao_offboard(drone, yaw)

        print(f"6) Bám mục tiêu ảo đi thẳng {SO_GIAY_THI_NGHIEM} giây "
              f"(Kp = {kp}, {'P + feedforward' if dung_ff else 'P thuần'})...")
        so_lan_dau = tt["so_lan"]
        t_dau = time.monotonic()
        mau = []
        try:
            mau = await vong_dieu_khien(drone, tt, yaw, goc_bac, goc_dong, kp, dung_ff, hien_thi)
        finally:
            await thoat_offboard(drone, yaw)
        tong_giay = time.monotonic() - t_dau
        if mau:
            in_ket_qua(mau, kp, dung_ff, tt["so_lan"] - so_lan_dau, tong_giay)
            if hien_thi is not None and hien_thi.hoat_dong:
                print(f"Cập nhật quả cầu trong Gazebo:                   {hien_thi.tan_so_cap_nhat():.1f} lần/giây")
    finally:
        if tac_vu is not None:
            tac_vu.cancel()
        if hien_thi is not None:
            await hien_thi.ket_thuc()  # xóa quả cầu khỏi Gazebo
        if da_cat_canh:
            print("\n7) Hạ cánh...")
            await drone.action.land()
            async for dang_bay in drone.telemetry.in_air():
                if not dang_bay:
                    print("   -> Đã đáp đất. Xong thí nghiệm!")
                    break


if __name__ == "__main__":
    asyncio.run(main())
