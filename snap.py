import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_firefox_profile(profile_path):
    logger.info(f"Setting up Firefox profile from {profile_path}")
    options = Options()
    options.add_argument("-profile")
    options.add_argument(profile_path)
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    logger.info("Firefox browser initialized with custom profile")
    return driver

def read_description(file_path):
    logger.info(f"Reading description from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        description = file.readline().strip()
    logger.info(f"Description read: {description[:50]}...")
    return description

def upload_video(driver, video_path, description):
    logger.info("Starting Snapchat upload process")
    
    try:
        driver.get('https://my.snapchat.com/')
        logger.info("Navigated to Snapchat")

        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept='video/mp4,video/quicktime,video/webm,image/jpeg,image/png']"))
        )
        file_input.send_keys(video_path)
        logger.info("Video file uploaded")
        time.sleep(10)

        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/main/div[2]/div[2]/div[2]/div[5]/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div/div/div/div[1]"))
        )
        post_button.click()
        logger.info("Clicked post button")

        description_textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Add a description and #topics']"))
        )
        description_textarea.send_keys(description)
        logger.info("Added description")

        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree to Spotlight Terms')]"))
        )
        agree_button.click()
        logger.info("Agreed to Spotlight Terms")

        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[2]/div/div[2]/div[3]/div/button[2]"))
        )
        accept_button.click()
        logger.info("Accepted terms")

        post_final_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post to Snapchat')]"))
        )
        post_final_button.click()
        logger.info("Clicked final post button")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Yay! Your post is now live!']"))
        )
        logger.info("Upload success message detected")

    except Exception as e:
        logger.error(f"An error occurred during Snapchat upload: {e}")
        raise

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