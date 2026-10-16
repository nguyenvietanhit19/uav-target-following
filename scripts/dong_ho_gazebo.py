"""
Đọc ĐỒNG HỒ SIM của Gazebo (thời gian trôi trong mô phỏng) và RTF.

Làm gì:
    Gazebo công bố khoảng 10 lần/giây một tin ở topic /world/<world>/stats, gồm sim_time
    (giây sim đã trôi), real_time_factor (RTF) và trạng thái tạm dừng. Module này đọc tin đó
    qua `docker exec`, rồi nội suy giữa hai tin để cho ra thời gian sim "ngay lúc này".

Chạy trên đâu / điều kiện cần:
    - Chạy trên Windows, cần lệnh `docker` dùng được và container sim đang chạy.
    - Không chạy riêng, được các script khác gọi (kiem_tra_nguoi.py, buoc4_p_controller.py).

Vì sao cần: người đi bộ (actor) trong Gazebo đi theo đồng hồ SIM, nên muốn biết người đang ở
đâu thì phải biết thời gian sim, không dùng đồng hồ thật của máy.
"""

import asyncio
import time

TEN_CONTAINER = "px4-gazebo"  # theo --name trong chay_gpu_nguoi.sh
TEN_WORLD = "default"
TOI_DA_NOI_SUY = 1.0  # giây thật; tin cũ hơn mức này thì không nội suy thêm


class DongHoGazebo:
    def __init__(self):
        self.tien_trinh = None
        self.tac_vu = None
        self.sim_cuoi = None  # giây sim trong tin mới nhất
        self.luc_nhan = None  # time.monotonic() lúc nhận tin đó
        self.rtf_cuoi = 1.0
        self.tam_dung = False
        self.so_tin = 0

    async def bat_dau(self, cho_toi_da=15):
        """Mở luồng đọc. Có lỗi nếu quá cho_toi_da giây mà chưa nhận được tin nào."""
        # Lệnh trong container: chạy gz topic ở nền, rồi chờ stdin đóng (cat) để tự dọn dẹp,
        # nhờ vậy script Python dừng đột ngột cũng không để lại tiến trình thừa trong container.
        lenh = ("gz topic -e -t /world/" + TEN_WORLD + "/stats & P=$!; cat > /dev/null; kill $P")
        self.tien_trinh = await asyncio.create_subprocess_exec(
            "docker", "exec", "-i", TEN_CONTAINER, "bash", "-c", lenh,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        self.tac_vu = asyncio.create_task(self._doc())
        bat_dau = time.monotonic()
        while self.sim_cuoi is None:
            if time.monotonic() - bat_dau > cho_toi_da:
                await self.ket_thuc()
                raise RuntimeError("không đọc được đồng hồ sim (sim có đang chạy không?)")
            await asyncio.sleep(0.05)

    async def _doc(self):
        """Chạy nền: đọc từng dòng của tin stats và ghi lại sim_time, RTF, trạng thái tạm dừng."""
        dang_o = None
        giay = 0
        nano = 0
        tam_dung = False
        while True:
            dong = await self.tien_trinh.stdout.readline()
            if not dong:
                break
            s = dong.decode(errors="replace").strip()
            if s.startswith("sim_time"):
                dang_o = "sim"
                giay = 0
                nano = 0
                tam_dung = False
            elif s.startswith("real_time {"):
                dang_o = "that"
            elif s.startswith("step_size"):
                dang_o = "khac"
            elif s.startswith("sec:") and dang_o == "sim":
                giay = int(s.split()[1])
            elif s.startswith("nsec:") and dang_o == "sim":
                nano = int(s.split()[1])
            elif s.startswith("paused:"):
                tam_dung = s.split()[1] == "true"
            elif s.startswith("real_time_factor:"):
                # Dòng này nằm sau khối sim_time trong tin, nên coi là hết tin
                self.rtf_cuoi = float(s.split()[1])
                self.sim_cuoi = giay + nano / 1e9
                self.tam_dung = tam_dung
                self.luc_nhan = time.monotonic()
                self.so_tin += 1

    def thoi_gian_sim(self):
        """Giây sim ngay lúc này (nội suy từ tin mới nhất). None nếu chưa có tin nào."""
        if self.sim_cuoi is None:
            return None
        if self.tam_dung:
            return self.sim_cuoi
        troi_qua = min(time.monotonic() - self.luc_nhan, TOI_DA_NOI_SUY)
        return self.sim_cuoi + troi_qua * self.rtf_cuoi

    def rtf(self):
        return self.rtf_cuoi

    async def ket_thuc(self):
        if self.tac_vu is not None:
            self.tac_vu.cancel()
            try:
                await self.tac_vu
            except BaseException:
                pass
            self.tac_vu = None
        if self.tien_trinh is not None:
            try:
                self.tien_trinh.stdin.close()  # container tự dọn tiến trình gz topic
                await asyncio.wait_for(self.tien_trinh.wait(), timeout=5)
            except Exception:
                try:
                    self.tien_trinh.kill()
                except Exception:
                    pass
            self.tien_trinh = None
