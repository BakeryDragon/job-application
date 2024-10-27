JOB_DESCRIPTION_PROMPT = """
Generate job event data including job_title, company_name, job_description, cover_letter, tech_stack, job_duty_summary, and date_posted 
based on the provided job description. If you don't find the information in the given job description, just output none.
tech_stack is a list of technologies or skills required for the job. If none found, output an empty list. 
Output the data in JSON format.
"""

COVER_LETTER_PROMPT = """
Here is detailed instructions for generating a cover letter for a job application.
Generate a personalized cover letter based on the provided job description and resume. Additionally, create a suitable file name for archiving the cover letter.

# Steps

1. Analyze the job description to identify key skills, qualifications, and experiences required for the position.
2. Review the uploaded resume to extract relevant experiences, accomplishments, and skills that match the job description.
3. Write a cover letter that highlights the candidate's strengths, experiences, and suitability for the job, ensuring it is tailored specifically to the position.
4. Generate a file name for the cover letter using the format: `companyName_positionName`.

# Output Format

The output should be in JSON format with the following fields:
- `"cover_letter"`: A detailed and personalized cover letter with form that is easily migrated to Microsoft Word.
- `"file_name"`: A string representing the file name, formatted as `companyName_positionName_jobDate`.

# Notes

- Ensure the cover letter is concise and well-structured, typically in 3-4 paragraphs explaining the candidate's fit for the role.
- The company name and position name should be extracted from the job description for creating the file name.
- Check for common cover letter requirements: introduction, relevant experiences, match with company goals/values, and a closing statement.
- Make sure all information is provided. Don't left optional fields for further edit.

The following is my resume:
"""
