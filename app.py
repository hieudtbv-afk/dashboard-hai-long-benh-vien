import streamlit as st
import pandas as pd

# =====================
# 1. CẤU HÌNH TRANG
# =====================
st.set_page_config(
    page_title="Dashboard Hài Lòng Người Bệnh",
    layout="wide"
)

# =====================
# 2. TIÊU ĐỀ
# =====================
st.title("📊 DASHBOARD ĐÁNH GIÁ SỰ HÀI LÒNG NGƯỜI BỆNH")
st.subheader("BV Đa khoa số 1 tỉnh Lào Cai")

st.info("📌 Dữ liệu được cập nhật tự động từ Google Forms")

# =====================
# 3. KẾT NỐI GOOGLE SHEETS
# =====================
SHEET_ID = "ukN4ftXcAtRidpv26"
SHEET_NAME = "Form_Responses"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&sheet={SHEET_NAME}"
)

@st.cache_data
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# =====================
# 4. CHUẨN HÓA DỮ LIỆU
# =====================
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Do_hai_long'] = pd.to_numeric(df['Do_hai_long'], errors='coerce')

df = df.dropna(subset=['Timestamp', 'Do_hai_long'])

# =====================
# 5. KPI TỔNG QUAN
# =====================
st.markdown("## 📌 Tổng quan nhanh")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🧾 Tổng số phản hồi", len(df))

with col2:
    st.metric("⭐ Điểm hài lòng trung bình", round(df['Do_hai_long'].mean(), 2))

with col3:
    st.metric(
        "🕒 Phản hồi mới nhất",
        df['Timestamp'].max().strftime("%d/%m/%Y %H:%M")
    )

# =====================
# 6. BIỂU ĐỒ HÀI LÒNG THEO KHOA
# =====================
st.markdown("## 🏥 Mức độ hài lòng theo khoa")

avg_by_khoa = (
    df.groupby("khoa")["Do_hai_long"]
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(avg_by_khoa)

# =====================
# 7. XU HƯỚNG HÀI LÒNG THEO THỜI GIAN
# =====================
st.markdown("## 📈 Xu hướng hài lòng theo thời gian")

df_time = (
    df.set_index("Timestamp")
    .resample("D")["Do_hai_long"]
    .mean()
)

st.line_chart(df_time)

# =====================
# 8. BẢNG CẢNH BÁO PHẢN HỒI THẤP
# =====================
st.markdown("## 🚨 Phản hồi cần chú ý (≤ 2 điểm)")

negative_df = df[df['Do_hai_long'] <= 2]

if len(negative_df) == 0:
    st.success("🎉 Không có phản hồi tiêu cực")
else:
    st.dataframe(
        negative_df[
            ['Timestamp', 'khoa', 'Do_hai_long', 'thai_do', 'thu_tuc']
        ],
        use_container_width=True
    )

# =====================
# 9. XEM TOÀN BỘ DỮ LIỆU (TÙY CHỌN)
# =====================
with st.expander("📋 Xem toàn bộ dữ liệu khảo sát"):
    st.dataframe(df, use_container_width=True)
