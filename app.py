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
    '
