#!/usr/bin/env python3
"""
Comprehensive Form Inspector - Find all selectors including Village, Taluka
"""
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

def inspect_all_form_elements(driver):
    """Find all form elements on the page"""
    print("🔍 INSPECTING ALL FORM ELEMENTS")
    print("=" * 50)
    
    # Find all select elements
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"Found {len(selects)} dropdown elements:")
    
    for i, select in enumerate(selects):
        try:
            select_id = select.get_attribute('id')
            select_name = select.get_attribute('name')
            select_class = select.get_attribute('class')
            
            print(f"\n{i+1}. SELECT ELEMENT:")
            print(f"   ID: '{select_id}'")
            print(f"   Name: '{select_name}'")
            print(f"   Class: '{select_class}'")
            
            # Get options
            select_obj = Select(select)
            options = select_obj.options
            print(f"   Options: {len(options)}")
            
            # Show first few options
            for j, option in enumerate(options[:5]):
                value = option.get_attribute('value')
                text = option.text.strip()
                print(f"      {j+1}. '{value}' | {text}")
            
            if len(options) > 5:
                print(f"      ... and {len(options) - 5} more options")
                
        except Exception as e:
            print(f"   Error inspecting select {i+1}: {e}")

def inspect_specific_selectors(driver):
    """Look for specific location-based selectors"""
    print("\n🎯 LOOKING FOR SPECIFIC LOCATION SELECTORS")
    print("=" * 50)
    
    # Common selector IDs/names for location
    location_selectors = [
        'village_id', 'village', 'village_name',
        'taluka_id', 'taluka', 'taluka_name', 'tehsil_id', 'tehsil',
        'sub_district', 'sub_district_id',
        'block_id', 'block', 'block_name',
        'area_id', 'area', 'area_name',
        'zone_id', 'zone', 'zone_name'
    ]
    
    found_selectors = []
    
    for selector in location_selectors:
        try:
            # Try by ID
            element = driver.find_element(By.ID, selector)
            found_selectors.append(('ID', selector, element))
            print(f"✅ Found by ID: '{selector}'")
        except:
            try:
                # Try by name
                element = driver.find_element(By.NAME, selector)
                found_selectors.append(('NAME', selector, element))
                print(f"✅ Found by NAME: '{selector}'")
            except:
                pass
    
    if not found_selectors:
        print("❌ No additional location selectors found")
    
    return found_selectors

def inspect_after_selections(driver):
    """Check what new selectors appear after making selections"""
    print("\n🔄 CHECKING DYNAMIC SELECTORS AFTER SELECTIONS")
    print("=" * 50)
    
    try:
        # Select database
        print("Selecting database...")
        db_element = driver.find_element(By.ID, "dbselect")
        Select(db_element).select_by_value("3")
        time.sleep(2)
        
        # Select Mumbai district
        print("Selecting Mumbai district...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']"))
        )
        district_element = driver.find_element(By.ID, "district_id")
        Select(district_element).select_by_value("31")
        time.sleep(2)
        
        # Check for new selectors
        print("Checking for new selectors after district selection...")
        new_selectors = inspect_specific_selectors(driver)
        
        # Select article
        print("Selecting Agreement article...")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
        article_element = driver.find_element(By.ID, "article_id")
        Select(article_element).select_by_value("42")  # Agreement to Sale
        time.sleep(2)
        
        # Check again for new selectors
        print("Checking for new selectors after article selection...")
        final_selectors = inspect_specific_selectors(driver)
        
        return final_selectors
        
    except Exception as e:
        print(f"Error during dynamic inspection: {e}")
        return []

def main():
    print("🔍 Comprehensive IGR Form Inspector")
    print("Looking for Village, Taluka, and all other selectors")
    print("=" * 60)
    
    driver = setup_driver()
    try:
        driver.get('https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index')
        time.sleep(3)
        
        # Initial inspection
        inspect_all_form_elements(driver)
        
        # Look for specific location selectors
        inspect_specific_selectors(driver)
        
        # Check dynamic selectors
        inspect_after_selections(driver)
        
        print("\n" + "=" * 60)
        print("✅ INSPECTION COMPLETE")
        print("Check the output above for Village, Taluka, and other location selectors")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()