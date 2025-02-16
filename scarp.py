from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# ✅ Initialize WebDriver
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")  # Open browser in maximized mode
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

# ✅ Open the website
url = "https://app.virtubox.io/bharat-tex/directory-website"
driver.get(url)

data_list = []

def smooth_scroll():
    """ Scrolls down smoothly to ensure all data loads properly. """
    scroll_height = driver.execute_script("return document.body.scrollHeight")  # Get full page height
    current_scroll = 0
    step = scroll_height // 10  # Divide scrolling into 10 steps

    while current_scroll < scroll_height:
        driver.execute_script(f"window.scrollTo(0, {current_scroll});")
        current_scroll += step
        time.sleep(0.5)  # Wait to allow content to load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Final scroll

while True:
    try:
        # ✅ Wait for the table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "DataTables_Table_0"))
        )

        # ✅ Scroll to load all visible data
        smooth_scroll()

        # ✅ Extract table rows
        rows = driver.find_elements(By.XPATH, '//*[@id="DataTables_Table_0"]/tbody/tr')
        
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            data = [col.text.strip() for col in columns]
            data_list.append(data)

        # ✅ Try clicking the "Next" button if available
        try:
            next_button = driver.find_element(By.XPATH, '//a[@class="page-link" and contains(text(), "Next")]')

            if "disabled" in next_button.get_attribute("class"):
                break  # Stop if "Next" button is disabled

            next_button.click()
            time.sleep(2)  # Wait for page load
        except Exception:
            break  # Exit if "Next" button is not found

    except Exception as e:
        print(f"Error encountered: {e}")
        break  # Exit the loop if an error occurs

# ✅ Save data to CSV
columns = [
    "Company Name", "Hall No.", "Booth No.", "Product Group",
    "Product Zone", "Contact Person", "Email", "Mobile",
    "City", "State", "Country", "Event Venue"
]
df = pd.DataFrame(data_list, columns=columns)
df.to_csv("scraped_data.csv", index=False, encoding="utf-8")

# ✅ Close browser
driver.quit()

print("Scraping Completed! Data saved to 'scraped_data.csv'.")
