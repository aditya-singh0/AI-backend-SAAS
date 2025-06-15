#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def save_options(driver, select_id, filename):
    try:
        element = driver.find_element(By.ID, select_id)
        select = Select(element)
        options = select.options
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Dropdown: {select_id}\n")
            f.write(f"Total: {len(options)}\n")
            f.write("="*40 + "\n")
            
            for i, option in enumerate(options):
                value = option.get_attribute('value')
                text = option.text.strip()
                f.write(f"{i+1:3d}. '{value}' | {text}\n")
        
        print(f"✅ {select_id}: {len(options)} options saved")
        return True
    except Exception as e:
        print(f"❌ {select_id}: {e}")
        return False

def main():
    print("🔍 Selector Inspector")
    driver = setup_driver()
    try:
        driver.get('https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index')
        time.sleep(3)
        
        os.makedirs('selectors', exist_ok=True)
        
        # Initial state
        save_options(driver, "dbselect", "selectors/db.txt")
        save_options(driver, "district_id", "selectors/district_init.txt")
        save_options(driver, "article_id", "selectors/article_init.txt")
        save_options(driver, "year", "selectors/year_init.txt")
        
        # After selecting database
        Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
        time.sleep(2)
        save_options(driver, "district_id", "selectors/district_db.txt")
        save_options(driver, "article_id", "selectors/article_db.txt")
        save_options(driver, "year", "selectors/year_db.txt")
        
        print("✅ All data saved to 'selectors' folder")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main() 