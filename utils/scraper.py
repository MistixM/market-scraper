# Import drissionpage to work with page
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions

import time

from configparser import ConfigParser

from PIL import Image

def get_price(item) -> str:
    config = ConfigParser()
    config.read('constants/config.ini')

    options = ChromiumOptions()
    
    # options.set_argument("--headless") # hide browser

    # disable another unnecessary options
    options.set_argument("--disable-blink-features=AutomationControlled")
    options.set_argument("--disable-gpu") 
    options.set_argument("--disable-dev-shm-usage")
    options.set_argument("--disable-infobars")
    options.set_argument("--window-size=1920,1080")
    options.set_argument("--disable-features=IsolateOrigins,site-per-process") 
    options.set_argument("--disable-blink-features=AutomationControlled")
    options.set_argument("--disable-extensions")

    # IMPORTANT: set user-agent and change headers for the chrome. Removes these two lines will break the scraper
    options.set_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.set_argument("--accept-language=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")

    # Initialize driver with options
    driver = ChromiumPage(options)

    # Get provided item to scrape
    driver.get(item) 
    
    time.sleep(2)

    try:
        full_img = driver.get_screenshot()
        cropped = Image.open(full_img).crop((1250, 350, 1500, 450))
        cropped.save("temp_img.png")

    except Exception as e:
        print(e)
        print("Парсер не может найти указанный тег. Тег возможно был изменён, пожалуйста, укажите обновлённый")
        
        driver.close()
        driver.quit()
        input()
        exit()

    # Quit the driver
    driver.close()
    driver.quit()

    # And return the price
    # return float(price.replace("₽", "").replace(" ", "").replace("\u2009", "").strip())
     