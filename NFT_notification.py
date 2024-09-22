from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import logging

# Path to ChromeDriver in the GitHub Actions environment
chrome_driver_path = '/usr/local/bin/chromedriver'

# Chrome binary location in the GitHub Actions environment
chrome_binary_path = '/usr/bin/google-chrome'

# Marketplace URL
URL = "https://marketplace.openxswap.exchange/Collection/59144/0x8d95f56b0bac46e8ac1d3a3f12fb1e5bc39b4c0c"

# Email credentials
SENDER_EMAIL = "notificationlynx@gmail.com"
RECEIVER_EMAIL = "jenopakin@gmail.com"
PASSWORD = "ahrd jkji ylsy kypx"

# Set up basic logging
logging.basicConfig(filename='nft_scraper.log', level=logging.INFO)

# Track previously seen listings
previous_listings = set()

# A flag to check if this is the first run
is_first_run = True

# Function to fetch data using Selenium with explicit waits
def check_listings_with_selenium():
    # Set Chrome options to specify the Chrome binary location and headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--no-sandbox')  # Required for CI environments
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--window-size=1920x1080')  # Set window size
    chrome_options.add_argument('--remote-debugging-port=9222')  # Prevent DevToolsActivePort error
    chrome_options.add_argument('--log-level=0')  # Enable verbose logging
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')

    # Start ChromeDriver with the specified Chrome binary and service
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the URL
    driver.get(URL)

    try:
        # Explicit wait to make sure the listings load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "dt"))
        )
    except Exception as e:
        print("Error: Timed out waiting for the page to load.")
        driver.quit()
        return []

    # Get the page source (after JS execution)
    page_source = driver.page_source
    driver.quit()

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(page_source, 'html.parser')

    # Your existing scraping logic here...

    return new_listings
    
# Function to send email notification
def send_email_notification(new_listing):
    subject = "New NFT Listing Alert"
    body = f"New NFT Listed!\nLocked Value: {new_listing['locked_value']}\nDiscount: {new_listing['discount']}\nLocked: {new_listing['lock_amount']}"

    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, PASSWORD)
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)

# Main function to check listings and notify
def check_and_notify():
    global is_first_run
    new_listings = check_listings_with_selenium()

    if new_listings:
        print(f"New listings found: {len(new_listings)}")
        for listing in new_listings:
            print(f"Listing found - Locked Value: {listing['locked_value']}, Discount: {listing['discount']}, Locked: {listing['lock_amount']}")
            send_email_notification(listing)
    else:
        print("No new listings found.")

    # After the first run, set is_first_run to False
    if is_first_run:
        is_first_run = False

# Schedule the function to run periodically
schedule.every(1).minutes.do(check_and_notify)  # Run the script every 1 minute

# Run the scheduler in a loop
while True:
    schedule.run_pending()
    time.sleep(1)
