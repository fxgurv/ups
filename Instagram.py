import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def remove_non_bmp_characters(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def read_description(file_path):
    logger.info(f"Reading description from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    cleaned_text = remove_non_bmp_characters(text)
    logger.info(f"Description read and cleaned: {cleaned_text[:50]}...")
    return cleaned_text

def setup_firefox_profile(profile_path):
    logger.info(f"Setting up Firefox profile from {profile_path}")
    options = Options()
    options.add_argument("-profile")
    options.add_argument(profile_path)
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    logger.info("Firefox browser initialized with custom profile")
    return driver

def click_next_button(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Next']"))
        )
        next_button.click()
        logger.info("'Next' button clicked successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to find and click 'Next' button: {e}")
        return False

def upload_video(driver, video_path, description):
    logger.info("Starting video upload process")
    driver.get("https://www.instagram.com/")
    logger.info("Navigated to Instagram homepage")

    try:
        logger.info("Attempting to click 'New post' button")
        new_post_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='New post']"))
        )
        new_post_button.click()
        logger.info("'New post' button clicked successfully")
    except Exception as e:
        logger.error(f"New post button click failed: {e}")
        return
    
    try:
        logger.info(f"Attempting to upload video file: {video_path}")
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        file_input.send_keys(video_path)
        logger.info("Video file uploaded successfully")
    except Exception as e:
        logger.error(f"File input send keys failed: {e}")
        return
    
    time.sleep(15)  # Wait for video processing

    try:
        logger.info("Attempting to select crop options")
        crop_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[name()='svg' and @aria-label='Select crop']"))
        )
        crop_button.click()
        logger.info("Crop button clicked")

        portrait_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[name()='svg' and @aria-label='Crop portrait icon']"))
        )
        portrait_button.click()
        logger.info("Portrait crop option selected")
    except Exception as e:
        logger.error(f"Crop selection failed: {e}")

    try:
        logger.info("Proceeding to next steps")
        if not click_next_button(driver) or not click_next_button(driver):
            raise Exception("Failed to click 'Next' buttons")
        
        logger.info("Entering video description")
        description_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='Write a caption...']"))
        )
        description_input.send_keys(description)
        logger.info("Description entered successfully")
        
        logger.info("Attempting to share the post")
        share_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Share']"))
        )
        share_button.click()
        logger.info("Share button clicked")
    except Exception as e:
        logger.error(f"Post sharing failed: {e}")
        return
    
    try:
        logger.info("Waiting for upload success message")
        WebDriverWait(driver, 120).until(
            lambda driver: driver.execute_script(
                "return document.body.innerText.includes('Your reel has been shared.');"
            )
        )
        logger.info("Upload success message detected. Upload process completed.")
    except Exception as e:
        logger.error(f"Failed to detect upload success message: {e}")

def main(profile_path, video_path, metadata_path):
    logger.info("Starting main process")
    description = read_description(metadata_path)
    driver = setup_firefox_profile(profile_path)

    try:
        upload_video(driver, video_path, description)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        logger.info("Closing the browser")
        driver.quit()

if __name__ == "__main__":
    profile_path = r"C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\me97qgzd.default-release"
    video_path = r"C:\Users\user\Desktop\UPLOADERS\2.mp4"
    metadata_path = r"C:\Users\user\Desktop\UPLOADERS\1.txt"
    
    main(profile_path, video_path, metadata_path)
    logger.info("Script execution completed")