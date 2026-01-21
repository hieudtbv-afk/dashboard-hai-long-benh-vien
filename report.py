from pptx import Presentation

def export_ppt(df, output_path="bao_cao_hai_long.pptx"):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])

    slide.shapes.title.text = "BÁO CÁO HÀI LÒNG NGƯỜI BỆNH"
    slide.placeholders[1].text = f"Tổng số phản hồi: {len(df)}"

    prs.save(output_path)
    return output_path
