import sqlite3

from flask import Blueprint, redirect, render_template, request, url_for
from openai import OpenAI

from config import DATABASE
from database import query_db
from models import JobEventData
from utils import generate_job_event_data, generate_plots, save_cover_letter

routes = Blueprint("routes", __name__)
client = OpenAI()


@routes.route("/")
def index():
    job_events = query_db(
        "SELECT id, job_title, company_name, tech_stack, job_duty_summary, date_posted, date_created FROM job_events"
    )
    total_jobs = len(job_events)
    return render_template("index.html", job_events=job_events, total_jobs=total_jobs)


@routes.route("/add", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        job_description = request.form["job_description"]
        gpt_model = request.form["gpt_model"]
        job_event_data = generate_job_event_data(job_description, gpt_model)
        job_event = JobEventData(**job_event_data)
        job_title = job_event.job_title
        company_name = job_event.company_name
        cover_letter = job_event.cover_letter
        tech_stack = ",".join(job_event.tech_stack) if job_event.tech_stack else None
        job_duty_summary = job_event.job_duty_summary
        date_posted = job_event.date_posted
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
        return redirect(url_for("routes.index"))
    return render_template("add_event.html")


@routes.route("/cover_letter/<int:event_id>")
def view_cover_letter(event_id):
    job_event = query_db("SELECT * FROM job_events WHERE id = ?", [event_id], one=True)
    return render_template("view_cover_letter.html", job_event=job_event)


@routes.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_events WHERE id = ?", (event_id,))
        conn.commit()
    return redirect(url_for("routes.index"))


@routes.route("/plots")
def plots():
    img1_base64, img2_base64, img3_base64 = generate_plots()
    return render_template(
        "plots.html",
        img1_base64=img1_base64,
        img2_base64=img2_base64,
        img3_base64=img3_base64,
    )
