"""
pages/about.py — Trang giới thiệu & thông tin ứng dụng.
"""

import streamlit as st
from utils.styles import page_header, divider
from components.sidebar import APP_VERSION


# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────

_FEATURES = [
    ("📋", "Lập Pre-Order",
     "Tạo đơn đặt hàng tự động theo template PO + CI. "
     "Tự động điền dữ liệu, tính giá, deposit và đồng bộ vào Database."),
    ("🗄", "Dữ liệu bảng",
     "Xem, chỉnh sửa trực tiếp các bảng MySQL. "
     "Hỗ trợ INSERT / UPDATE / DELETE, lazy load và xuất Excel."),
    ("⬆", "Import Excel",
     "Nạp hàng loạt dữ liệu từ file .xlsx/.xls vào MySQL. "
     "Mapping cột linh hoạt, hỗ trợ INSERT IGNORE cho dữ liệu trùng."),
    ("⬇", "Export Excel",
     "Xuất 1 bảng, nhiều bảng (multi-sheet) hoặc kết quả SQL tùy chỉnh "
     "ra file Excel với tên file có timestamp tự động."),
    ("📄", "Xem Templates",
     "Xem trước các biểu mẫu Excel (PO, CI) theo từng Vendor "
     "ngay trong trình duyệt — hỗ trợ merged cells, màu sắc, font."),
]

_TECH_STACK = [
    ("Python 3.11+",      "Runtime"),
    ("Streamlit",         "Web Framework"),
    ("MySQL",             "Database"),
    ("Pandas",            "Data Processing"),
    ("openpyxl",          "Excel Engine"),
    ("mysql-connector",   "DB Driver"),
]

_CHANGELOG = [
    ("v2.5", "2025",
     "Xóa debug code, thêm nút Xóa tất cả Pre-Order, cải thiện UI/UX toàn bộ, "
     "fix primaryColor theme, cập nhật tài liệu đầy đủ."),
    ("v2.0", "2025",
     "Redesign UI với design system Emerald, cải thiện sidebar, "
     "thêm badge DB connection, refactor CSS thành design tokens."),
    ("v1.0", "2024",
     "Phiên bản đầu tiên: Pre-Order, Data Browser, Import/Export Excel, "
     "View Templates, xác thực SHA-256."),
]


# ─────────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────────

def _feature_card(icon: str, title: str, desc: str) -> str:
    return f"""
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                padding:1.2rem 1.4rem;height:100%;
                border-top:3px solid #10b981;
                box-shadow:0 1px 3px rgba(15,23,42,.05);
                transition:box-shadow .2s;">
        <div style="font-size:1.5rem;margin-bottom:.6rem;">{icon}</div>
        <div style="font-size:.9rem;font-weight:700;color:#0f172a;
                    margin-bottom:.4rem;">{title}</div>
        <div style="font-size:.82rem;color:#64748b;line-height:1.55;">{desc}</div>
    </div>
    """


def _tech_pill(name: str, role: str) -> str:
    return (
        f'<div style="display:inline-flex;align-items:center;gap:6px;'
        f'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;'
        f'padding:6px 12px;margin:4px;">'
        f'<span style="font-size:.82rem;font-weight:600;color:#0f172a;">{name}</span>'
        f'<span style="font-size:.72rem;color:#94a3b8;">·</span>'
        f'<span style="font-size:.72rem;color:#64748b;">{role}</span>'
        f'</div>'
    )


def _changelog_row(version: str, year: str, notes: str) -> str:
    return (
        f'<div style="display:flex;gap:1rem;padding:.75rem 0;'
        f'border-bottom:1px solid #f1f5f9;">'
        f'<div style="min-width:48px;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.75rem;'
        f'font-weight:700;color:#10b981;background:#ecfdf5;'
        f'padding:2px 8px;border-radius:6px;">{version}</span>'
        f'</div>'
        f'<div style="min-width:36px;font-size:.78rem;color:#94a3b8;'
        f'padding-top:2px;">{year}</div>'
        f'<div style="font-size:.82rem;color:#334155;line-height:1.5;">{notes}</div>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        page_header("SUPPLY_CHAIN / ABOUT", "VỀ ỨNG DỤNG"),
        unsafe_allow_html=True,
    )

    # ── Hero banner ───────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#ecfdf5 0%,#f0fdf4 100%);
                    border:1px solid rgba(16,185,129,.2);border-radius:16px;
                    padding:2rem 2.5rem;margin-bottom:2rem;
                    display:flex;align-items:center;gap:1.5rem;">
            <div style="background:#10b981;color:#fff;width:56px;height:56px;
                        border-radius:14px;display:flex;align-items:center;
                        justify-content:center;font-size:1.8rem;flex-shrink:0;
                        box-shadow:0 8px 24px rgba(16,185,129,.3);">🛒</div>
            <div>
                <div style="font-size:1.4rem;font-weight:800;color:#0f172a;
                            letter-spacing:-.02em;">Supply Chain Management</div>
                <div style="font-size:.88rem;color:#64748b;margin-top:3px;">
                    OQR Co. Ltd &nbsp;·&nbsp; Hệ thống quản lý chuỗi cung ứng
                    &nbsp;·&nbsp;
                    <span style="font-family:'JetBrains Mono',monospace;
                                 font-size:.8rem;font-weight:700;color:#10b981;">
                        {APP_VERSION}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tính năng chính ───────────────────────────────────
    st.markdown(
        '<div style="font-size:.72rem;font-weight:700;color:#64748b;'
        'text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem;">'
        '⚡ TÍNH NĂNG CHÍNH</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(_FEATURES))
    for col, (icon, title, desc) in zip(cols, _FEATURES):
        with col:
            st.markdown(_feature_card(icon, title, desc), unsafe_allow_html=True)

    st.markdown(divider(margin="2rem 0 1.5rem 0"), unsafe_allow_html=True)

    # ── Tech stack + Changelog ────────────────────────────
    left, right = st.columns([1, 1.2])

    with left:
        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:#64748b;'
            'text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;">'
            '🔧 CÔNG NGHỆ SỬ DỤNG</div>',
            unsafe_allow_html=True,
        )
        pills = "".join(_tech_pill(n, r) for n, r in _TECH_STACK)
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{pills}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="background:#f8fafc;border:1px solid #e2e8f0;
                        border-radius:10px;padding:1rem 1.2rem;">
                <div style="font-size:.72rem;font-weight:700;color:#64748b;
                            text-transform:uppercase;letter-spacing:.07em;
                            margin-bottom:.6rem;">📁 CẤU TRÚC DỰ ÁN</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;
                            color:#334155;line-height:1.8;">
                    app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; — Entry point<br>
                    login.py &nbsp;&nbsp;&nbsp;&nbsp; — Xác thực<br>
                    pages/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; — Các trang chính<br>
                    modules/ &nbsp;&nbsp;&nbsp;&nbsp; — Business logic<br>
                    components/ &nbsp; — UI components<br>
                    db/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; — Database layer<br>
                    utils/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; — Tiện ích<br>
                    templates/ &nbsp;&nbsp; — Template Excel<br>
                    scripts/ &nbsp;&nbsp;&nbsp;&nbsp; — Admin scripts<br>
                    config/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; — Cấu hình JSON
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:#64748b;'
            'text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;">'
            '📋 LỊCH SỬ PHIÊN BẢN</div>',
            unsafe_allow_html=True,
        )
        rows = "".join(_changelog_row(v, y, n) for v, y, n in _CHANGELOG)
        st.markdown(
            f'<div style="border:1px solid #e2e8f0;border-radius:10px;'
            f'padding:.5rem 1rem;">{rows}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="background:#fff7ed;border:1px solid #fed7aa;
                        border-radius:10px;padding:1rem 1.2rem;">
                <div style="font-size:.72rem;font-weight:700;color:#9a3412;
                            text-transform:uppercase;letter-spacing:.07em;
                            margin-bottom:.5rem;">🔒 BẢO MẬT</div>
                <div style="font-size:.82rem;color:#7c2d12;line-height:1.6;">
                    · Password mã hóa <b>SHA-256</b><br>
                    · File <code>log/log.xlsx</code> nằm trong .gitignore<br>
                    · Session-based auth + URL params survive F5<br>
                    · Không lưu plain-text credentials
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(divider(margin="2rem 0 1rem 0"), unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="text-align:center;padding:.5rem 0;">
            <div style="font-size:.78rem;color:#94a3b8;">
                © 2025 <b style="color:#64748b;">OQR Co. Ltd</b>
                &nbsp;·&nbsp; Supply Chain Management
                &nbsp;·&nbsp;
                <span style="font-family:'JetBrains Mono',monospace;
                             color:#10b981;font-weight:600;">{APP_VERSION}</span>
            </div>
            <div style="font-size:.72rem;color:#cbd5e1;margin-top:4px;">
                Tài liệu đầy đủ tại <code>docs/USER_GUIDE.md</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
