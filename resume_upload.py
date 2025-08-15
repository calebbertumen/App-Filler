from browser_use import ActionResult, BrowserSession, Controller
from pathlib import Path
import logging
import pyautogui
import time

logger = logging.getLogger(__name__)
CV = Path.cwd() / "Client Info/Test_Resume.pdf"
path = str(CV.absolute())

def open_finder_and_upload(): #uploading resume using finder
    print('Running: upload_resume_finder function')
    time.sleep(3)
    pyautogui.doubleClick(x=787, y=646)  # move to x, y, then click the left mouse button.
    time.sleep(3)
    pyautogui.hotkey('command', 'shift', 'g')
    time.sleep(3)
    pyautogui.write(path)
    time.sleep(3)
    pyautogui.press('return')
    time.sleep(3)
    pyautogui.press('return')
    return

controller = Controller()
@controller.action('Upload resume if label or element suggests resume or CV')
async def upload_resume(index: int, browser_session: BrowserSession):
    print("RUNNING: UPLOAD_RESUME FUNCTION")

    file_upload_dom_el = await browser_session.find_file_upload_element_by_index(index)

    if file_upload_dom_el is None:
        logger.info(f'No file upload element found at ind   ex {index}')
        return ActionResult(error=f'No file upload element found at index {index}')
    
    file_upload_el = await browser_session.get_locate_element(file_upload_dom_el)

    if file_upload_el is None:
        msg = f'No file upload element found at index {index}'
        logger.info(msg)
        return ActionResult(error=msg)

    try:
        await file_upload_el.set_input_files(path)
        # print("RUNNING: OPEN FINDER AND UPLOAD FUNCTION")
        # await file_upload_el.click()
        # await open_finder_and_upload()
        msg = f'Successfully uploaded file to index {index}'
        logger.info(msg)
        return ActionResult(extracted_content=msg, include_in_memory=True)
    except Exception as e:
        msg = f'Failed to upload file to index {index}: {str(e)}'
        logger.info(msg)
        return ActionResult(error=msg)



    

    

