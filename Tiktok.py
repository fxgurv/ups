import os
import logging
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotInteractableException
from webdriver_manager.firefox import GeckoDriverManager

# Constants
TIKTOK_UPLOAD_URL = "https://www.tiktok.com/upload"
TIKTOK_FILE_INPUT_XPATH = "//input[@type='file']"
TIKTOK_CAPTION_XPATH = "//div[contains(@class, 'DraftEditor-editorContainer')]//div[contains(@class, 'public-DraftEditor-content')]"
TIKTOK_UPLOADED_TEXT_XPATH = "//span[text()='Uploaded']"
TIKTOK_POST_BUTTON_XPATH = "//button[contains(@class, 'TUXButton') and .//div[text()='Post']]"
TIKTOK_UPLOAD_SUCCESS_XPATH = "//div[text()='Your video has been uploaded']"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_video(fp_profile_path, video_path, title):
    if not os.path.exists(video_path):
        logging.error("Video file does not exist.")
        return None

    options = Options()
    options.add_argument("-profile")
    options.add_argument(fp_profile_path)
    options.add_argument("--headless")

    try:
        service = Service(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=service, options=options)
    except WebDriverException as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        return None

    try:
        tiktok_url = upload_to_tiktok(browser, video_path, title)
        logging.info(f"Uploaded Video to TikTok: {tiktok_url}")
        return tiktok_url

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    finally:
        if 'browser' in locals():
            browser.quit()

def upload_to_tiktok(browser, video_path, caption):
    logging.info("Navigating to TikTok upload page")
    browser.get(TIKTOK_UPLOAD_URL)
    
    try:
        file_input = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, TIKTOK_FILE_INPUT_XPATH))
        )
        logging.info("Uploading video to TikTok")
        file_input.send_keys(video_path)

        logging.info("Waiting for caption input to be interactable")
        caption_input = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, TIKTOK_CAPTION_XPATH))
        )
        
        logging.info("Setting video caption")
        try:
            caption_input.click()
            ActionChains(browser).move_to_element(caption_input).send_keys(caption).perform()
        except ElementNotInteractableException:
            try:
                browser.execute_script("arguments[0].textContent = arguments[1];", caption_input, caption)
            except:
                ActionChains(browser).move_to_element(caption_input).click().send_keys(caption).perform()

        logging.info("Waiting for 'Uploaded' text")
        try:
            WebDriverWait(browser, 60).until(
                EC.presence_of_element_located((By.XPATH, TIKTOK_UPLOADED_TEXT_XPATH))
            )
        except Exception as e:
            logging.error(f"Failed to find 'Uploaded' text: {e}")

        logging.info("Waiting for post button to be clickable")
        try:
            post_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, TIKTOK_POST_BUTTON_XPATH))
            )
            post_button.click()
            logging.info("Clicked post button")
        except Exception as e:
            logging.error(f"Post sharing failed: {e}")

        logging.info("Waiting for upload success message")
        try:
            WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH, TIKTOK_UPLOAD_SUCCESS_XPATH))
            )
            logging.info("Upload completed successfully")
            return browser.current_url
        except Exception as e:
            logging.error(f"Failed to detect upload success message: {e}")

    except TimeoutException as e:
        logging.error(f"Timeout occurred while interacting with TikTok: {e}")
    except Exception as e:
        logging.error(f"Error during TikTok upload: {e}")
    
    return None

# Define your parameters
profile_path = r"C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\me97qgzd.default-release"
video_path = r"C:\Users\user\Desktop\TEST\1.mp4"
metadata = "r"C:\Users\user\Desktop\TEST\1.txt"

tiktok_url = upload_video(profile_path, video_path, metadata)