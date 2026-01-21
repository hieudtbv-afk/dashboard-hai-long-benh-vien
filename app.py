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
SHEET_ID = "ukN4ftXcAtRidpv26"
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
# 9. WORD CLOUD
# =====================
st.markdown("## 🧠 Ý kiến chưa hài lòng")

text_data = bad_df['khong_hai_long'].dropna()

if len(text_data) > 0:
    wc = WordCloud(width=800, height=400, background_color="white")
    wc.generate(" ".join(text_data.astype(str)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("Chưa có góp ý tiêu cực")
