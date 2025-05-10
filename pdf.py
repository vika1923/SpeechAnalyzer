from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
from custom_types import UnderlineType, PartOfSpeech, Point, ColorType, WordBoundary

def create_plot(points: List[Point], title: str, x_axis_name: str, y_axis_name: str, save_to_path: str) -> None:
    x, y = zip(*points)
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.savefig(save_to_path)
    plt.close()

def maybe_new_page(pdf: canvas.Canvas, current_y: float, needed_space: float, page_height: float) -> float:
    """Start a new page if there's not enough vertical space."""
    if current_y - needed_space < 50:
        pdf.showPage()
        return page_height - 50
    return current_y

def draw_title(pdf: canvas.Canvas, x: float, y: float, title: str, font: str = "Times-Roman", size: int = 16) -> float:
    """Draw the title on the PDF."""
    pdf.setFont(font, size)
    pdf.drawString(x, y, title)
    return y - 30

def draw_stats(pdf: canvas.Canvas, x: float, y: float, stats: List[str], font: str = "Times-Roman", size: int = 12) -> float:
    """Draw the statistics (word count, parts of speech, etc.) on the PDF."""
    pdf.setFont(font, size)
    for stat in stats:
        y = maybe_new_page(pdf, y, 15, A4[1])
        pdf.drawString(x, y, stat)
        y -= 15
    return y

def draw_graph(pdf: canvas.Canvas, x: float, y: float, img_path: str, img_width: float, img_height: float) -> float:
    """Draw the image on the PDF with boundary checks."""
    y = maybe_new_page(pdf, y, img_height + 20, A4[1])  # Check if space is available
    pdf.drawImage(img_path, x, y - img_height, width=img_width, height=img_height)
    return y - (img_height + 20)



def draw_block_of_text_with_underline_styles(
    pdf: canvas.Canvas, x: float, y: float, text: str, 
    highlight: List[Tuple[WordBoundary, ColorType]] = [],
    underline: List[Tuple[WordBoundary, UnderlineType]] = [],
    font: str = "Times-Roman", size: int = 12, 
    line_height: float = 14, max_width: float = 500
) -> float:
    pdf.setFont(font, size)
    lines = []
    current_line = ""
    current_index = 0

    words = text.split(" ")
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if stringWidth(test_line, font, size) > max_width:
            lines.append((current_line, current_index - len(current_line)))
            current_line = word
        else:
            current_line = test_line
        current_index += len(word) + 1  # +1 for space
    if current_line:
        lines.append((current_line, len(text) - len(current_line)))

    for line_text, global_offset in lines:
        underline_y = y - 2

        # Draw highlights
        for (start, end), color in highlight:
            if end <= global_offset or start >= global_offset + len(line_text):
                continue  # Not in this line
            sub_start = max(start, global_offset)
            sub_end = min(end, global_offset + len(line_text))
            prefix = line_text[:sub_start - global_offset]
            sub = line_text[sub_start - global_offset:sub_end - global_offset]

            highlight_x = x + stringWidth(prefix, font, size)
            width = stringWidth(sub, font, size)
            pdf.setFillColorRGB(*color)
            pdf.rect(highlight_x, y - line_height + 2, width, line_height - 2, fill=1)
            pdf.setFillColor(colors.black)

        # Draw text
        pdf.drawString(x, y, line_text)

        # Draw underlines
        for (start, end), style in underline:
            if end <= global_offset or start >= global_offset + len(line_text):
                continue
            sub_start = max(start, global_offset)
            sub_end = min(end, global_offset + len(line_text))
            prefix = line_text[:sub_start - global_offset]
            sub = line_text[sub_start - global_offset:sub_end - global_offset]

            underline_x = x + stringWidth(prefix, font, size)
            width = stringWidth(sub, font, size)

            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(0.7)

            if style == "solid":
                pdf.line(underline_x, underline_y, underline_x + width, underline_y)
            elif style == "dashed":
                pdf.setDash(3, 2)
                pdf.line(underline_x, underline_y, underline_x + width, underline_y)
                pdf.setDash()
            elif style == "dotted":
                pdf.setDash(1, 3)
                pdf.line(underline_x, underline_y, underline_x + width, underline_y)
                pdf.setDash()
            elif style == "double":
                pdf.line(underline_x, underline_y, underline_x + width, underline_y)
                pdf.line(underline_x, underline_y - 2, underline_x + width, underline_y - 2)

        y -= line_height

    return y

def create_pdf(
        word_count: int, 
        parts_of_speech: Dict[PartOfSpeech, int], 
        rate_of_speech_points: List[Point],
        volume_points: List[Point],
        image_scaling: float = 2 / 3
):
    for dir_name in ["pdfs", "graphs"]:
        os.makedirs(dir_name, exist_ok=True)

    report_number = int(random.random()*10000)
    pdf = canvas.Canvas(f"pdfs/goldenbek{report_number}.pdf")
    _, page_height = A4
    x = 50
    y = page_height - 50

    # Title
    pdf.setTitle(f"Speech Report #{report_number}") 
    y = draw_title(pdf, x, y, f"Speech Report #{report_number}")

    # Stats
    stats = [f"Word Count: {word_count}"]
    for name, count in parts_of_speech.items():
        stats.append(f"{name}: {count}")
    y = draw_stats(pdf, x, y, stats)

    # TODO: ADD grammary stuff here
    # and the Verbal Pauses

    # Graphs
    create_plot(rate_of_speech_points, "Rate of speech", "Time", "Rate of speech (per second)", "graphs/ros.png")
    create_plot(volume_points, "Volume", "Time", "dB", "graphs/vol.png")

    img_width = 400 * image_scaling
    img_height = 300 * image_scaling
    y = draw_graph(pdf, x, y, "graphs/ros.png", img_width, img_height)
    y = draw_graph(pdf, x, y, "graphs/vol.png", img_width, img_height)

    pdf.save()




