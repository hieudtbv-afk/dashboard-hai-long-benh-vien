from pptx import Presentation
import pandas as pd

def export_ppt(df):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "BÁO CÁO KHẢO SÁT SỰ HÀI LÒNG NGƯỜI BỆNH"
    slide.placeholders[1].text = "BV Đa khoa số 1 tỉnh Lào Cai"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Tổng quan"
    slide.placeholders[1].text = (
        f"Tổng số phản hồi: {len(df)}\n"
        f"Điểm hài lòng trung bình: {round(df['Do_hai_long'].mean(),2)}"
    )

    prs.save("bao_cao_hai_long.pptx")
