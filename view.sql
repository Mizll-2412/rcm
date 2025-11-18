CREATE VIEW vw_SuKien_FullInfo AS
SELECT
    sk.MaSuKien,
    sk.TenSuKien,
    sk.NoiDung,
    sk.SoLuong,
    sk.DiaChi,
    sk.NgayBatDau,
    sk.NgayKetThuc,
    sk.NgayTao,
    sk.NgayTuyen,
    sk.NgayKetThucTuyen,
    sk.TrangThai,
    sk.TrangThaiTuyen,
    sk.NgayDienRaBatDau,
    sk.NgayDienRaKetThuc,
    sk.ThoiGianKhoaHuy,
    sk.HinhAnh,
    tc.MaToChuc,
    tc.TenToChuc,
    tc.Email AS EmailToChuc,
    tc.SoDienThoai,
    tc.DiaChi AS DiaChiToChuc,
    -- Lĩnh vực của sự kiện (dùng STRING_AGG để gom nhiều lĩnh vực)
    LV.LinhVucList,
    -- Kỹ năng của sự kiện
    KN.KyNangList
FROM SuKien sk
INNER JOIN ToChuc tc ON sk.MaToChuc = tc.MaToChuc
-- Lấy danh sách lĩnh vực
LEFT JOIN (
    SELECT 
        sklv.MaSuKien,
        STRING_AGG(lv.TenLinhVuc, ', ') AS LinhVucList
    FROM SuKien_LinhVuc sklv
    INNER JOIN LinhVuc lv ON sklv.MaLinhVuc = lv.MaLinhVuc
    GROUP BY sklv.MaSuKien
) LV ON sk.MaSuKien = LV.MaSuKien
-- Lấy danh sách kỹ năng
LEFT JOIN (
    SELECT 
        skkn.MaSuKien,
        STRING_AGG(kn.TenKyNang, ', ') AS KyNangList
    FROM SuKien_KyNang skkn
    INNER JOIN KyNang kn ON skkn.MaKyNang = kn.MaKyNang
    GROUP BY skkn.MaSuKien
) KN ON sk.MaSuKien = KN.MaSuKien;
CREATE VIEW vw_TinhNguyenVien_FullInfo AS
SELECT
    tnv.MaTNV,
    tnv.HoTen,
    tnv.NgaySinh,
    tnv.GioiTinh,
    tnv.Email,
    tnv.CCCD,
    tnv.SoDienThoai,
    tnv.DiaChi,
    tnv.GioiThieu,
    tnv.AnhDaiDien,
    tnv.DiemTrungBinh,
    tnv.CapBac,
    tnv.TongSuKienThamGia,
    tk.MaTaiKhoan,
    tk.VaiTro,
    tk.TrangThai AS TrangThaiTaiKhoan,
    -- Lĩnh vực TNV
    LV.LinhVucList,
    -- Kỹ năng TNV
    KN.KyNangList
FROM TinhNguyenVien tnv
INNER JOIN TaiKhoan tk ON tnv.MaTaiKhoan = tk.MaTaiKhoan
-- Lấy danh sách lĩnh vực
LEFT JOIN (
    SELECT 
        tnv_lv.MaTNV,
        STRING_AGG(lv.TenLinhVuc, ', ') AS LinhVucList
    FROM TinhNguyenVien_LinhVuc tnv_lv
    INNER JOIN LinhVuc lv ON tnv_lv.MaLinhVuc = lv.MaLinhVuc
    GROUP BY tnv_lv.MaTNV
) LV ON tnv.MaTNV = LV.MaTNV
-- Lấy danh sách kỹ năng
LEFT JOIN (
    SELECT 
        tnv_kn.MaTNV,
        STRING_AGG(kn.TenKyNang, ', ') AS KyNangList
    FROM TinhNguyenVien_KyNang tnv_kn
    INNER JOIN KyNang kn ON tnv_kn.MaKyNang = kn.MaKyNang
    GROUP BY tnv_kn.MaTNV
) KN ON tnv.MaTNV = KN.MaTNV;
