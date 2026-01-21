import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# =====================
# 1. CẤU HÌNH TRANG
# =====================
st.set_page_config(
    page_title="Dashboard Hài Lòng Người Bệnh",
    layout="wide"
)

# =====================
# 2. KẾT NỐI GOOGLE SHEETS
# =====================
SHEET_ID = "1vHPkRbZGxhLZr9N60tFyKzgUkbnRKB_-Dg7FaCiqtBo"
SHEET_NAME = "Form_Responses"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&sheet={SHEET_NAME}"
)

@st.cache_data(ttl=300)  # cập nhật mỗi 5 phút
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# =====================
# 3. CHUẨN HOÁ DỮ LIỆU
# =====================
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

def normalize_khoa(x):
    if pd.isna(x):
        return None
    x = str(x).strip().lower()
    if "nội c" in x or "noi c" in x or "noic" in x:
        return "Nội C"
    return x.title()

df['khoa'] = df['khoa'].apply(normalize_khoa)

GRID_SCORE_MAP = {
    "Rất kém": 1,
    "Kém": 2,
    "Bình thường": 3,
    "Tốt": 4,
    "Rất tốt": 5
}

GRID_COLS = [
    'thu_tuc',
    'thai_do',
    'chuyen_mon',
    'hieu_qua',
    'thoi_gian_cho',
    'co_so_vat_chat'
]

for col in GRID_COLS:
    df[col + "_score"] = df[col].map(GRID_SCORE_MAP)

df['grid_avg'] = df[[c + "_score" for c in GRID_COLS]].mean(axis=1)

df['Do_hai_long'] = pd.to_numeric(df['Do_hai_long'], errors='coerce')
df['Do_hai_long_final'] = df['Do_hai_long'].fillna(df['grid_avg'])

df = df.dropna(subset=['Timestamp', 'Do_hai_long_final'])

# =====================
# 4. SIDEBAR FILTER
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
    (min_date, max_date)
)

filtered_df = df[
    (df['khoa'].isin(selected_khoa)) &
    (df['Timestamp'].dt.date >= date_range[0]) &
    (df['Timestamp'].dt.date <= date_range[1])
]

# =====================
# 5. HEADER
# =====================
st.title("📊 DASHBOARD HÀI LÒNG NGƯỜI BỆNH")
st.subheader("BV Đa khoa số 1 tỉnh Lào Cai")

# =====================
# 6. KPI
# =====================
c1, c2, c3 = st.columns(3)

c1.metric("🧾 Tổng phản hồi", len(filtered_df))
c2.metric("⭐ Điểm TB", round(filtered_df['Do_hai_long_final'].mean(), 2))
c3.metric("🚨 Phản hồi ≤ 2",
          len(filtered_df[filtered_df['Do_hai_long_final'] <= 2]))

# =====================
# 7. BIỂU ĐỒ THEO KHOA
# =====================
st.markdown("## 🏥 Hài lòng trung bình theo khoa")

avg_by_khoa = (
    filtered_df.groupby("khoa")["Do_hai_long_final"]
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(avg_by_khoa)

# =====================
# 8. CẢNH BÁO
# =====================
st.markdown("## 🚨 Phản hồi rất kém / chưa hài lòng")

bad_df = filtered_df[
    (filtered_df['Do_hai_long_final'] <= 2) |
    (filtered_df['khong_hai_long'].notna())
]

st.dataframe(
    bad_df[
        ['Timestamp', 'khoa', 'Do_hai_long_final',
         'khong_hai_long', 'sdt']
    ],
    use_container_width=True
)

# =====================
# 9. PHÂN LOẠI HÀI LÒNG
# =====================
st.markdown("## 😊 Tỷ lệ hài lòng / chưa hài lòng")

def classify(row):
    if row["Do_hai_long_final"] <= 3:
        return "Không hài lòng"
    if pd.notna(row["khong_hai_long"]) and str(row["khong_hai_long"]).strip() != "":
        return "Không hài lòng"
    return "Hài lòng"

filtered_df["Trang_thai"] = filtered_df.apply(classify, axis=1)

summary = filtered_df["Trang_thai"].value_counts().reset_index()
summary.columns = ["Trạng thái", "Số lượng"]

st.dataframe(summary, use_container_width=True)

st.bar_chart(
    summary.set_index("Trạng thái")["Số lượng"]
)
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
