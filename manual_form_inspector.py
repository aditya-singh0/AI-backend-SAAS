#!/usr/bin/env python3
"""
Manual Form Inspector - Opens Firefox visibly for manual inspection
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def main():
    print("🔍 Manual Form Inspector")
    print("=" * 50)
    print("This will open Firefox so you can manually inspect the form")
    print("Look for Village, Taluka, and other location selectors")
    print("=" * 50)
    
    # Setup visible Firefox
    options = webdriver.FirefoxOptions()
    # No headless - we want to see the browser
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1280, 1024)
    
    try:
        print("🚀 Opening IGR website...")
        driver.get('https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index')
        time.sleep(3)
        
        print("✅ Website loaded!")
        print("\n📋 INSPECTION CHECKLIST:")
        print("1. Look at the form - count all dropdown menus")
        print("2. Check if there are Village/Taluka dropdowns")
        print("3. Try selecting Database = '3' (Recent years)")
        print("4. Try selecting District = 'Mumbai' (मुंबई)")
        print("5. See if new dropdowns appear after selections")
        print("6. Look for any Village/Taluka/Tehsil options")
        
        print("\n🔍 WHAT TO LOOK FOR:")
        print("- Village dropdown (गाव)")
        print("- Taluka dropdown (तालुका)")
        print("- Tehsil dropdown (तहसील)")
        print("- Sub-district dropdown")
        print("- Any other location-based dropdowns")
        
        # Auto-fill some fields to see if new ones appear
        try:
            print("\n🤖 Auto-filling some fields to trigger dynamic dropdowns...")
            
            # Select database
            db_element = driver.find_element(By.ID, "dbselect")
            Select(db_element).select_by_value("3")
            print("   ✅ Database selected")
            time.sleep(2)
            
            # Wait and select Mumbai
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']"))
            )
            district_element = driver.find_element(By.ID, "district_id")
            Select(district_element).select_by_value("31")
            print("   ✅ Mumbai district selected")
            time.sleep(2)
            
            print("   🔍 Check if new dropdowns appeared after district selection!")
            
        except Exception as e:
            print(f"   ⚠️ Auto-fill error: {e}")
        
        print("\n" + "="*60)
        print("👀 MANUALLY INSPECT THE FIREFOX BROWSER NOW")
        print("Look for all dropdown menus and note their IDs/names")
        print("="*60)
        
        input("\n>>> Press Enter when you're done inspecting...")
        
        # Print all select elements found
        print("\n📊 TECHNICAL ANALYSIS:")
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"Found {len(selects)} total dropdown elements:")
        
        for i, select in enumerate(selects):
            try:
                select_id = select.get_attribute('id')
                select_name = select.get_attribute('name')
                print(f"   {i+1}. ID: '{select_id}', Name: '{select_name}'")
            except:
                print(f"   {i+1}. [Error reading element]")
        
    finally:
        print("\n👋 Closing browser...")
        driver.quit()
        print("✅ Done!")

if __name__ == '__main__':
    main() 