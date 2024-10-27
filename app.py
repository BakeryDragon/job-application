import json
import os
import sqlite3

import openai
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from openai import OpenAI
from docx import Document
from prompt import COVER_LETTER_PROMPT, JOB_DESCRIPTION_PROMPT

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
DATABASE = "database.db"

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def read_resume(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


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
    resume_text = read_resume("data/resume/Resume_JIAWEI_ZHANG_raw.docx")

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


# Route to create a new job application event
@app.route("/add", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        job_description = request.form["job_description"]
        gpt_model = request.form["gpt_model"]  # Get selected GPT model

        # Generate job event data using OpenAI API
        job_event_data = generate_job_event_data(job_description, gpt_model)

        job_title = job_event_data["job_title"]
        company_name = job_event_data["company_name"]
        cover_letter = job_event_data["cover_letter"]
        tech_stack = (
            ",".join(job_event_data["tech_stack"])
            if job_event_data["tech_stack"]
            else None
        )  # Convert list to comma-separated string or set to None
        job_duty_summary = job_event_data["job_duty_summary"]
        date_posted = job_event_data["date_posted"]

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

        return redirect(url_for("index"))
    return render_template("add_event.html")


# Route to view all job applications
@app.route("/")
def index():
    job_events = query_db(
        "SELECT id, job_title, company_name, tech_stack, job_duty_summary, date_posted, date_created FROM job_events"
    )
    return render_template("index.html", job_events=job_events)


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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
