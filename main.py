# RUNS 1+ AGENTS SIMULTANEOUSLY 
# For loop: Creating an agent for each url and then adding it to an agent lsit.
# Then running three agents at a time simultaneously.

from browser_use.llm import ChatOpenAI
# from browser_use.llm import ChatAnthropic
# from browser_use.llm import ChatGoogle

from clients import *
from resume_upload import *
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import os
import sys

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

url_path = Path.cwd() / "Job Postings/20 URLs.csv" # CSV of Job Posting URLs
with open(url_path, 'r') as f:
    reader = csv.reader(f)
    urls = list(reader)
    urls = urls[1:] # removing first row containing title "Url"

async def main():  

    # CSV creation for application results
    data = [["URL", "Submitted", "Result"]]
    filename = "Test-GPT-5-mini_Results.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data) # Write all rows at once

    llm = ChatOpenAI(
            model='gpt-5-mini',
            temperature=1,
            # reasoning_effort='low',
            base_url='https://api.openai.com/v1',
            max_retries=3
        )
    
    # Creating agents per url
    agent_list = []
    i = 1
    for url in urls[1:]:
        url = url[0] # url in urls is a list containing just the one link. Indexing "0" to get the link inside it.

        initial_actions = [{'go_to_url': {'url':  str(url)}},]

        task = f""" Fill out this job applications: {url} """

        extend_system_message = f"""

            Follow these instructions carefully:

            ------------------------------
            * General Rules:
            ------------------------------
            1. Use the following client information tofill out the job application fields as they are presented on screen: {client}
            2. If prompted: Accept all cookies.
            3. If an "Apply" or "Apply manually" button is present:
                - Click it immediately, always choosing "Apply manually" if available.
                - If a new tab opens after clicking, move focus to the just opened tab.
            4. After any page finishes loading (including new tabs, navigated forms, and login redirects):
                - Wait 5 full seconds before taking any actions, including DOM evaluation, clicking, typing, or scrolling.
            5. Fill out form fields **in the order they appear on the webpage**, not based on the order of keys in the client dictionary.
      
            ------------------------------
            * Filling Out Fields:
            ------------------------------			
            1. For each field:
                - If the label/aria-label/id matches a key in the client dictionary:
                    - If the field is empty, insert the corresponding value.
                    - If the field contains a different value, replace it with the correct value.
                - If no matching key is found:
                    - If field is required, answer with "N/A" or "No".
                        - If field does not allow "N/A" or "No", generate answer based on client info.
            2. For drop-down/select type fields:
                - First, select the field and then type the correct value into the field.
                - Then, click the index in the drop-down menu that best matches the correct value.
                    - If value does not show up, scroll down the element's drop-down menu until value is shown.
            3. When answering the question "How did you hear about us?" or one that is similar:
                - Always select through corporate/company website
                - If company/corporate website is not an option, select one of the following: LinkedIn, Indeeed, or Glassdoor
            4. If all necessary fields on the screen are filled:
                - scroll to find more elements or move to next page of application.
            5. When scrolling, scroll up/down in increments of 500 pixels or less only.
                - If no element is presented on screen, scroll down as much as needed until it is presented.
                
            ------------------------------------
            * Account Creation / Sign-in Logic:
            ------------------------------------
            1. Always attempt to create an account first using {username} and {password} 
            2. If the account already exists, sign in using the same credentials.

            --------------------
            * Resume Handling:
            --------------------
            1. On every page, actively search for file upload elements.
            2. Always use the "upload_resume" function to upload the resume to the associated upload element.
            3. For each:
                - Check the label, nearby text, inner text, or surrounding container for keywords like:
                    - "Resume", "CV", "Curriculum Vitae", "Upload Resume", "Upload your resume", "Choose File", "Select File", "Upload File", "Attach", "Attachment"
                - If keywords are found, use the "upload_resume" function on that element's index to upload the resume.

            --------------------------
            * Work History Guidelines:
            --------------------------
            1. If a job's end date is marked as "current":
                - Select the appropriate element to indicate that the client is currently at the job.
                - If the form lacks a "current" option, leave the field blank or enter today's date if required.

            ----------------
            * Task Completion:
            ----------------
            Only end the task if:
                - Before submitting, went back and checked entire page to makee sure all required fileds were filled and filled with appropriate value.
                - The application is clearly submitted after clicking "Submit" and a confirmation page is presented, OR
                - A required field cannot be filled, preventing further progress.
                - If entire browser was manually closed by human.
        """
        
        agent = Agent(
            task=task,
            extend_system_message=extend_system_message,
            initial_actions=initial_actions,
            llm=llm,
            # sensitive_data=sensitive_data,
            use_vision=True,
            controller=controller,
            browser_session=BrowserSession(user_data_dir=f"~/.config/browseruse/profiles/session_{i}", allowed_domains=['https://*'], viewport={'width': 100, 'height': 100}),
            vision_detail_level="low"
        )

        agent_list.append(agent)
        i = i + 1

    batch_size = 1 # Number of agents running simultaneously at a time.
    index = 0
    x = 0
    if ((len(agent_list))%batch_size) > 0: 
        x = 1
    # for i in range(1,((len(agent_list))//batch_size) + x):
    for i in range(1,2):
        results = await asyncio.gather(*[agent.run(max_steps = 70) for agent in agent_list[(i-1)*batch_size : min(i*batch_size , len(agent_list))]])	

        for result in results:
            if result.is_successful():
                submitted = "Success"
            else:
                submitted = 'Failed'

            url_result = [urls[index][0], submitted, result.history[-1].result[-1].extracted_content]
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(url_result)
            index = index + 1
    
if __name__ == '__main__':
    asyncio.run(main())