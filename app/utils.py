import base64
import io
import json
import os
import re
import sqlite3

import matplotlib
import matplotlib.pyplot as plt
from docx import Document
from fpdf import FPDF
from openai import OpenAI
from pdfminer.high_level import extract_text
from wordcloud import WordCloud

from app.config import DATABASE
from app.prompt import COVER_LETTER_PROMPT, JOB_DESCRIPTION_PROMPT

matplotlib.use("Agg")  # Use a non-GUI backend


def read_resume(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".docx":
        doc = Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    elif file_extension == ".pdf":
        text = extract_text(file_path)
        return text
    else:
        raise ValueError("Unsupported file format")


def save_cover_letter(company_name, job_title, cover_letter_content):
    company_name = re.sub(r"[^a-zA-Z]", "", company_name)
    job_title = re.sub(r"[^a-zA-Z]", "", job_title)
    cover_letter_body = "\n".join(cover_letter_content.split("\n"))
    output_dir = "data/cover_letter"
    backup_dir = "C:/Users/Steven/Documents/Resume/Cover letter/Pdf"
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"cover_letter_{company_name}_{job_title}.pdf"
    file_path = os.path.join(output_dir, file_name)
    backup_file_path = os.path.join(backup_dir, file_name)
    pdf = FPDF()
    pdf.add_page()
    margin = 20
    pdf.set_auto_page_break(auto=True, margin=margin)
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)
    num_lines = len(cover_letter_body.split("\n"))
    line_height = 10
    page_height = 260 - 2 * margin
    font_size = 12
    while num_lines * line_height > page_height and font_size > 1:
        font_size -= 1
        line_height = font_size * 0.8
    pdf.set_font("Times", size=font_size)
    cover_letter_body = cover_letter_body.encode("utf-8", "ignore").decode(
        "latin1", "ignore"
    )
    pdf.multi_cell(0, line_height, cover_letter_body)
    pdf.output(file_path)
    try:
        pdf.output(backup_file_path)
    except FileNotFoundError:
        print("Backup file path not found")


def generate_job_event_data(job_description, gpt_model="gpt-4o"):
    client = OpenAI()
    resume_folder = os.path.join("data", "resume")
    resume_files = [
        f for f in os.listdir(resume_folder) if f.endswith((".docx", ".pdf"))
    ]

    if not resume_files:
        raise FileNotFoundError("No resume files found in the data/resume folder.")

    resume_path = os.path.join(resume_folder, resume_files[0])
    resume_text = read_resume(resume_path)

    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": f"{JOB_DESCRIPTION_PROMPT} /n {COVER_LETTER_PROMPT} /n {resume_text}",
            },
            {"role": "user", "content": job_description},
        ],
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )

    if (
        response.choices
        and response.choices[0].message
        and response.choices[0].message.content
    ):
        data = json.loads(response.choices[0].message.content.strip())
        return data
    else:
        raise ValueError("Invalid response from OpenAI API")


def generate_plots():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Query to get the total amount of jobs applied grouped by days
        cursor.execute(
            """
            SELECT date(date_created), COUNT(*) 
            FROM job_events 
            GROUP BY date(date_created)
        """
        )
        jobs_by_day = cursor.fetchall()
        # Query to get the breakdown of amount jobs applied by company
        cursor.execute(
            """
            SELECT company_name, COUNT(*) 
            FROM job_events 
            GROUP BY company_name
        """
        )
        jobs_by_company = cursor.fetchall()
        # Query to get the tech stack data
        cursor.execute(
            """
            SELECT tech_stack 
            FROM job_events
        """
        )
        tech_stack_data = cursor.fetchall()

    # Plot total amount of jobs applied grouped by days
    dates, counts = zip(*jobs_by_day)
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker="o")
    plt.title("Total Jobs Applied by Day")
    plt.xlabel("Date")
    plt.ylabel("Number of Jobs")
    plt.xticks(rotation=45)
    plt.tight_layout()
    img1 = io.BytesIO()
    plt.savefig(img1, format="png")
    img1.seek(0)
    img1_base64 = base64.b64encode(img1.getvalue()).decode()

    # Plot breakdown of amount jobs applied by company
    companies, counts = zip(*jobs_by_company)
    plt.figure(
        figsize=(10, len(companies) * 0.5)
    )  # Adjust figure height based on number of companies
    plt.barh(companies, counts)  # Change to horizontal bar plot
    plt.title("Jobs Applied by Company")
    plt.xlabel("Number of Jobs")
    plt.ylabel("Company")
    plt.tight_layout()
    plt.subplots_adjust(
        left=0.3
    )  # Adjust left margin to add more space for company names
    img2 = io.BytesIO()
    plt.savefig(img2, format="png")
    img2.seek(0)
    img2_base64 = base64.b64encode(img2.getvalue()).decode()

    # Generate word cloud for tech stack
    tech_stack_text = " ".join([tech for tech, in tech_stack_data if tech])
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        tech_stack_text
    )
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    img3 = io.BytesIO()
    plt.savefig(img3, format="png")
    img3.seek(0)
    img3_base64 = base64.b64encode(img3.getvalue()).decode()

    return img1_base64, img2_base64, img3_base64
