"""
Tính VỊ TRÍ và VẬN TỐC của người đi bộ (actor) trong Gazebo từ thời gian sim.

Làm gì:
    Gazebo không công bố vị trí của actor (đã thử: pose/info, dynamic_pose/info, gz model đều
    không có). Nhưng đường đi của actor được định nghĩa cố định trong file world
    sim/default_nguoi.sdf (các điểm mốc theo thời gian sim), nên ta ĐỌC CHÍNH FILE ĐÓ rồi
    tính vị trí tại thời điểm sim bất kỳ. Nhờ vậy chỉ có một nơi định nghĩa đường đi.

Giả định (CHƯA kiểm chứng hết, dùng kiem_tra_nguoi.py để đối chiếu bằng mắt):
    - Trước delay_start người đứng ở điểm mốc đầu.
    - Giữa hai điểm mốc người đi thẳng đều (nội suy tuyến tính).
    - Sau điểm mốc cuối: nếu loop false thì dừng ở đó; nếu loop true thì quay lại điểm đầu.

Tọa độ: Gazebo là ENU (x = đông, y = bắc). PX4 là NED so với điểm Home (bắc, đông, xuống).
    Home nằm ở (GOC_GAZEBO_BAC, GOC_GAZEBO_DONG) trong world (lấy từ hien_thi_gazebo.py).
"""

import os
import xml.etree.ElementTree as ET

import hien_thi_gazebo

DUONG_DAN_SDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sim", "default_nguoi.sdf")
TEN_ACTOR = "muc_tieu_nguoi"


class DuongDiNguoi:
    def __init__(self, cac_moc, tre_bat_dau, lap):
        """cac_moc: danh sách (thời_gian, x, y) theo thứ tự thời gian tăng dần."""
        self.cac_moc = cac_moc
        self.tre_bat_dau = tre_bat_dau
        self.lap = lap

    @classmethod
    def tu_file_sdf(cls, duong_dan=DUONG_DAN_SDF, ten_actor=TEN_ACTOR):
        goc = ET.parse(duong_dan).getroot()
        actor = next(a for a in goc.iter("actor") if a.get("name") == ten_actor)
        script = actor.find("script")
        tre = float(script.findtext("delay_start", default="0"))
        lap = script.findtext("loop", default="true").strip().lower() == "true"
        cac_moc = []
        for moc in script.find("trajectory").findall("waypoint"):
            t = float(moc.findtext("time"))
            x, y = [float(v) for v in moc.findtext("pose").split()[:2]]
            cac_moc.append((t, x, y))
        if len(cac_moc) < 2:
            raise ValueError("đường đi cần ít nhất 2 điểm mốc")
        return cls(cac_moc, tre, lap)

    def vi_tri_van_toc_gazebo(self, t_sim):
        """Trả về ((x, y), (vx, vy)) trong toạ độ Gazebo (ENU) tại thời điểm sim t_sim (giây)."""
        t = t_sim - self.tre_bat_dau
        t_cuoi = self.cac_moc[-1][0]
        dau = self.cac_moc[0]
        cuoi = self.cac_moc[-1]
        if t <= self.cac_moc[0][0]:
            return (dau[1], dau[2]), (0.0, 0.0)  # chưa bắt đầu đi
        if t >= t_cuoi:
            if not self.lap:
                return (cuoi[1], cuoi[2]), (0.0, 0.0)  # đã đi hết đường, đứng lại
            t = t % t_cuoi
        for (t1, x1, y1), (t2, x2, y2) in zip(self.cac_moc, self.cac_moc[1:]):
            if t1 <= t <= t2:
                he_so = (t - t1) / (t2 - t1)
                vi_tri = (x1 + (x2 - x1) * he_so, y1 + (y2 - y1) * he_so)
                van_toc = ((x2 - x1) / (t2 - t1), (y2 - y1) / (t2 - t1))
                return vi_tri, van_toc
        return (cuoi[1], cuoi[2]), (0.0, 0.0)

    def vi_tri_van_toc_ned(self, t_sim):
        """Trả về ((bắc, đông), (v_bắc, v_đông)) so với điểm Home, tại thời điểm sim t_sim."""
        (x, y), (vx, vy) = self.vi_tri_van_toc_gazebo(t_sim)
        bac = y - hien_thi_gazebo.GOC_GAZEBO_BAC
        dong = x - hien_thi_gazebo.GOC_GAZEBO_DONG
        return (bac, dong), (vy, vx)
