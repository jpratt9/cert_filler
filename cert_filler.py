from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from random import uniform as random_uniform, random as random_random
from urllib.parse import urlsplit, urlunsplit
from getpass import getpass

def init_driver(chrome_driver_path):
    # Setup Chrome options for the driver
    options = Options()
    options.add_argument("--start-maximized")  # Maximize the browser window
    options.add_argument("--incognito")  # Start Chrome in incognito mode
    options.add_argument("--disable-webrtc")  # Disable WebRTC to prevent IP leaks
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-devtools"])  # Disable unnecessary logging
    options.add_argument("--disable-logging")  # Further disable Chrome logging
    options.add_argument("--disable-dev-shm-usage")  # Disable shared memory to avoid errors
    options.add_argument("--disable-extensions")  # Disable Chrome extensions

    # Disable WebRTC IP handling to ensure no leaks
    options.add_experimental_option("prefs", {
        "webrtc.ip_handling_policy": "disable_non_proxied_udp"
    })

    # Provide a default chromedriver path if not specified
    if not chrome_driver_path:
        print("No path to chromedriver provided. Using default...")
        chrome_driver_path= '/Users/john/dev/vdi_login/chromedriver/chromedriver'

    # Initialize the Chrome webdriver with the provided path and options
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def find_element_by_xpath(wait, xpath):
    # Wait for an element to be present in the DOM and return it
    return wait.until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def fill_textbox_immediate(wait, xpath, input, clear = True):
    # Find the element and optionally clear the input before filling it
    element = find_element_by_xpath(wait, xpath)
    if clear:
        element.clear()  # Clear any existing value in the textbox
    element.send_keys(input)
    return element

def fill_textbox(wait, xpath, input, sleep_min = 0, pause = True):
    # Slowly fill the textbox character by character to simulate human input
    element = find_element_by_xpath(wait, xpath)
    
    for char in input:
        element.send_keys(char)
        if pause:
            sleep(random_uniform(sleep_min+0.1, sleep_min+0.3))  # Add a delay between key presses to mimic typing
        element = find_element_by_xpath(wait, xpath)
    return element

def wait_for_page_load(driver):
    # Wait for the page to fully load by checking the document's readyState
    while True:
        if driver.execute_script("return document.readyState") == "complete":
            break

def scroll_to_bottom(driver):
    # Scroll to the bottom of the page to load additional content
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for the new content to load
        sleep(2)
        
        # Calculate new scroll height and compare with the last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Break the loop if no new content is loaded
        if new_height == last_height:
            break
        
        # Update the last height for the next iteration
        last_height = new_height

def bsc_fmt_cert(raw_cert_name):
    # Basic formatting of certificate names by removing unwanted substrings
    bsc_fmt_cert = raw_cert_name
    phrases_to_remove = [":", "AWS", "Google Cloud", "Google", "Microsoft", "Certified", "HashiCorp", "KCNA", "CKA", "cert", "Certification"]
    for substring in phrases_to_remove:
        bsc_fmt_cert = bsc_fmt_cert.replace(substring, "").strip()
    
    # Replace special characters like hyphens with standard versions
    replacement_dict = {
        "–" : "-"
    }

    for old_substring, new_substring in replacement_dict.items():
        bsc_fmt_cert = bsc_fmt_cert.replace(old_substring, new_substring).strip()
    
    # Remove any extra spaces
    return " ".join(bsc_fmt_cert.split())

def bsc_fmt_dates(raw_full_date_string):
    # Format the date strings into a standard format (e.g., MMDDYYYY)
    month_dict = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    split_result = raw_full_date_string.split("·")
    has_expiry_date = "·" in raw_full_date_string
    raw_issue_date = split_result[0].replace("Issued", "").strip()
    raw_expiry_date = split_result[1].replace("Expires", "").replace("Expired", "").strip() if has_expiry_date else ""
    
    # Convert issue date to the required format
    issue_month = month_dict[raw_issue_date.split(" ")[0]]
    issue_year = raw_issue_date.split(" ")[1]
    result = [has_expiry_date, f"{issue_month}01{issue_year}"]
    
    # Convert expiry date if present
    if has_expiry_date:
        expiry_month = month_dict[raw_expiry_date.split(" ")[0]]
        expiry_year = raw_expiry_date.split(" ")[1]
        result.append(f"{expiry_month}01{expiry_year}")
    else:
        result.append(None)
    
    return result

def bsc_fmt_url(url):
    # Clean the URL by removing unnecessary query strings and parameters
    split_url = urlsplit(url)
    clean_url = urlunsplit((split_url.scheme, split_url.netloc, split_url.path, '', ''))
    clean_url = clean_url.replace("linked_in_profile", "").strip()
    return clean_url

# URLs and credentials for LinkedIn login
cert_claim_url = "https://www.bscemployee.com/certificates/add-certificate-claim/"

linkedin_email = input("Please enter your LinkedIn email: ")
linkedin_pwd = getpass("Please enter your LinkedIn password: ")
linkedin_user = input("Please enter your LinkedIn \"custom username\" (e.g., https://www.linkedin.com/in/jpratt444 -> jpratt444): ")
linkedin_certs_url = f"https://www.linkedin.com/in/{linkedin_user}/details/certifications/"
linkedin_login_url = "https://www.linkedin.com/login/"
linkedin_feed_url = "https://www.linkedin.com/feed/"

# Initialize Chrome driver path for Selenium
chrome_driver_path = input("Please download a chromedriver for Selenium to use (https://googlechromelabs.github.io/chrome-for-testing/#stable for the latest version, https://chromedriver.storage.googleapis.com/index.html for old versions). The version number must match your version of Google Chrome. Enter its file path:")

# Start LinkedIn session
linkedin_chromedriver = init_driver(chrome_driver_path)
linkedin_wait = WebDriverWait(linkedin_chromedriver, 7)
linkedin_chromedriver.get(linkedin_login_url)

# Log in to LinkedIn with the provided credentials
fill_textbox(linkedin_wait, "//*[@id='username'][1]", linkedin_email, sleep_min = 0, pause=False)
linkedin_pwd_ele = fill_textbox(linkedin_wait, "//*[@id='password'][1]", linkedin_pwd, sleep_min = 0, pause=False)
linkedin_pwd_ele.send_keys(Keys.ENTER)

# Wait for the LinkedIn feed page to load
while True:
    current_url = linkedin_chromedriver.current_url
    if current_url == linkedin_feed_url:
        print("Page has reached the expected URL!")
        break
    sleep(1)

# Access LinkedIn certifications page
linkedin_chromedriver.get(linkedin_certs_url)
wait_for_page_load(linkedin_chromedriver)
scroll_to_bottom(linkedin_chromedriver)

# Locate the element containing certifications
div_ele = find_element_by_xpath(linkedin_wait, "//div[contains(@class, 'scaffold-finite-scroll__content')]")
ul_ele = div_ele.find_element(By.TAG_NAME, 'ul')
cert_li_eles = ul_ele.find_elements(By.XPATH, './li')  # Find all certifications

# Process certifications
print(f"Certs found on LinkedIn profile: {len(cert_li_eles)}")
full_certs = []
for li in cert_li_eles:
    # Extract and format the certificate name, issue, and expiry dates
    cert_name = bsc_fmt_cert(li.find_element(By.XPATH,'.//span').text)
    issued_text = li.find_element(By.XPATH, ".//*[starts-with(text(), 'Issued')]").text
    has_expiry, issue_date, expiry_date = bsc_fmt_dates(issued_text)

    try:
        link_div = li.find_element(By.CLASS_NAME, "pv-action__padding")
    except NoSuchElementException:
        print("No link found for this cert. Continuing...")
        continue

    link_a_ele = link_div.find_element(By.TAG_NAME, "a")
    link_text = bsc_fmt_url(link_a_ele.get_attribute("href"))

    # Print and store certification details
    print(f"Cert: {cert_name}")
    print(f"Issue date: {issue_date}")
    if has_expiry:
        print(f"Expiry date: {expiry_date}")
    print(f"Cert link: {link_text}")
    
    full_certs.append({
        "cert_name" : cert_name,
        "expires" : has_expiry,
        "issue_date" : issue_date,
        "expiry_date" : expiry_date,
        "url" : link_text
    })

# Setup Chrome WebDriver for BSC login
bsc_email = input("Please enter your BSC email: ")
bsc_pwd = getpass("Please enter your BSC password: ")


bsc_cert_chromedriver = init_driver(chrome_driver_path)
bsc_cert_wait = WebDriverWait(bsc_cert_chromedriver, 7)

# Sign into BSC Google account
bsc_cert_chromedriver.get("https://www.bscemployee.com/certificates/add-certificate-claim")
fill_textbox(bsc_cert_wait, "//input[@type='email'][1]", bsc_email, sleep_min = 0, pause=False).send_keys(Keys.ENTER)
fill_textbox(bsc_cert_wait, "//*[@id='username'][1]", bsc_email, sleep_min = 0, pause=False).send_keys(Keys.ENTER)
fill_textbox(bsc_cert_wait, "//*[@id='password'][1]", bsc_pwd, sleep_min = 0, pause=False).send_keys(Keys.ENTER)
bsc_auth_code = input("Please enter your BSC MFA code: ")
# Try doing MFA code page if it loads, otherwise skip it
try:
    fill_textbox(bsc_cert_wait, "//*[@id='security-code'][1]", bsc_auth_code, sleep_min = 0, pause=False).send_keys(Keys.ENTER)
except TimeoutException:
    print("MFA code textbox not found. Attempting to skip...")

wait_for_page_load(bsc_cert_chromedriver)

failures = []
# Input all certifications into the BSC system
for i, cert in enumerate(full_certs):
    print(f"Entering '{cert['cert_name']}' cert into BSC system...")
    if i != 0:
        bsc_cert_chromedriver.get("https://www.bscemployee.com/certificates/add-certificate-claim")
    wait_for_page_load(bsc_cert_chromedriver)

    # Fill out the form with certification details
    cert_name_xpath = '//span[@id="select2-certificate-id-container"]'
    cert_input_xpath = "//input[@class='select2-search__field'][1]"
    cert_results_xpath = "//span[@class='select2-results']"
    issue_date_xpath = "//input[@name='issue_date']"
    expiry_date_xpath = "//input[@type='date' and @name='expiry_date']"
    no_expiry_checkbox_xpath = '//input[@type="checkbox"][1]'
    no_cert_found_xpath = ".//li[@role='alert' and contains(@class, 'select2-results__message')]"
    url_xpath = '//input[@type="url"][1]'
    alert_div = "//div[@role='alert'][1]"

    find_element_by_xpath(bsc_cert_wait, cert_name_xpath)
    bsc_cert_chromedriver.find_element(By.XPATH, cert_name_xpath).click()

    cert_name_input = fill_textbox_immediate(bsc_cert_wait, cert_input_xpath, cert["cert_name"], clear=False)
    try:
        no_cert_found_alert = bsc_cert_chromedriver.find_element(By.XPATH, cert_results_xpath).find_element(By.XPATH, no_cert_found_xpath)
    except NoSuchElementException:
        no_cert_found_alert = None
    
    # Skip certifications not found in BSC system
    if no_cert_found_alert:
        print(f"Cert {cert['cert_name']} not found in BSC Cert system. Skipping...")
        failures.append(cert)
        continue

    # Complete the form with issue/expiry dates and URL
    cert_name_input.send_keys(Keys.ENTER)
    fill_textbox_immediate(bsc_cert_wait, issue_date_xpath, cert["issue_date"])
    if cert["expires"]:
        fill_textbox_immediate(bsc_cert_wait, expiry_date_xpath, cert["expiry_date"], clear=False)
    else:
        bsc_cert_chromedriver.find_element(By.XPATH, no_expiry_checkbox_xpath).click()
    
    cert_url_input = fill_textbox_immediate(bsc_cert_wait, url_xpath, cert["url"], clear=False)
    cert_url_input.send_keys(Keys.ENTER)
    alert = find_element_by_xpath(bsc_cert_wait, alert_div)

    # Log errors
    if alert and "has been added" not in alert.text.strip():
        print(f"ERROR : {alert.text.strip()}")
        failures.append(cert)

print(f"ERROR : Failed to add the following certs - {[d['cert_name'] for d in failures]}. Go back & add these manually.")

print("Finished entering all certifications. *IMPORTANT*: You will have to go back & enter dates (day of month) manually.")
print("Please validate that no extra certifications were added in error.")
input("Press any key to exit: ")
