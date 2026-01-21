import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# =====================
# 1. CẤU HÌNH TRANG (PHẢI ĐẶT TRÊN CÙNG)
# =====================
st.set_page_config(
    page_title="Dashboard Hài Lòng Người Bệnh",
    layout="wide"
)

# =====================
# 2. KẾT NỐI GOOGLE SHEETS
# =====================
SHEET_ID = "1vHPkRbZGxhLZr9N60tFyKzgUkbnRKB_-Dg7FaCiqtBo"
SHEET_NAME = "Form_Responses"   # ✅ ĐÚNG NHƯ BẠN XÁC NHẬN

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&sheet={SHEET_NAME}"
)

@st.cache_data
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# =====================
# 3. TIÊU ĐỀ DASHBOARD
# =====================
st.title("📊 DASHBOARD ĐÁNH GIÁ SỰ HÀI LÒNG NGƯỜI BỆNH")
st.subheader("BV Đa khoa số 1 tỉnh Lào Cai")
st.info("📌 Dữ liệu cập nhật tự động từ Google Forms")

# =====================
# 4. CHUẨN HÓA DỮ LIỆU
# =====================
df.columns = df.columns.str.strip()

df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Do_hai_long'] = pd.to_numeric(df['Do_hai_long'], errors='coerce')

df = df.dropna(subset=['Timestamp', 'Do_hai_long'])

# =====================
# 5. SIDEBAR – BỘ LỌC
# =====================
st.sidebar.header("🔎 Bộ lọc dữ liệu")

khoa_list = sorted(df['khoa'].dropna().unique())
selected_khoa = st.sidebar.multiselect(
    "Chọn khoa",
    khoa_list,
    default=khoa_list
)

min_date = df['Timestamp'].min().date()
max_date = df['Timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Khoảng thời gian",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    (df['khoa'].isin(selected_khoa)) &
    (df['Timestamp'].dt.date >= date_range[0]) &
    (df['Timestamp'].dt.date <= date_range[1])
]

# =====================
# 6. KPI TỔNG QUAN
# =====================
st.markdown("## 📌 Tổng quan nhanh")

c1, c2, c3 = st.columns(3)

c1.metric("🧾 Tổng số phản hồi", len(filtered_df))
c2.metric(
    "⭐ Điểm hài lòng trung bình",
    round(filtered_df['Do_hai_long'].mean(), 2)
    if len(filtered_df) else 0
)
c3.metric(
    "🕒 Phản hồi mới nhất",
    filtered_df['Timestamp'].max().strftime("%d/%m/%Y %H:%M")
    if len(filtered_df) else "—"
)

# =====================
# 7. ĐÁNH GIÁ THEO KHOA (BỘ Y TẾ)
# =====================
st.markdown("## 🧪 Đánh giá theo khoa")

def xep_loai(d):
    if d >= 4.0:
        return "🟢 Đạt"
    elif d >= 3.5:
        return "🟡 Cần cải thiện"
    else:
        return "🔴 Không đạt"

by_khoa = (
    filtered_df.groupby("khoa")["Do_hai_long"]
    .mean()
    .reset_index()
)

by_khoa["Điểm TB"] = by_khoa["Do_hai_long"].round(2)
by_khoa["Xếp loại"] = by_khoa["Do_hai_long"].apply(xep_loai)

st.dataframe(
    by_khoa[["khoa", "Điểm TB", "Xếp loại"]],
    use_container_width=True
)

# =====================
# 8. BIỂU ĐỒ
# =====================
st.markdown("## 🏥 Mức độ hài lòng theo khoa")
st.bar_chart(
    by_khoa.set_index("khoa")["Điểm TB"]
)

st.markdown("## 📈 Xu hướng hài lòng theo thời gian")
trend = (
    filtered_df.set_index("Timestamp")
    .resample("D")["Do_hai_long"]
    .mean()
)
st.line_chart(trend)

# =====================
# 9. PHẢN HỒI TIÊU CỰC
# =====================
st.markdown("## 🚨 Phản hồi cần xử lý (≤ 2 điểm)")

bad_df = filtered_df[filtered_df['Do_hai_long'] <= 2]

if bad_df.empty:
    st.success("🎉 Không có phản hồi tiêu cực")
else:
    st.dataframe(bad_df, use_container_width=True)

# =====================
# 10. WORD CLOUD GÓP Ý
# =====================
st.markdown("## 💬 Ý kiến góp ý của người bệnh")

if 'nguoi_gop_y' in filtered_df.columns:
    text = " ".join(filtered_df['nguoi_gop_y'].dropna().astype(str))
    if text.strip():
        wc = WordCloud(
            width=900,
            height=400,
            background_color="white",
            collocations=False
        ).generate(text)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("Chưa có nội dung góp ý")
else:
    st.info("Không tìm thấy cột góp ý")

# =====================
# 11. XEM DỮ LIỆU GỐC
# =====================
with st.expander("📋 Xem toàn bộ dữ liệu khảo sát"):
    st.dataframe(filtered_df, use_container_width=True)

# =====================
# 12. XUẤT BÁO CÁO
# =====================
from report import export_ppt

st.markdown("## 📤 Xuất báo cáo")

if st.button("📊 Tạo báo cáo PowerPoint"):
    file_path = export_ppt(filtered_df)

    with open(file_path, "rb") as f:
        st.download_button(
            label="⬇️ Tải file PowerPoint",
            data=f,
            file_name="bao_cao_hai_long.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

