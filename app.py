import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
DATABASE = 'database.db'

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize database (run once to create table)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT,
                company_name TEXT,
                job_description TEXT,
                cover_letter TEXT,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Helper function to fetch data from database
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv

# Route to create a new job application event
@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        job_title = request.form['job_title']
        company_name = request.form['company_name']
        job_description = request.form['job_description']

        # Generate cover letter using OpenAI API
        cover_letter = generate_cover_letter(job_description)

        # Insert into database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_events (job_title, company_name, job_description, cover_letter)
                VALUES (?, ?, ?, ?)
            ''', (job_title, company_name, job_description, cover_letter))
            conn.commit()

        return redirect(url_for('index'))
    return render_template('add_event.html')

# Route to view all job applications
@app.route('/')
def index():
    job_events = query_db('SELECT id, job_title, company_name, date_created FROM job_events')
    return render_template('index.html', job_events=job_events)

# Route to fetch and display a specific cover letter
@app.route('/cover_letter/<int:event_id>')
def view_cover_letter(event_id):
    job_event = query_db('SELECT * FROM job_events WHERE id = ?', [event_id], one=True)
    return render_template('view_cover_letter.html', job_event=job_event)

# Function to call OpenAI API and generate cover letter
def generate_cover_letter(job_description):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Write a cover letter for the following job description:\n\n{job_description}",
        max_tokens=250
    )
    return response.choices[0].text.strip()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
