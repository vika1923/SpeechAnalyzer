from reportlab.pdfgen import canvas 
import random
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict
import os

def create_plot(points: List[Tuple[np.float64, np.float64]], title: str, x_axis_name: str, y_axis_name: str, save_to_path: str) -> None:
    x, y = zip(*points)
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.savefig(save_to_path)
    plt.close()


def create_pdf(
        word_count: int, 
        parts_of_speech: Dict[str, int], 
        rate_of_speech_points: List[Tuple[np.float64, np.float64]],
        volume_points: List[Tuple[np.float64, np.float64]],
):

    for dir_name in ["pdfs", "graphs"]:
        os.makedirs(dir_name, exist_ok=True)

    report_number = int(random.random()*10000)
    pdf = canvas.Canvas(f"pdfs/goldenbek{report_number}.pdf")
    pdf.setTitle(f"Speech Report #{report_number}") 
    texts = [
        f"Word Count: {word_count}"
    ]

    x = 50
    y = 750
    line_height = 15

    for name, count in parts_of_speech.items():
        texts.append(f"{name}: {count}")

    for text in texts: 
        pdf.drawString(x, y, text)
        y -= line_height

    # TODO: ADD grammary stuff here
    # and the Verbal Pauses

    y -= 20

    create_plot(rate_of_speech_points, "Rate of speech", "Time", "Rate of speech (per second)", "graphs/ros.png")
    create_plot(volume_points, "Volume", "Time", "dB", "graphs/vol.png")
 
    img_width = 400
    img_height = 300

    pdf.drawImage("graphs/ros.png", x, y - img_height, width=img_width, height=img_height)
    y -= (img_height + 20)

    pdf.drawImage("graphs/vol.png", x, y - img_height, width=img_width, height=img_height)
    y -= (img_height + 20)

    pdf.save()




