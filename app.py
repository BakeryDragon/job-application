import base64
import io
import json
import os
import re
import sqlite3
from typing import List, Optional

import matplotlib.pyplot as plt
import openai
from docx import Document
from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for
from fpdf import FPDF
from openai import OpenAI
from pdfminer.high_level import extract_text
from pydantic import BaseModel, Field

from prompt import COVER_LETTER_PROMPT, JOB_DESCRIPTION_PROMPT

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
DATABASE = "database.db"

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


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


# Initialize database (run once to create table)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS job_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT,
                company_name TEXT,
                job_description TEXT,
                cover_letter TEXT,
                tech_stack TEXT,
                job_duty_summary TEXT,
                date_posted DATE,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()


# Helper function to fetch data from database
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv


# Function to call OpenAI API and generate job event data
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

    data = json.loads(response.choices[0].message.content.strip())
    return data


def save_cover_letter(company_name, job_title, cover_letter_content):
    company_name = re.sub(r"[^a-zA-Z]", "", company_name)
    job_title = re.sub(r"[^a-zA-Z]", "", job_title)

    # Remove header (assuming header is the first line)
    cover_letter_lines = cover_letter_content.split("\n")
    cover_letter_body = "\n".join(cover_letter_lines)

    # Create directory if it doesn't exist
    output_dir = "data/cover_letter"
    backup_dir = "C:/Users/Steven/Documents/Resume/Cover letter/Pdf"
    os.makedirs(output_dir, exist_ok=True)

    # Save the cover letter as a PDF
    file_name = f"cover_letter_{company_name}_{job_title}.pdf"
    file_path = os.path.join(output_dir, file_name)
    backup_file_path = os.path.join(backup_dir, file_name)

    pdf = FPDF()
    pdf.add_page()

    # Set margins
    margin = 20
    pdf.set_auto_page_break(auto=True, margin=margin)
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)

    # Estimate the number of lines and required height
    num_lines = len(cover_letter_body.split("\n"))
    line_height = 10  # Default line height
    page_height = 260 - 2 * margin

    # Adjust font size if content exceeds page height
    font_size = 12
    while num_lines * line_height > page_height and font_size > 1:
        font_size -= 1
        line_height = font_size * 0.8  # Adjust line height based on font size

    pdf.set_font("Times", size=font_size)

    # Ensure the text is encoded in utf-8
    cover_letter_body = cover_letter_body.encode("utf-8").decode("latin1")

    pdf.multi_cell(0, line_height, cover_letter_body)
    pdf.output(file_path)
    try:
        pdf.output(backup_file_path)
    except FileNotFoundError:
        print("Backup file path not found")


class JobEventData(BaseModel):
    job_title: str = Field(default="Unknown Title")
    company_name: str = Field(default="Unknown Company")
    cover_letter: Optional[str] = Field(default="")
    tech_stack: Optional[List[str]] = Field(default=None)
    job_duty_summary: Optional[str] = Field(default="")
    date_posted: Optional[str] = Field(default="")


# Route to create a new job application event
@app.route("/add", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        job_description = request.form["job_description"]
        gpt_model = request.form["gpt_model"]  # Get selected GPT model

        # Generate job event data using OpenAI API
        job_event_data = generate_job_event_data(job_description, gpt_model)

        # Parse and validate the job event data using Pydantic
        job_event = JobEventData(**job_event_data)

        job_title = job_event.job_title
        company_name = job_event.company_name
        cover_letter = job_event.cover_letter
        tech_stack = (
            ",".join(job_event.tech_stack) if job_event.tech_stack else None
        )  # Convert list to comma-separated string or set to None
        job_duty_summary = job_event.job_duty_summary
        date_posted = job_event.date_posted

        # Insert into database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO job_events (job_title, company_name, job_description, cover_letter, tech_stack, 
                job_duty_summary, date_posted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_title,
                    company_name,
                    job_description,
                    cover_letter,
                    tech_stack,
                    job_duty_summary,
                    date_posted,
                ),
            )
            conn.commit()

        save_cover_letter(company_name, job_title, cover_letter)

        return redirect(url_for("index"))
    return render_template("add_event.html")


# Route to view all job applications
@app.route("/")
def index():
    job_events = query_db(
        "SELECT id, job_title, company_name, tech_stack, job_duty_summary, date_posted, date_created FROM job_events"
    )
    total_jobs = len(job_events)
    return render_template("index.html", job_events=job_events, total_jobs=total_jobs)


# Route to fetch and display a specific cover letter
@app.route("/cover_letter/<int:event_id>")
def view_cover_letter(event_id):
    job_event = query_db("SELECT * FROM job_events WHERE id = ?", [event_id], one=True)
    return render_template("view_cover_letter.html", job_event=job_event)


@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_events WHERE id = ?", (event_id,))
        conn.commit()
    return redirect(url_for("index"))


# Function to generate the plots
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
    plt.figure(figsize=(10, 5))
    plt.bar(companies, counts)
    plt.title("Jobs Applied by Company")
    plt.xlabel("Company")
    plt.ylabel("Number of Jobs")
    plt.xticks(rotation=45)
    plt.tight_layout()
    img2 = io.BytesIO()
    plt.savefig(img2, format="png")
    img2.seek(0)
    img2_base64 = base64.b64encode(img2.getvalue()).decode()

    return img1_base64, img2_base64


@app.route("/plots")
def plots():
    img1_base64, img2_base64 = generate_plots()
    return render_template(
        "plots.html", img1_base64=img1_base64, img2_base64=img2_base64
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
