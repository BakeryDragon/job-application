JOB_DESCRIPTION_PROMPT = """
Generate job event data including job_title, company_name, job_description, cover_letter, tech_stack, job_duty_summary, and date_posted 
based on the provided job description. If you don't find the information in the given job description, just output none.
tech_stack is a list of technologies or skills required for the job. If none found, output an empty list. 
Output the data in JSON format.
"""

COVER_LETTER_PROMPT = """
Generate a personalized cover letter for a job application based on the provided job description and resume. Additionally, create a suitable file name for archiving the cover letter.

# Steps

1. **Analyze the Job Description**: Identify key skills, qualifications, and experiences that are required for the position.
2. **Review the Resume**: Extract relevant experiences, accomplishments, and skills that align with the job description.
3. **Compose the Cover Letter**: Draft a personalized cover letter highlighting the candidate's strengths, experiences, and suitability for the job. The letter should be specifically tailored to the position, adhering to common cover letter structures such as introduction, relevant experiences, alignment with company goals and values, and a formal closing.
4. **Generate the File Name**: Create a file name for the cover letter using the format `companyName_positionName`.

# Output Format

The output should be in JSON format with the following fields:
- `"cover_letter"`: A detailed and personalized cover letter that is formatted for easy migration to Microsoft Word, structured in 3-4 paragraphs.
- `"file_name"`: A string representing the file name, formatted as `companyName_positionName_jobDate`, where the company name and position name should be derived from the job description.

# Notes

- The cover letter should be concise and well-structured, typically comprising 3-4 paragraphs.
- Ensure the cover letter includes the following components: introduction, relevant work experiences, connection with company goals/values, and a closing statement.
- Extract the company name and position name from the job description to output the file name.
- Avoid leaving placeholders for items such as company name or date; provide complete details as rendered from the job description and resume.

Following is my resume:
"""
