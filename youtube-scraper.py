from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from YoutubeTags import videotags
import json, re, time

options = Options()
options.add_argument('--headless=new')

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)

url = 'https://www.youtube.com/watch?v=94qfTPON5kU'
driver.get(url)

#preprocessing
try:
    # wait up to 15 seconds for the consent dialog to show up
    consent_overlay = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'dialog'))
    )

    # select the consent option buttons
    consent_buttons = consent_overlay.find_elements(By.CSS_SELECTOR, '.eom-buttons button.yt-spec-button-shape-next')
    if len(consent_buttons) > 1:
        # retrieve and click the 'Accept all' button
        accept_all_button = consent_buttons[1]
        accept_all_button.click()
except TimeoutException:
    print('Cookie modal missing')

# wait for YouTube to load the page data
WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.ytd-watch-metadata'))
)

#scraping logic
video = {}

title = driver \
    .find_element(By.CSS_SELECTOR, 'h1.ytd-watch-metadata') \
    .text

# dictionary where to store the channel info
channel = {}

# scrape the channel info attributes
channel_element = driver \
    .find_element(By.ID, 'owner')

channel_url = channel_element \
              .find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint') \
              .get_attribute('href')
channel_name = channel_element \
              .find_element(By.ID, 'channel-name') \
              .text

channel['url'] = channel_url
channel['name'] = channel_name

# click the description section to expand it
try:
    show_more_button = driver.find_element(By.XPATH, '//tp-yt-paper-button[@class="more-button style-scope ytd-video-secondary-info-renderer"]')
    show_more_button.click()
    time.sleep(2)  # Wait for the description to expand
except Exception as e:
    print("Show more button not found or already expanded:", e)

#extract tags
meta_keywords = driver.find_element(By.XPATH, "//meta[@name='keywords']")
tags = meta_keywords.get_attribute("content")
tags = tags.split(", ")

#Metadata corpus
video['title'] = title
video['channel'] = channel
video['tags'] = tags

# close the browser and free up the resources
driver.quit()

def namefix(name):
    new = re.sub(r'[<>:"/\\|?*]','_',name).rstrip(' .')
    return new

json_address = f"{namefix(title)}.json"

with open(json_address, 'w', encoding='utf-16') as file:
    json.dump(video, file)