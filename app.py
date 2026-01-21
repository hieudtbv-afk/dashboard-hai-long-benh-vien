import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
st.sidebar.header("👤 Phân quyền truy cập")

role = st.sidebar.selectbox(
    "Chọn vai trò",
    ["Lãnh đạo", "Quản lý chất lượng", "Khoa"]
)

if role == "Khoa":
    khoa_user = st.sidebar.selectbox(
        "Chọn khoa của bạn",
        df['khoa'].unique()
    )
    filtered_df = filtered_df[filtered_df['khoa'] == khoa_user]

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
# 5. BỘ LỌC (SIDEBAR)
# =====================
st.sidebar.header("🔎 Bộ lọc dữ liệu")

# Lọc khoa
khoa_list = sorted(df['khoa'].dropna().unique())
selected_khoa = st.sidebar.multiselect(
    "Chọn khoa",
    khoa_list,
    default=khoa_list
)

# Lọc thời gian
min_date = df['Timestamp'].min().date()
max_date = df['Timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Chọn khoảng thời gian",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Áp dụng filter
filtered_df = df[
    (df['khoa'].isin(selected_khoa)) &
    (df['Timestamp'].dt.date >= date_range[0]) &
    (df['Timestamp'].dt.date <= date_range[1])
]

# =====================
# 6. KPI TỔNG QUAN
# =====================
st.markdown("## 📌 Tổng quan nhanh")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🧾 Tổng số phản hồi", len(filtered_df))

with col2:
    st.metric(
        "⭐ Điểm hài lòng trung bình",
        round(filtered_df['Do_hai_long'].mean(), 2)
        if len(filtered_df) > 0 else 0
    )

with col3:
    if len(filtered_df) > 0:
        st.metric(
            "🕒 Phản hồi mới nhất",
            filtered_df['Timestamp'].max().strftime("%d/%m/%Y %H:%M")
        )
    else:
        st.metric("🕒 Phản hồi mới nhất", "—")
        
st.markdown("## 🧪 Đánh giá theo tiêu chí Bộ Y tế")

def xep_loai(diem):
    if diem >= 4.0:
        return "🟢 Đạt"
    elif diem >= 3.5:
        return "🟡 Cần cải thiện"
    else:
        return "🔴 Không đạt"

by_khoa = (
    filtered_df.groupby("khoa")["Do_hai_long"]
    .mean()
    .reset_index()
)

by_khoa["Xếp loại"] = by_khoa["Do_hai_long"].apply(xep_loai)
by_khoa["Điểm TB"] = by_khoa["Do_hai_long"].round(2)

st.dataframe(
    by_khoa[["khoa", "Điểm TB", "Xếp loại"]],
    use_container_width=True
)

# =====================
# 7. BIỂU ĐỒ HÀI LÒNG THEO KHOA
# =====================
st.markdown("## 🏥 Mức độ hài lòng theo khoa")

avg_by_khoa = (
    filtered_df.groupby("khoa")["Do_hai_long"]
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(avg_by_khoa)

# =====================
# 8. XU HƯỚNG HÀI LÒNG THEO THỜI GIAN
# =====================
st.markdown("## 📈 Xu hướng hài lòng theo thời gian")

df_time = (
    filtered_df.set_index("Timestamp")
    .resample("D")["Do_hai_long"]
    .mean()
)

st.line_chart(df_time)

# =====================
# 9. BẢNG CẢNH BÁO PHẢN HỒI THẤP
# =====================
st.markdown("## 🚨 Phản hồi cần chú ý (≤ 2 điểm)")

negative_df = filtered_df[filtered_df['Do_hai_long'] <= 2]

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
# 10. WORD CLOUD GÓP Ý
# =====================
st.markdown("## 🧠 Phân tích ý kiến góp ý")

if 'nguoi_gop_y' in filtered_df.columns:
    text_data = filtered_df['nguoi_gop_y'].dropna()
    text = " ".join(text_data.astype(str))

    if len(text.strip()) > 0:
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            collocations=False
        ).generate(text)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("Chưa có nội dung góp ý dạng chữ")
else:
    st.info("Không tìm thấy cột góp ý")

# =====================
# 11. XEM TOÀN BỘ DỮ LIỆU
# =====================
with st.expander("📋 Xem toàn bộ dữ liệu khảo sát"):
    st.dataframe(filtered_df, use_container_width=True)
from report import export_ppt

st.markdown("## 📤 Xuất báo cáo")

if st.button("📊 Xuất báo cáo PowerPoint"):
    export_ppt(filtered_df)
    st.success("Đã tạo file bao_cao_hai_long.pptx (xem trong thư mục dự án)")
