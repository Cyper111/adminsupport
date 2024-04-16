
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Replace these with your actual username and password
username_str = 'user'
password_str = 'input ("Enter your password: ")'

# Setting up the WebDriver
driver = webdriver.Chrome() # or use another WebDriver, e.g., webdriver.Firefox()
driver.get('google.com')  # Replace with the actual URL

# Waiting for the relevant elements to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))

# Find the input fields
username_input = driver.find_element_by_name('username')  # Replace with the correct name or id
password_input = driver.find_element_by_name('password')  # Replace with the correct name or id

# Sending the login information
username_input.send_keys(username_str)
password_input.send_keys(password_str)

# Find the login button and click it
login_button = driver.find_element_by_name('login')  # Replace with the correct name or id
login_button.click()

# Your custom code after login 
# ...

# Don't forget to close the browser!
driver.close()