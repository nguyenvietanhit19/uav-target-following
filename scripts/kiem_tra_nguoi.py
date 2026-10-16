r"""
Kiểm chứng CÔNG THỨC vị trí người đi bộ: vẽ một quả cầu đỏ LƠ LỬNG TRÊN ĐẦU vị trí mà công thức
(duong_di_nguoi.py + đồng hồ sim) dự đoán. Nếu công thức đúng thì quả cầu luôn nằm ngay trên
đầu người đi bộ và đi cùng người.

Cách chạy (PowerShell, tại thư mục gốc của repo, khi sim có người đang chạy):
    .\.venv\Scripts\python.exe scripts\kiem_tra_nguoi.py              # chạy 60 giây
    .\.venv\Scripts\python.exe scripts\kiem_tra_nguoi.py 120          # chạy 120 giây
    .\.venv\Scripts\python.exe scripts\kiem_tra_nguoi.py 120 -13      # kèm độ lệch thời gian -13 giây
Độ lệch thời gian (giây): cộng vào thời gian sim trước khi tính vị trí. Người đi 1 m/s nên
    nếu quả cầu nằm TRƯỚC người (theo hướng đi) khoảng D mét thì thử độ lệch âm (-D);
    nếu quả cầu nằm SAU người khoảng D mét thì thử độ lệch dương (+D).
Dừng sớm: bấm Ctrl+C (quả cầu được xóa khi kết thúc).

Điều kiện cần: sim chạy bằng chay_gpu_nguoi.sh với ĐÚNG file world hiện tại trong sim/
(nếu sửa default_nguoi.sdf thì chép lại sang ~/phao và khởi động lại sim).
Không cần PX4/MAVSDK, không làm drone bay.
"""

import asyncio
import sys
import time

import hien_thi_gazebo
from dong_ho_gazebo import DongHoGazebo
from duong_di_nguoi import DuongDiNguoi

SO_GIAY_MAC_DINH = 60
DO_CAO_QUA_CAU = 2.4  # mét; cao hơn đầu người (khoảng 1,8 m) để quả cầu không bị người che
CHU_KY_IN = 2.0  # giây thật


async def main():
    so_giay = float(sys.argv[1]) if len(sys.argv) > 1 else SO_GIAY_MAC_DINH
    do_lech = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0  # giây, cộng vào thời gian sim

    print("1) Đọc đường đi của người từ sim/default_nguoi.sdf...")
    duong_di = DuongDiNguoi.tu_file_sdf()
    print(f"   -> {len(duong_di.cac_moc)} điểm mốc, bắt đầu đi sau {duong_di.tre_bat_dau:.1f} giây sim, "
          f"{'lặp lại' if duong_di.lap else 'không lặp'}")

    print("2) Kết nối đồng hồ sim của Gazebo...")
    dong_ho = DongHoGazebo()
    await dong_ho.bat_dau()
    print(f"   -> Sim đang ở giây {dong_ho.thoi_gian_sim():.1f}, RTF {dong_ho.rtf():.2f}")
    if do_lech != 0.0:
        print(f"   -> Đang dùng độ lệch thời gian {do_lech:+.1f} giây (người đi 1 m/s nên tương đương {do_lech:+.1f} m)")

    print("3) Tạo quả cầu đỏ trên đầu vị trí dự đoán...")
    hien_thi_gazebo.DO_CAO_TAM_VAT = DO_CAO_QUA_CAU
    qua_cau = hien_thi_gazebo.MucTieuGazebo()
    (bac, dong), _ = duong_di.vi_tri_van_toc_ned(dong_ho.thoi_gian_sim() + do_lech)
    await qua_cau.bat_dau(bac, dong)
    if not qua_cau.hoat_dong:
        await dong_ho.ket_thuc()
        return

    print(f"4) Quả cầu đỏ phải nằm ngay trên đầu người và đi cùng người ({so_giay:.0f} giây). "
          "Bấm Ctrl+C để dừng sớm.")
    try:
        t_dau = time.monotonic()
        lan_in_cuoi = -CHU_KY_IN
        while time.monotonic() - t_dau < so_giay:
            t_sim = dong_ho.thoi_gian_sim()
            (bac, dong), (v_bac, v_dong) = duong_di.vi_tri_van_toc_ned(t_sim + do_lech)
            qua_cau.dat_vi_tri(bac, dong)
            t = time.monotonic() - t_dau
            if t - lan_in_cuoi >= CHU_KY_IN:
                lan_in_cuoi = t
                print(f"   sim {t_sim:7.1f} s | RTF {dong_ho.rtf():.2f} | dự đoán người ở "
                      f"(bắc {bac:6.1f} m, đông {dong:5.1f} m), đang đi {v_bac:+.2f} m/s về bắc")
            await asyncio.sleep(0.1)
    finally:
        await qua_cau.ket_thuc()
        await dong_ho.ket_thuc()
        print("5) Đã xóa quả cầu. Xong.")
        print(f"   Cập nhật quả cầu đạt khoảng {qua_cau.tan_so_cap_nhat():.1f} lần/giây.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
