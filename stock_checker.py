import time
import os
import random
import smtplib
import ssl
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

PRODUCT_URL = "https://www.microcenter.com/product/691100/asrock-amd-radeon-rx-9070-xt-steel-legend-triple-fan-16gb-gddr6-pcie-50-graphics-card?storeid=171"

# Email credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Function to send email alerts
def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL

        # Connect to email server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def check_stock_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(20)  # Prevent infinite hangs
        driver.get(PRODUCT_URL)
        
        time.sleep(random.uniform(3, 6))  # Mimic human browsing

        stock_text = None
        stock_count = None
        try:
            # First, check if any inventory container exists
            inventory_div = driver.find_element(By.CLASS_NAME, "inventory")
            
            # Then, check for the actual stock count (inventoryCnt)
            stock_status_elements = inventory_div.find_elements(By.CLASS_NAME, "inventoryCnt")

            if stock_status_elements:
                stock_text = stock_status_elements[0].text.strip().lower()
                stock_count = stock_text[0:3]
            else:
                print("❌ Product is OUT OF STOCK (No inventoryCnt found).")
        
        except:
            print("⚠ Inventory section not found at all. Assuming out of stock.")

        driver.quit()

        if stock_text and "in stock" in stock_text:
            send_email("Micro Center Stock Alert", f"The product is in stock! Count: {stock_count} Check: {PRODUCT_URL}")
            return True
        else:
            print("❌ Not in stock yet (Selenium check).")

    except Exception as e:
        print(f"❌ Selenium error: {e}")

    return False


def run_stock_checker():
    check_stock_selenium()
    # while True:
    #     print("\n🔄 Checking stock...")
    #     if(check_stock_selenium()):
    #         break

    #     sleep_time = random.randint(300, 600)  # Wait between 3 to 10 minutes
    #     print(f"⏳ Sleeping for {sleep_time} seconds...\n")
    #     time.sleep(sleep_time)

# Start the bot
run_stock_checker()
