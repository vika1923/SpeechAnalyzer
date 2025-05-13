from faster_whisper.transcribe import Word
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
import random
import matplotlib.pyplot as plt
from typing import List, Dict
import os
from custom_types import PartOfSpeech, Point, WordBoundary

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

def _wrap_and_hyphenate(text: str, font: str, size: float, max_width: float):
    """
    Breaks `text` into lines that fit within `max_width`, using simple hyphenation
    at existing hyphens or by splitting long words.
    Returns: List of (line_text, start_char_index).
    """
    # WARNING: created by Chat Gypyty
    # TODO: Test Everything So it works
    words = text.split(' ')
    lines = []
    current_line = ""
    index = 0  # running char index in original text
    line_start_idx = 0

    for w in words:
        w_with_space = ("" if current_line=="" else " ") + w
        test_line = current_line + w_with_space
        w_width = pdfmetrics.stringWidth(test_line, font, size)
        if w_width <= max_width:
            current_line = test_line
        else:
            # try hyphenation at existing hyphens
            if '-' in w and pdfmetrics.stringWidth(current_line + " " + w[:w.index('-')+1]+'-', font, size) <= max_width:
                # split at hyphen
                prefix = w[:w.index('-')+1] + '-'
                suffix = w[w.index('-')+1:]
                current_line += ("" if current_line=="" else " ") + prefix
                lines.append((current_line, line_start_idx))
                line_start_idx = index + len(prefix) + (1 if current_line!="" else 0)
                current_line = suffix
            else:
                # forced break: put current_line, start fresh
                lines.append((current_line, line_start_idx))
                line_start_idx = index + (1 if current_line!="" else 0)
                current_line = w
        index += len(w_with_space)
    if current_line:
        lines.append((current_line, line_start_idx))
    return lines

def _draw_highlights(pdf, x, y, line_text, line_idx0, font, size,
                     under_spans, squiggle_spans, color_spans):
    """
    Draws red underlines / squiggles / rect highlights for all spans
    that overlap this line.
    """
    # WARNING: created by Chat Gypyty
    # TODO: Test Everything So it works
    pdf.setLineWidth(1)
    text_widths = [pdfmetrics.stringWidth(line_text[:i], font, size) for i in range(len(line_text)+1)]
    for span_list, style in (
        (under_spans, 'underline'),
        (squiggle_spans, 'squiggle'),
        (color_spans, 'color'),
    ):
        for (span_start, span_end) in span_list:
            # check overlap
            line_start = line_idx0
            line_end = line_idx0 + len(line_text)
            if span_end <= line_start or span_start >= line_end:
                continue
            # compute in‐line coords
            s = max(span_start, line_start) - line_start
            e = min(span_end, line_end)   - line_start
            x0 = x + text_widths[s]
            x1 = x + text_widths[e]
            if style == 'color':
                pdf.setFillColorRGB(1,0,0, alpha=0.2)
                pdf.rect(x0, y - size*0.2, x1 - x0, size*1.1, fill=1, stroke=0)
                pdf.setFillColorRGB(0,0,0)
            else:
                pdf.setStrokeColorRGB(1,0,0)
                if style == 'underline':
                    pdf.line(x0, y-2, x1, y-2)
                else:  # squiggle
                    period = 4
                    amp = 1.5
                    x_pos = x0
                    toggle = False
                    while x_pos < x1:
                        y_off = amp if toggle else 0
                        pdf.line(x_pos, y-2+y_off, min(x_pos+period, x1), y-2 + (0 if toggle else amp))
                        x_pos += period
                        toggle = not toggle
                pdf.setStrokeColorRGB(0,0,0)


def draw_text_block(pdf: canvas.Canvas,
                    x: float, y: float,
                    width: float, text: str,
                    underline_spans: List[WordBoundary],
                    squiggle_spans: List[WordBoundary],
                    color_spans: List[WordBoundary],
                    font="Times-Roman", size=12):
    """
    Draws `text` within a box of given `width`, starting at (x,y).  
    *underline_spans*, *squiggle_spans*, *color_spans* are lists of (start_idx,end_idx)
    in the original `text` where you want each style.  All highlighting is in red.
    Returns the new y position after drawing the block.
    """
    # WARNING: created by Chat Gypyty
    # TODO: Test Everything So it works

    # wrap & hyphenate
    lines = _wrap_and_hyphenate(text, font, size, width)

    pdf.setFont(font, size)
    line_height = size * 1.2

    for line_text, line_idx0 in lines:
        # draw text
        pdf.drawString(x, y, line_text)
        # draw any highlights on this line
        _draw_highlights(pdf, x, y, line_text, line_idx0, font, size,
                         underline_spans, squiggle_spans, color_spans)
        y -= line_height

        # if you want page‐break logic, call maybe_new_page here:
        # y = maybe_new_page(pdf, y, line_height, A4[1])

    return y

def create_pdf(
        punctuated_text: str,
        word_count: int, 
        parts_of_speech: Dict[PartOfSpeech, int], 
        rate_of_speech_points: List[Point],
        volume_points: List[Point],
        pronunciation_mistakes: List[WordBoundary],
        floss_mistakes: List[WordBoundary],
        grammar_mistakes: List[WordBoundary],
        image_scaling: float = 2 / 3,
):
    for dir_name in ["pdfs", "graphs"]:
        os.makedirs(dir_name, exist_ok=True)

    report_number = int(random.random()*10000)
    pdf = canvas.Canvas(f"pdfs/goldenbek{report_number}.pdf")
    page_width, page_height = A4
    margin = 50
    x = 50
    y = page_height - margin

    # Title
    pdf.setTitle(f"Speech Report #{report_number}") 
    y = draw_title(pdf, x, y, f"Speech Report #{report_number}")

    # Stats
    stats = [f"Word Count: {word_count}"]
    for name, count in parts_of_speech.items():
        stats.append(f"{name}: {count}")
    y = draw_stats(pdf, x, y, stats)


    # Text blocks
    column_width = page_width - margin * 2
    y = draw_text_block(pdf, x, y, column_width, punctuated_text, pronunciation_mistakes, floss_mistakes, grammar_mistakes)

    # Graphs
    create_plot(rate_of_speech_points, "Rate of speech", "Time", "Rate of speech (per second)", "graphs/ros.png")
    create_plot(volume_points, "Volume", "Time", "dB", "graphs/vol.png")

    img_width = 400 * image_scaling
    img_height = 300 * image_scaling
    y = draw_graph(pdf, x, y, "graphs/ros.png", img_width, img_height)
    y = draw_graph(pdf, x, y, "graphs/vol.png", img_width, img_height)

    pdf.save()




