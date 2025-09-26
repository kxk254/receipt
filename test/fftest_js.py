import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model

@pytest.fixture
def driver():
    chromedriver_path = r'C:\Users\konno\SynologyDrive\develop\djhtml\receipt_ocr_dev\chromedriver-win32\chromedriver-win32\chromedriver.exe'
    # Setup WebDriver (for Chrome in this case)
    # service = Service(ChromeDriverManager().install())
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()

@pytest.fixture
def user():
    """Fixture to create a test user"""
    user_model = get_user_model()
    return user_model.objects.create_user(username='testuser', password='testpassword')

@pytest.mark.django_db
def test_user_creation(user):
    # Fetch the user from the database
    user_model = get_user_model()
    user_from_db = user_model.objects.get(username='testuser')

    # Check if the user exists and has the expected attributes
    assert user_from_db is not None
    assert user_from_db.username == 'testuser'
    assert user_from_db.check_password('testpassword')  # Verify the password is correct

@pytest.mark.django_db
def test_dropzone_upload(driver, user):
    # Go to your page (replace with the actual URL of your page)
    driver.get("http://localhost:8000/accounts/login/")  #?next=/
    # username_field = driver.find_element(By.NAME, "testuser")  # Adjust the field name if necessary
    # print(driver.page_source) 
    # driver.switch_to.frame("frame_name_or_id")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "login"))  # Adjust if necessary
    )
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys('testuser')
    password_field.send_keys('testpassword')
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    print("2001", driver.current_url)  # Debugging statement
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    # WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:8000/"))
    driver.get("http://localhost:8000/dropupload/")
    print("3001", driver.current_url)  # Debugging statement

    # WebDriverWait(driver, 10).until(EC.url_contains("dropupload/"))
    # driver.get("http://localhost:8000/dropupload/")  # Adjust this to your Django app URL

    # Find the dropzone element
    dropzone_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "my-awesome-dropzone"))
    )

    # Simulate dragging and dropping a file (or just selecting it manually if easier)
    # file_input = driver.find_element(By.NAME, "file")  # This depends on your form's HTML
    # file_input.send_keys("/path/to/your/test-file.pdf")  # Adjust with the actual file path

    # Find the upload button and click it
    # upload_button = driver.find_element(By.ID, "upload-button")
    # upload_button.click()

    # Wait for the upload to complete (adjust according to the process time)
    # time.sleep(5)

    # Check for a success message (this is based on your JavaScript that shows alerts)
    # alert = driver.switch_to.alert
    # assert "success" in alert.text.lower()  # Assuming success message contains 'success'
    # alert.accept()