from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

import os

def create_plot(points: List[Tuple[float, float]], title: str, x_axis_name: str, y_axis_name: str, save_to_path: str) -> None:
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

def create_pdf(
        word_count: int, 
        parts_of_speech: Dict[str, int], 
        rate_of_speech_points: List[Tuple[float, float]],
        volume_points: List[Tuple[float, float]],
):
    for dir_name in ["pdfs", "graphs"]:
        os.makedirs(dir_name, exist_ok=True)

    report_number = int(random.random()*10000)
    pdf = canvas.Canvas(f"pdfs/goldenbek{report_number}.pdf")
    page_width, page_height = A4
    x = 50
    y = page_height - 50
    line_height = 15

    # Title
    pdf.setTitle(f"Speech Report #{report_number}") 
    y = draw_title(pdf, x, y, f"Speech Report #{report_number}")

    # Stats
    stats = [
        f"Word Count: {word_count}"
    ]
    for name, count in parts_of_speech.items():
        stats.append(f"{name}: {count}")

    y = draw_stats(pdf, x, y, stats)

    # TODO: ADD grammary stuff here
    # and the Verbal Pauses

    # Graphs
    create_plot(rate_of_speech_points, "Rate of speech", "Time", "Rate of speech (per second)", "graphs/ros.png")
    create_plot(volume_points, "Volume", "Time", "dB", "graphs/vol.png")

    # TODO: fix if the image goes out of the border
    scale = 2 / 3
    img_width = 400 * scale
    img_height = 300 * scale
    y = draw_graph(pdf, x, y, "graphs/ros.png", img_width, img_height)
    y = draw_graph(pdf, x, y, "graphs/vol.png", img_width, img_height)

    pdf.save()




