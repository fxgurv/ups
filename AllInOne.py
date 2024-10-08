import os
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementNotInteractableException
from webdriver_manager.firefox import GeckoDriverManager

# Constants
PROFILE_PATH = r"C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\me97qgzd.default-release"
VIDEO_PATH = r"C:\Users\user\Desktop\ups\V2\video.mp4"
METADATA_PATH = r"C:\Users\user\Desktop\ups\V2\1.txt"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_metadata(file_path):
    """Read and parse the metadata from the given file."""
    logger.info(f"Reading metadata from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        title = lines[0].strip()
        description = ''.join(lines[1:-1]).strip()
        tags = lines[-1].strip()
        
        logger.info(f"Title: {title}")
        logger.info(f"Description: {description[:50]}...")
        logger.info(f"Tags: {tags}")
        
        return title, description, tags
    except FileNotFoundError:
        logger.error(f"Metadata file not found: {file_path}")
        return "", "", ""
    except Exception as e:
        logger.error(f"Error reading metadata: {e}")
        return "", "", ""

def setup_browser(profile_path):
    """Set up and return a Firefox browser instance with the given profile."""
    logger.info(f"Setting up Firefox browser with profile: {profile_path}")
    try:
        options = Options()
        options.add_argument("-profile")
        options.add_argument(profile_path)
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        logger.info("Firefox browser initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Error setting up browser: {e}")
        return None

def click_element(driver, xpath, timeout=20):
    """Wait for an element to be clickable and then click it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        time.sleep(random.uniform(0.5, 1))
        element.click()
        return True
    except TimeoutException:
        logger.error(f"Timeout waiting for element: {xpath}")
        return False
    except Exception as e:
        logger.error(f"Error clicking element {xpath}: {e}")



def upload_to_x(driver, video_path, title, description, tags):
    """Upload a video to X (Twitter) with the given title, description, and tags."""
    logger.info("Starting X (Twitter) upload process")
    try:
        driver.get("https://twitter.com/compose/tweet")
        logger.info("Navigated to X (Twitter) compose page")

        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        file_input.send_keys(video_path)
        logger.info(f"Video file uploaded: {video_path}")

        tweet_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
        )
        full_tweet = f"{title}\n\n{description}\n\n{tags}"[:280]  # Twitter character limit
        tweet_input.send_keys(full_tweet)
        logger.info("Tweet text entered")

        if not click_element(driver, "//span[text()='Tweet']"):
            raise Exception("Failed to click 'Tweet' button")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Your Tweet was sent')]"))
        )
        logger.info("Upload success message detected")

    except Exception as e:
        logger.error(f"Error during X (Twitter) upload: {e}")

        return False



def upload_to_linkedin(driver, video_path, title, description, tags):
    """Upload a video to LinkedIn with the given title, description, and tags."""
    logger.info("Starting LinkedIn upload process")
    try:
        driver.get("https://www.linkedin.com/feed/")
        logger.info("Navigated to LinkedIn feed")

        if not click_element(driver, "//span[text()='Start a post']"):
            raise Exception("Failed to click 'Start a post' button")

        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        file_input.send_keys(video_path)
        logger.info(f"Video file uploaded: {video_path}")

        post_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
        )
        full_post = f"{title}\n\n{description}\n\n{tags}"
        post_input.send_keys(full_post)
        logger.info("Post text entered")

        if not click_element(driver, "//span[text()='Post']"):
            raise Exception("Failed to click 'Post' button")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Post successful')]"))
        )
        logger.info("Upload success message detected")

    except Exception as e:
        logger.error(f"Error during LinkedIn upload: {e}")




def upload_to_instagram(driver, video_path, title, description, tags):
    """Upload a video to Instagram with the given title, description, and tags."""
    logger.info("Starting Instagram upload process")
    try:
        driver.get("https://www.instagram.com/")
        logger.info("Navigated to Instagram homepage")

        if not click_element(driver, "//*[@aria-label='New post']"):
            raise Exception("Failed to click 'New post' button")

        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        file_input.send_keys(video_path)
        logger.info(f"Video file uploaded: {video_path}")

        time.sleep(15)  # Wait for video processing

        if not click_element(driver, "//*[name()='svg' and @aria-label='Select crop']"):
            raise Exception("Failed to click crop button")

        if not click_element(driver, "//*[name()='svg' and @aria-label='Crop portrait icon']"):
            raise Exception("Failed to select portrait crop")

        for _ in range(2):
            if not click_element(driver, "//*[text()='Next']"):
                raise Exception("Failed to click 'Next' button")

        description_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='Write a caption...']"))
        )
        full_description = f"{title}\n\n{description}\n\n{tags}"
        description_input.send_keys(full_description)
        logger.info("Description entered")

        if not click_element(driver, "//*[text()='Share']"):
            raise Exception("Failed to click 'Share' button")

        WebDriverWait(driver, 120).until(
            lambda d: "Your reel has been shared." in d.page_source
        )
        logger.info("Upload success message detected")

        time.sleep(10)  # Wait for the page to update
        try:
            profile_link = driver.find_element(By.XPATH, "//a[contains(@href, '/reel/')]").get_attribute('href')
            logger.info(f"Uploaded video link: {profile_link}")
            print(f"Uploaded video link: {profile_link}")
        except NoSuchElementException:
            logger.error("Could not find the uploaded video link")

    except Exception as e:
        logger.error(f"Error during Instagram upload: {e}")

def upload_to_tiktok(driver, video_path, title, description, tags):
    """Upload a video to TikTok with the given title, description, and tags."""
    logger.info("Starting TikTok upload process")
    try:
        driver.get("https://www.tiktok.com/upload")
        logger.info("Navigated to TikTok upload page")

        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        file_input.send_keys(video_path)
        logger.info(f"Video file uploaded: {video_path}")

        caption_input = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'DraftEditor-editorContainer')]//div[contains(@class, 'public-DraftEditor-content')]"))
        )
        full_description = f"{title}\n\n{description}\n\n{tags}"
        try:
            caption_input.click()
            ActionChains(driver).move_to_element(caption_input).send_keys(full_description).perform()
        except ElementNotInteractableException:
            driver.execute_script("arguments[0].textContent = arguments[1];", caption_input, full_description)
        logger.info("Description entered")

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Uploaded']"))
        )
        logger.info("Upload completed")

        if not click_element(driver, "//button[contains(@class, 'TUXButton') and .//div[text()='Post']]"):
            raise Exception("Failed to click 'Post' button")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Your video has been uploaded']"))
        )
        logger.info("Upload success message detected")

    except Exception as e:
        logger.error(f"Error during TikTok upload: {e}")

def upload_to_snapchat(driver, video_path, title, description, tags):
    """Upload a video to Snapchat with the given title, description, and tags."""
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
        full_description = f"{title}\n\n{description}\n\n{tags}"
        description_textarea.send_keys(full_description)
        logger.info("Added description")

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

def upload_to_youtube(driver, video_path, title, description, tags):
    """Upload a video to YouTube with the given title, description, and tags."""
    logger.info("Starting YouTube upload process")
    try:
        driver.get("https://studio.youtube.com")
        WebDriverWait(driver, 20).until(EC.url_contains("studio.youtube.com"))
        channel_id = driver.current_url.split("/")[-1]
        logger.info(f"Retrieved Channel ID: {channel_id}")

        driver.get("https://www.youtube.com/upload")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "ytcp-uploads-file-picker")))

        file_picker = driver.find_element(By.TAG_NAME, "ytcp-uploads-file-picker")
        file_input = file_picker.find_element(By.TAG_NAME, "input")
        file_input.send_keys(video_path)
        time.sleep(5)  # Wait for the file to be uploaded

        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.ID, "textbox")))
        textboxes = driver.find_elements(By.ID, "textbox")
        
        title_box = textboxes[0]
        title_box.clear()
        title_box.send_keys(title)
        time.sleep(3)  # Short wait after setting the title
        
        description_box = textboxes[1]
        description_box.send_keys(f"{description}\n\n{tags}")
        time.sleep(3)  # Short wait after setting the description

        try:
            is_not_for_kids_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "VIDEO_MADE_FOR_KIDS_NOT_MFK"))
            )
            is_not_for_kids_checkbox.click()
        except TimeoutException:
            logger.warning("Could not find 'NOT_MADE_FOR_KIDS' checkbox. Trying alternative method.")
            try:
                not_for_kids_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
                )
                not_for_kids_label.click()
            except TimeoutException:
                logger.error("Failed to set 'made for kids' option. Continuing with upload.")

        for _ in range(3):
            try:
                next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button")))
                next_button.click()
                time.sleep(3)
            except TimeoutException:
                logger.warning(f"Next button not found on step {_+1}. Continuing to next step.")

        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"radioLabel\"]")))
            radio_buttons = driver.find_elements(By.XPATH, "//*[@id=\"radioLabel\"]")
            if len(radio_buttons) >= 2:
                driver.execute_script("arguments[0].scrollIntoView(true);", radio_buttons[1])
                radio_buttons[1].click()  # Select the second radio button for unlisted
            else:
                logger.warning("Could not find the correct radio button for unlisted visibility.")
        except TimeoutException:
            logger.error("Failed to set video visibility. Continuing with upload.")

        try:
            done_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "done-button")))
            done_button.click()
            time.sleep(5)  # Wait for the upload to finalize
        except TimeoutException:
            logger.error("Could not find the 'Done' button. Upload may not have completed successfully.")

        driver.get(f"https://studio.youtube.com/channel/{channel_id}/videos/short")
        time.sleep(2)
        videos = driver.find_elements(By.TAG_NAME, "ytcp-video-row")
        first_video = videos[0]
        anchor_tag = first_video.find_element(By.TAG_NAME, "a")
        href = anchor_tag.get_attribute("href")
        video_id = href.split("/")[-2]

        url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Uploaded Video: {url}")

    except Exception as e:
        logger.error(f"An unexpected error occurred during YouTube upload: {e}")

def main():
    title, description, tags = read_metadata(METADATA_PATH)
    driver = setup_browser(PROFILE_PATH)

    if driver:
        try:
            upload_to_snapchat(driver, VIDEO_PATH, title, description, tags)          
            upload_to_linkedin(driver, VIDEO_PATH, title, description, tags)          
            upload_to_x(driver, VIDEO_PATH, title, description, tags)
            upload_to_instagram(driver, VIDEO_PATH, title, description, tags)
            upload_to_tiktok(driver, VIDEO_PATH, title, description, tags)
            upload_to_youtube(driver, VIDEO_PATH, title, description, tags)


        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            logger.info("Closing the browser")
            driver.quit()
    else:
        logger.error("Failed to initialize browser. Exiting.")

if __name__ == "__main__":
    main()
    logger.info("Script execution completed")
