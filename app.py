import streamlit as st
import pandas as pd

# =====================
# CẤU HÌNH TRANG
# =====================
st.set_page_config(
    page_title="Dashboard Hài Lòng Người Bệnh",
    layout="wide"
)

# =====================
# TIÊU ĐỀ
# =====================
st.title("📊 DASHBOARD ĐÁNH GIÁ SỰ HÀI LÒNG NGƯỜI BỆNH")
st.subheader("BV Đa khoa số 1 tỉnh Lào Cai")

st.info("📌 Dữ liệu được cập nhật tự động từ Google Forms")

# =====================
# KẾT NỐI GOOGLE SHEETS
# =====================
SHEET_ID = "1vHPkRbZGxhLZr9N60tFyKzgUkbnRKB_-Dg7FaCiqtBo"
SHEET_NAME = "Form_Responses"  # nếu sheet tên khác, báo mình

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# =====================
# HIỂN THỊ DỮ LIỆU
# =====================
st.markdown("## 📋 Dữ liệu khảo sát")
st.dataframe(df, use_container_width=True)

# =====================
# THỐNG KÊ NHANH
# =====================
st.markdown("## 📈 Thống kê nhanh")

col1, col2 = st.columns(2)

with col1:
    st.metric("🧾 Tổng số phiếu khảo sát", len(df))

with col2:
    st.metric("🕒 Bản ghi mới nhất", df.iloc[-1, 0])
