"""
Hiển thị MỤC TIÊU ẢO trong Gazebo: tạo một quả cầu đỏ rồi di chuyển nó theo mục tiêu ảo.

Làm gì:
    Mục tiêu ảo chỉ là con số trong code nên không thấy được trong Gazebo. Module này gọi
    các dịch vụ của Gazebo (create, set_pose, remove) qua `docker exec` để vẽ nó thành một
    quả cầu đỏ. Chỉ để QUAN SÁT: lỗi ở đây không làm ảnh hưởng việc điều khiển bay.

Chạy trên đâu / điều kiện cần:
    - Chạy trên Windows, cần lệnh `docker` dùng được và container sim (TEN_CONTAINER) đang chạy.
    - Không chạy riêng, được `buoc4_p_controller.py` gọi.

Tọa độ: PX4 dùng NED (bắc, đông, xuống) so với điểm Home; Gazebo dùng ENU (x = đông,
y = bắc, z = lên). Vì vậy x = đông, y = bắc. Nếu drone không xuất phát đúng gốc (0, 0)
của world Gazebo thì chỉnh GOC_GAZEBO_BAC / GOC_GAZEBO_DONG.
"""

import asyncio
import time

TEN_CONTAINER = "px4-gazebo"  # theo --name trong ~/phao/chay_gpu.sh
TEN_WORLD = "default"  # theo dịch vụ /world/default/set_pose đã kiểm tra
TEN_VAT = "muc_tieu"
BAN_KINH_VAT = 0.5  # mét
DO_CAO_TAM_VAT = 0.5  # mét, độ cao tâm quả cầu so với mặt đất (bằng bán kính thì cầu nằm trên đất)
TIMEOUT_MS = 3000

# Vị trí điểm Home (nơi drone xuất phát) trong world Gazebo, tính bằng mét
GOC_GAZEBO_BAC = 0.0  # trục y của Gazebo
GOC_GAZEBO_DONG = 0.0  # trục x của Gazebo


def _tham_so_vi_tri(bac, dong):
    x = GOC_GAZEBO_DONG + dong
    y = GOC_GAZEBO_BAC + bac
    return x, y


def lenh_tao(bac, dong):
    """Lệnh bash tạo quả cầu đỏ (không trọng lực, không va chạm) tại vị trí (bắc, đông)."""
    x, y = _tham_so_vi_tri(bac, dong)
    sdf = (
        '<sdf version=\\"1.8\\"><model name=\\"' + TEN_VAT + '\\"><link name=\\"link\\">'
        '<gravity>false</gravity><visual name=\\"visual\\"><geometry><sphere><radius>'
        + str(BAN_KINH_VAT) +
        '</radius></sphere></geometry><material><ambient>1 0 0 1</ambient>'
        '<diffuse>1 0 0 1</diffuse></material></visual></link></model></sdf>'
    )
    pose = "pose: {position: {x: %.3f, y: %.3f, z: %.3f}}" % (x, y, DO_CAO_TAM_VAT)
    return (
        "gz service -s /world/" + TEN_WORLD + "/create --reqtype gz.msgs.EntityFactory "
        "--reptype gz.msgs.Boolean --timeout " + str(TIMEOUT_MS)
        + " --req 'sdf: \"" + sdf + "\" " + pose + "'"
    )


def lenh_di_chuyen(bac, dong):
    x, y = _tham_so_vi_tri(bac, dong)
    return (
        "gz service -s /world/" + TEN_WORLD + "/set_pose --reqtype gz.msgs.Pose "
        "--reptype gz.msgs.Boolean --timeout " + str(TIMEOUT_MS)
        + " --req 'name: \"" + TEN_VAT + "\" position: {x: %.3f, y: %.3f, z: %.3f}'"
        % (x, y, DO_CAO_TAM_VAT)
    )


def lenh_xoa():
    return (
        "gz service -s /world/" + TEN_WORLD + "/remove --reqtype gz.msgs.Entity "
        "--reptype gz.msgs.Boolean --timeout " + str(TIMEOUT_MS)
        + " --req 'name: \"" + TEN_VAT + "\" type: MODEL'"
    )


class MucTieuGazebo:
    """Quả cầu đỏ trong Gazebo. Mọi lỗi chỉ in cảnh báo rồi tự tắt, không ném lỗi ra ngoài."""

    def __init__(self):
        self.tien_trinh = None
        self.hoat_dong = False
        self.vi_tri_moi = None  # (bắc, đông) mới nhất cần hiển thị
        self.vi_tri_da_gui = None
        self.tac_vu = None
        self.so_lan_cap_nhat = 0
        self.t_bat_dau = None

    async def _chay_lenh(self, lenh):
        """Gửi một lệnh vào phiên bash trong container, chờ xong, trả về dòng kết quả."""
        self.tien_trinh.stdin.write((lenh + " 2>&1; echo XONG\n").encode())
        await self.tien_trinh.stdin.drain()
        ket_qua = []
        while True:
            dong = await asyncio.wait_for(self.tien_trinh.stdout.readline(), timeout=10)
            if not dong:
                raise RuntimeError("phiên docker đã đóng")
            chu = dong.decode(errors="replace").strip()
            if chu == "XONG":
                return " ".join(ket_qua)
            if chu:
                ket_qua.append(chu)

    async def bat_dau(self, bac, dong):
        """Mở phiên bash trong container và tạo quả cầu. Lỗi thì tắt tính năng này."""
        try:
            self.tien_trinh = await asyncio.create_subprocess_exec(
                "docker", "exec", "-i", TEN_CONTAINER, "bash",
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            ket_qua = await self._chay_lenh(lenh_tao(bac, dong))
            if "true" not in ket_qua:
                raise RuntimeError("tạo vật thất bại: " + ket_qua)
        except Exception as loi:
            print(f"   (Không hiển thị được mục tiêu trong Gazebo: {loi})")
            await self._dong()
            return
        self.hoat_dong = True
        self.vi_tri_da_gui = (bac, dong)
        self.vi_tri_moi = (bac, dong)
        self.t_bat_dau = time.monotonic()
        self.tac_vu = asyncio.create_task(self._vong_cap_nhat())
        print("   -> Đã tạo quả cầu đỏ (mục tiêu ảo) trong Gazebo")

    def dat_vi_tri(self, bac, dong):
        """Gọi mỗi chu kỳ điều khiển: chỉ ghi nhớ vị trí mới nhất, KHÔNG chờ gì cả."""
        self.vi_tri_moi = (bac, dong)

    async def _vong_cap_nhat(self):
        """Chạy nền: luôn gửi vị trí mới nhất, xong lệnh trước mới gửi lệnh sau (không bị dồn lệnh)."""
        try:
            while True:
                if self.vi_tri_moi == self.vi_tri_da_gui:
                    await asyncio.sleep(0.02)
                    continue
                bac, dong = self.vi_tri_moi
                self.vi_tri_da_gui = self.vi_tri_moi
                await self._chay_lenh(lenh_di_chuyen(bac, dong))
                self.so_lan_cap_nhat += 1
        except asyncio.CancelledError:
            raise
        except Exception as loi:
            print(f"   (Ngừng hiển thị mục tiêu trong Gazebo: {loi})")
            self.hoat_dong = False

    def tan_so_cap_nhat(self):
        if not self.t_bat_dau:
            return 0.0
        return self.so_lan_cap_nhat / max(time.monotonic() - self.t_bat_dau, 1e-6)

    async def _dong(self):
        if self.tien_trinh is not None:
            try:
                self.tien_trinh.stdin.close()
                await asyncio.wait_for(self.tien_trinh.wait(), timeout=5)
            except Exception:
                try:
                    self.tien_trinh.kill()
                except Exception:
                    pass
            self.tien_trinh = None

    async def ket_thuc(self):
        """Dừng cập nhật, xóa quả cầu khỏi Gazebo, đóng phiên docker."""
        if self.tac_vu is not None:
            self.tac_vu.cancel()
            try:
                await self.tac_vu
            except BaseException:
                pass
            self.tac_vu = None
        if self.tien_trinh is not None and self.hoat_dong:
            try:
                await self._chay_lenh(lenh_xoa())
                print("   -> Đã xóa quả cầu khỏi Gazebo")
            except Exception as loi:
                print(f"   (Không xóa được quả cầu: {loi})")
        self.hoat_dong = False
        await self._dong()
