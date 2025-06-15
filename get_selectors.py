#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

print("🔍 Getting all selector options...")

# Setup Firefox
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get('https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index')
    time.sleep(3)
    
    # Get article options
    print("\n=== ARTICLE OPTIONS ===")
    article_element = driver.find_element(By.ID, "article_id")
    article_select = Select(article_element)
    
    for i, option in enumerate(article_select.options):
        value = option.get_attribute('value')
        text = option.text.strip()
        if 'agreement' in text.lower() or 'sale' in text.lower() or 'करार' in text or 'विक्री' in text:
            print(f"*** {i+1:3d}. '{value}' | {text}")
        else:
            print(f"    {i+1:3d}. '{value}' | {text}")
    
    # Select database first
    db_element = driver.find_element(By.ID, "dbselect")
    Select(db_element).select_by_value("3")
    time.sleep(2)
    
    # Get year options after selecting database
    print("\n=== YEAR OPTIONS (after selecting database) ===")
    try:
        year_element = driver.find_element(By.ID, "year")
        year_select = Select(year_element)
        
        for i, option in enumerate(year_select.options):
            value = option.get_attribute('value')
            text = option.text.strip()
            print(f"    {i+1:3d}. '{value}' | {text}")
    except Exception as e:
        print(f"Year dropdown error: {e}")
    
    print("\n✅ Done!")
    
finally:
    driver.quit()