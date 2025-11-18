from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json

def fill_google_form(data):
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')  # nếu muốn chạy ẩn
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10) 
    try:
        url = "https://docs.google.com/forms/d/e/1FAIpQLScSNByk48LdndODacJ8EKAqKwEvfYQS4Zx3EplfjM-uwBygEA/viewform"
        driver.get(url)
        print(f"Mở form cho {data['location']} tuổi {data['age']}")
        try:
            first_button = wait.until(EC.element_to_be_clickable( (By.XPATH, "//*[@id='i6']/div[3]") )) 
            first_button.click()
            time.sleep(1)
        except:
            print("Không tìm thấy nút đầu tiên, tiếp tục...")
        
        try: 
            continue_button = wait.until(EC.element_to_be_clickable( (By.XPATH, "//span[contains(text(), 'Tiếp')]") )) 
            continue_button.click() 
            time.sleep(2) 
        except: 
            print("Không tìm thấy nút Tiếp tục, tiếp tục...")
        age_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='mG61Hd']/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")
        ))
        age_input.clear()
        age_input.send_keys(str(data["age"]))
        location_input = driver.find_element(By.XPATH,
            "//*[@id='mG61Hd']/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input"
        )
        location_input.clear()
        location_input.send_keys(data["location"])
        skills_input = driver.find_element(By.XPATH,
            "//*[@id='mG61Hd']/div[2]/div/div[2]/div[5]/div/div/div[2]/div[1]/div[8]/div/div/div/div/div[1]/input"
        )
        skills_input.clear()
        skills_input.send_keys(data["skills"])
        availability_input = driver.find_element(By.XPATH,
            "//*[@id='mG61Hd']/div[2]/div/div[2]/div[6]/div/div/div[2]/div[1]/div[6]/div/div/div/div/div[1]/input"
        )
        availability_input.clear()
        availability_input.send_keys(data["availability"])
        interests_input = driver.find_element(By.XPATH,
            "//*[@id='mG61Hd']/div[2]/div/div[2]/div[7]/div/div/div[2]/div[1]/div[7]/div/div/div/div/div[1]/input"
        )
        interests_input.clear()
        interests_input.send_keys(data["interests"])

        submit_button = driver.find_element(By.XPATH,
            "//*[@id='mG61Hd']/div[2]/div/div[3]/div[1]/div[1]/div[2]/span"
        )
        submit_button.click()
        print("Đã gửi thành công")

        time.sleep(2)

    except Exception as e:
        print(f"Lỗi khi gửi: {e}")
        driver.save_screenshot("error.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    with open("volunteer_dataset_semantic_1000.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Bắt đầu gửi {len(dataset)} bản ghi...")
    start_idx = next(i for i, record in enumerate(dataset) if record["id"] == 500)
    for i, record in enumerate(dataset[start_idx:], start_idx):
        print(f"\n--- Gửi bản ghi {i}/{len(dataset)} ---")
        fill_google_form(record)
        time.sleep(3)
    print("\nHoàn thành gửi tất cả dữ liệu!")
