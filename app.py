# =====================
# 0. IMPORT
# =====================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from report import export_ppt

# =====================
# 1. CẤU HÌNH TRANG (PHẢI ĐẶT TRÊN CÙNG)
# =====================
st.set_page_config(
    page_title="Dashboard Hài Lòng Người Bệnh",
    layout="wide"
)

# =====================
# 2. THÔNG TIN GOOGLE SHEETS
# =====================
SHEET_ID = "ukN4ftXcAtRidpv26"
SHEET_NAME = "Form_Responses"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&sheet={SHEET_NAME}"
)

@st.cache_data(ttl=600)  # 10 phút cập nhật 1 lần
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# =====================
# 3. CHUẨN HOÁ DỮ LIỆU
# =====================

# Chuẩn hoá tên cột
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Chuẩn hoá khoa (Nội C ≡ nội c)
df["khoa"] = (
    df["khoa"]
    .astype(str)
    .str.strip()
    .str.title()
)

# Thời gian
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# =====================
# 4. MAP ĐIỂM CHO CÁC CÂU DẠNG CHỌN
# =====================
score_map = {
    "Rất hài lòng": 5,
    "Hài lòng": 4,
    "Bình thường": 3,
    "Chưa hài lòng": 2,
    "Rất không hài lòng": 1,
    "Rất kém": 1,
    "Kém": 2
}

cols_score = [
    "thai_do",
    "thu_tuc",
    "chuyen_mon",
    "hieu_qua",
    "thoi_gian_cho",
    "co_so_vat_chat"
]

for col in cols_score:
    if col in df.columns:
        df[col + "_score"] = df[col].map(score_map)

# =====================
# 5. TÍNH ĐIỂM HÀI LÒNG TỔNG
# =====================
score_cols = [c for c in df.columns if c.endswith("_score")]

df["diem_hai_long"] = df[score_cols].mean(axis=1)

df = df.dropna(subset=["timestamp", "diem_hai_long"])

# =====================
# 6. TIÊU ĐỀ
# =====================
st.title("📊 DASHBOARD ĐÁNH GIÁ SỰ HÀI LÒNG NGƯỜI BỆNH")
st.subheader("BV Đa khoa số 1 tỉnh Lào Cai")
st.info("📌 Dữ liệu cập nhật tự động từ Google Forms (10 phút/lần)")

# =====================
# 7. SIDEBAR – BỘ LỌC
# =====================
st.sidebar.header("🔎 Bộ lọc dữ liệu")

khoa_list = sorted(df["khoa"].unique())
selected_khoa = st.sidebar.multiselect(
    "Chọn khoa",
    khoa_list,
    default=khoa_list
)

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Khoảng thời gian",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    (df["khoa"].isin(selected_khoa)) &
    (df["timestamp"].dt.date >= date_range[0]) &
    (df["timestamp"].dt.date <= date_range[1])
]

# =====================
# 8. KPI TỔNG QUAN
# =====================
st.markdown("## 📌 Tổng quan")

c1, c2, c3 = st.columns(3)

c1.metric("🧾 Tổng phản hồi", len(filtered_df))
c2.metric("⭐ Điểm TB", round(filtered_df["diem_hai_long"].mean(), 2))

if len(filtered_df) > 0:
    c3.metric(
        "🕒 Phản hồi mới nhất",
        filtered_df["timestamp"].max().strftime("%d/%m/%Y %H:%M")
    )

# =====================
# 9. ĐÁNH GIÁ THEO KHOA
# =====================
st.markdown("## 🏥 Hài lòng theo khoa")

by_khoa = (
    filtered_df
    .groupby("khoa")["diem_hai_long"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)

st.bar_chart(by_khoa)

# =====================
# 10. PHẢN HỒI TIÊU CỰC
# =====================
st.markdown("## 🚨 Phản hồi chưa hài lòng")

bad_df = filtered_df[filtered_df["diem_hai_long"] <= 2.5]

if bad_df.empty:
    st.success("🎉 Không có phản hồi tiêu cực")
else:
    st.dataframe(
        bad_df[
            ["timestamp", "khoa", "diem_hai_long",
             "thai_do", "thu_tuc", "chuyen_mon"]
        ],
        use_container_width=True
    )

# =====================
# 11. WORDCLOUD GÓP Ý
# =====================
st.markdown("## 💬 Ý kiến người bệnh")

text_cols = ["hai_long", "khong_hai_long"]
texts = []

for col in text_cols:
    if col in filtered_df.columns:
        texts += filtered_df[col].dropna().astype(str).tolist()

text = " ".join(texts)

if text.strip():
    wc = WordCloud(
        width=900,
        height=400,
        background_color="white"
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("Chưa có nội dung góp ý")

# =====================
# 12. XUẤT BÁO CÁO
# =====================
st.markdown("## 📤 Xuất báo cáo")

if st.button("📊 Xuất PowerPoint"):
    file_path = export_ppt(filtered_df)
    st.success(f"✅ Đã tạo báo cáo: {file_path}")
