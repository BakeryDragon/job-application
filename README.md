# job-application

An interface to automate the process for applying jobs.

## Prerequisites

- Python 3.8 or higher
- pip

## Setup

1. Clone the Repository

   git clone https://github.com/BakeryDragon/job-application.git
   cd job-application

2. Create a Virtual Environment

   python -m venv .venv

3. Activate the Virtual Environment

   - On Windows:
     .\.venv\Scripts\activate
   - On macOS/Linux:
     source .venv/bin/activate

4. Install Dependencies

   pip install -r requirements.txt

5. Set Up Environment Variables

   Create a .env file in the root directory of the project and add the following environment variables:

   OPENAI_API_KEY=your_openai_api_key
   BACKUP_DIR=path_to_backup_directory

6. Run the Application

   make start

   The application will be available at http://127.0.0.1:5000.

## Usage

### Adding a Job Application

1. Navigate to http://127.0.0.1:5000/add.
2. Fill in the job description and select the GPT model.
3. Click "Add Event" to save the job application.

### Viewing Job Applications

1. Navigate to http://127.0.0.1:5000/.
2. You will see a list of job applications with options to view cover letters and delete entries.

### Viewing Plots

1. Navigate to http://127.0.0.1:5000/plots.
2. You will see various plots related to your job applications.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.