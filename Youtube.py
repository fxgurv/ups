import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager

# Constants
YOUTUBE_TEXTBOX_ID = "textbox"
YOUTUBE_NEXT_BUTTON_ID = "next-button"
YOUTUBE_DONE_BUTTON_ID = "done-button"
YOUTUBE_RADIO_BUTTON_XPATH = "//*[@id=\"radioLabel\"]"
YOUTUBE_MADE_FOR_KIDS_NAME = "VIDEO_MADE_FOR_KIDS_MFK"
YOUTUBE_NOT_MADE_FOR_KIDS_NAME = "VIDEO_MADE_FOR_KIDS_NOT_MFK"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_url(video_id):
    return f"https://www.youtube.com/watch?v={video_id}"

def read_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip().split('\n\n')
        title = content[0]
        description = '\n\n'.join(content[1:3])
        return title, description

def upload_video(fp_profile_path, video_path, title, description, verbose=True):
    if not os.path.exists(video_path):
        logging.error("Video file does not exist.")
        return None

    options = Options()
    options.add_argument("-profile")
    options.add_argument(fp_profile_path)

    # Uncomment the following line to run in headless mode
    # options.add_argument("--headless")

    # Initialize WebDriver
    try:
        service = Service(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=service, options=options)
    except WebDriverException as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        return None

    try:
        logging.info("Navigating to YouTube Studio to get Channel ID")
        browser.get("https://studio.youtube.com")
        WebDriverWait(browser, 20).until(EC.url_contains("studio.youtube.com"))
        channel_id = browser.current_url.split("/")[-1]
        logging.info(f"Retrieved Channel ID: {channel_id}")

        logging.info("Navigating to YouTube upload page")
        browser.get("https://www.youtube.com/upload")
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, "ytcp-uploads-file-picker")))

        logging.info("Uploading video")
        file_picker = browser.find_element(By.TAG_NAME, "ytcp-uploads-file-picker")
        file_input = file_picker.find_element(By.TAG_NAME, "input")
        file_input.send_keys(video_path)
        time.sleep(5)  # Wait for the file to be uploaded

        logging.info("Setting video title and description")
        WebDriverWait(browser, 20).until(EC.presence_of_all_elements_located((By.ID, YOUTUBE_TEXTBOX_ID)))
        textboxes = browser.find_elements(By.ID, YOUTUBE_TEXTBOX_ID)
        
        # Clear and set title
        title_box = textboxes[0]
        title_box.clear()
        title_box.send_keys(title)
        time.sleep(3)  # Short wait after setting the title
        
        # Set description
        description_box = textboxes[1]
        description_box.send_keys(description)
        time.sleep(3)  # Short wait after setting the description

        # Set `made for kids` option
        logging.info("Setting `made for kids` option")
        try:
            is_not_for_kids_checkbox = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.NAME, YOUTUBE_NOT_MADE_FOR_KIDS_NAME))
            )
            is_not_for_kids_checkbox.click()
        except TimeoutException:
            logging.warning("Could not find 'NOT_MADE_FOR_KIDS' checkbox. Trying alternative method.")
            try:
                not_for_kids_label = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
                )
                not_for_kids_label.click()
            except TimeoutException:
                logging.error("Failed to set 'made for kids' option. Continuing with upload.")

        logging.info("Set video as not made for kids")
        time.sleep(3)  # Short wait after setting the kids option

        # Click through additional steps
        logging.info("Clicking through additional steps")
        for _ in range(3):
            try:
                next_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, YOUTUBE_NEXT_BUTTON_ID)))
                next_button.click()
                time.sleep(3)
            except TimeoutException:
                logging.warning(f"Next button not found on step {_+1}. Continuing to next step.")

        # Set video visibility to unlisted
        logging.info("Setting video visibility to unlisted")
        try:
            WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, YOUTUBE_RADIO_BUTTON_XPATH)))
            radio_buttons = browser.find_elements(By.XPATH, YOUTUBE_RADIO_BUTTON_XPATH)
            if len(radio_buttons) >= 2:
                browser.execute_script("arguments[0].scrollIntoView(true);", radio_buttons[1])
                radio_buttons[1].click()  # Select the second radio button for unlisted
            else:
                logging.warning("Could not find the correct radio button for unlisted visibility.")
        except TimeoutException:
            logging.error("Failed to set video visibility. Continuing with upload.")

        time.sleep(3)  # Short wait after setting visibility

        logging.info("Finalizing upload")
        try:
            done_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, YOUTUBE_DONE_BUTTON_ID)))
            done_button.click()
            time.sleep(5)  # Wait for the upload to finalize
        except TimeoutException:
            logging.error("Could not find the 'Done' button. Upload may not have completed successfully.")

        # Get the latest uploaded video URL
        browser.get(f"https://studio.youtube.com/channel/{channel_id}/videos/short")
        time.sleep(2)
        videos = browser.find_elements(By.TAG_NAME, "ytcp-video-row")
        first_video = videos[0]
        anchor_tag = first_video.find_element(By.TAG_NAME, "a")
        href = anchor_tag.get_attribute("href")
        video_id = href.split("/")[-2]

        # Build URL
        url = build_url(video_id)

        if verbose:
            logging.info(f"Uploaded Video: {url}")

        return url

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if 'browser' in locals():
            browser.quit()

# Define your parameters
profile_path = r"C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\me97qgzd.default-release"
video_path = r"C:\Users\user\Desktop\UPLOADERS\1.mp4"
metadata = r"C:\Users\user\Desktop\UPLOADERS\1.txt"

# Read video metadata
title, description = read_metadata(metadata)

# Upload video
youtube_url = upload_video(profile_path, video_path, title, description)