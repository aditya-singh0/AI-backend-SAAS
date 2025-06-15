#!/usr/bin/env python3
"""
Quick Selector Check - Saves all dropdown options to files
"""
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
    options.add_argument("--headless")  # Run in background
    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def save_dropdown_options(driver, select_id, filename):
    try:
        element = driver.find_element(By.ID, select_id)
        select = Select(element)
        options = select.options
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Dropdown: {select_id}\n")
            f.write(f"Total options: {len(options)}\n")
            f.write("="*50 + "\n")
            
            for i, option in enumerate(options):
                value = option.get_attribute('value')
                text = option.text.strip()
                f.write(f"{i+1:3d}. Value: '{value}' | Text: '{text}'\n")
        
        print(f"✅ Saved {len(options)} options for {select_id} to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error with {select_id}: {e}")
        return False

def main():
    print("🔍 Quick Selector Check - Saving all options to files")
    
    driver = setup_driver()
    try:
        driver.get('https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index')
        time.sleep(3)
        
        # Create data directory
        os.makedirs('selector_data', exist_ok=True)
        
        # Save initial state
        save_dropdown_options(driver, "dbselect", "selector_data/dbselect_options.txt")
        save_dropdown_options(driver, "district_id", "selector_data/district_initial.txt")
        save_dropdown_options(driver, "article_id", "selector_data/article_initial.txt")
        save_dropdown_options(driver, "year", "selector_data/year_initial.txt")
        
        # Select database and save updated options
        db_element = driver.find_element(By.ID, "dbselect")
        Select(db_element).select_by_value("3")
        time.sleep(2)
        
        save_dropdown_options(driver, "district_id", "selector_data/district_after_db.txt")
        save_dropdown_options(driver, "article_id", "selector_data/article_after_db.txt")
        save_dropdown_options(driver, "year", "selector_data/year_after_db.txt")
        
        # Select Mumbai district
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']"))
        )
        district_element = driver.find_element(By.ID, "district_id")
        Select(district_element).select_by_value("31")  # Mumbai
        time.sleep(2)
        
        save_dropdown_options(driver, "article_id", "selector_data/article_after_district.txt")
        save_dropdown_options(driver, "year", "selector_data/year_after_district.txt")
        
        print("\n✅ All selector data saved to 'selector_data' folder!")
        print("Check the files to find the correct Agreement to Sale article ID.")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()