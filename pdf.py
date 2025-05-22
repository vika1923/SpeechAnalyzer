from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from reportlab.lib.colors import red, black
from reportlab.pdfbase.pdfmetrics import stringWidth
import os
from custom_types import PartOfSpeech, Point, ColorType, WordBoundary

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

def block_of_text(
    pdf: canvas.Canvas,
    punctuated_text: str,
    pronunciation_mistakes: List[Tuple[int, int]],
    floss_mistakes: List[Tuple[int, int]],
    grammar_mistakes: List[Tuple[int, int]],
    x: float,
    y: float,
    margin: float,
    font: str = "Times-Roman",
    size: int = 12,
    page_width: float = A4[0],
    page_height: float = A4[1],
) -> float:
    x = x if x is not None else margin
    y = y if y is not None else page_height - margin

    pdf.setFont(font, size)
    line_height = size * 1.5
    max_width = page_width - 2 * margin

    annotations: Dict[int, List[str]] = {}
    def mark(lst: List[Tuple[int, int]], label: str):
        for start, end in lst:
            for i in range(start, end):
                annotations.setdefault(i, []).append(label)

    mark(pronunciation_mistakes, "pron")
    mark(floss_mistakes, "floss")
    mark(grammar_mistakes, "grammar")

    current_x = x

    for i, char in enumerate(punctuated_text):
        annots = annotations.get(i, [])
        char_width = pdf.stringWidth(char, font, size)

        # Line wrap
        if current_x + char_width > margin + max_width:
            current_x = margin
            y -= line_height
            y = maybe_new_page(pdf, y, line_height, page_height)

        # Color
        pdf.setFillColor(red if 'grammar' in annots else black)
        pdf.drawString(current_x, y, char)

        # Underlines
        if 'pron' in annots:
            pdf.line(current_x, y - 2, current_x + char_width, y - 2)
        if 'floss' in annots:
            step = 1.5
            for s in range(int(char_width // step)):
                if s % 2 == 0:
                    pdf.line(current_x + s * step, y - 4, current_x + (s + 1) * step, y - 4)

        current_x += char_width

    return y

def create_pdf(
        punctuated_text: str,
        word_count: int, 
        parts_of_speech: Dict[PartOfSpeech, int], 
        rate_of_speech_points: List[Point],
        volume_points: List[Point],
        image_scaling: float = 2 / 3,
        pronunciation_mistakes=[], # TODO: paste in real values
        floss_mistakes=[],
        grammar_mistakes=[],       # TODO: paste in real values
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




