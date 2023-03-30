import requests
import json
import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


TOKEN = 'YOUR_TOKEN_HERE'
URL = f'https://api.telegram.org/bot{TOKEN}/'

# Dictionary to store information about each user
users = {}


# Method sends a message to the specified chat_id
def send_message(chat_id, text):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)


# Send a message to a user specified by their chat_id
def send_updates():
    for chat_id in users:
        # Change the message here to whatever you want to send to each user
        message = "This is an update from your bot."
        send_message(chat_id, message)


def click_button_in_kamu_chatbot():
    # Create a new Chrome browser window
    driver = webdriver.Chrome()

    # Navigate to the Kamu chatbot page
    driver.get("https://migri.fi/en/citizenship-for-adults")

    # Wait for the page to load
    time.sleep(5)

    # Accept cookies
    # button_element = driver.find_element("xpath", f"//*[contains(text(), 'I accept all cookies')]")
    # button_element.click()

    # Find Kamu chatbot
    element = driver.find_element(By.CLASS_NAME, 't2m-trigger.t2m-empty')
    # Click the button
    driver.execute_script("arguments[0].click();", element)

    # Wait for the button click to complete
    time.sleep(15)

    # Query the queue number
    button_element = driver.find_element("xpath", f"//*[contains(text(), 'My place in queue')]")
    button_element.click()

    time.sleep(5)

    # Find the search box element and send keys
    search_box = driver.find_element(By.CLASS_NAME, 'ComposeFooter__StyledTextArea-jPCSeW.kVVZEX.Boost-ChatPanel-Composer')
    search_box.send_keys("YOUR_NUMBER_HERE")

    # Press the Enter key
    search_box.send_keys(Keys.RETURN)

    time.sleep(10)

    # Find the username input field element and extract its value attribute
    input = driver.find_element(By.CLASS_NAME, 'CounterSlider__MarkerCount-bgvjiu.jdPtXZ')
    queue_number = input.text

    # Close the browser window
    driver.quit()

    return queue_number


def handle_message(message):
    chat_id = message['chat']['id']
    text = message['text']

    # Check if the user is in the dictionary
    if chat_id not in users:
        users[chat_id] = {}

    # Do something based on the user's message
    users[chat_id]['name'] = message['from']['first_name']
    send_message(chat_id, f"Hello, {message['from']['first_name']}! Please wait, I am getting your queue number.")
    queue_number = click_button_in_kamu_chatbot()
    print(queue_number)
    send_message(chat_id, f"Your queue number is {queue_number}")


if __name__ == '__main__':
    # Set up the task scheduler to send a message every minute
    # schedule.every().minute.do(send_updates)

    # Get the latest update ID to avoid processing the same message multiple times
    url = URL + 'getupdates'
    response = requests.get(url)
    updates = json.loads(response.content)['result']
    latest_update_id = updates[-1]['update_id'] if updates else None

    while True:
        # Get new updates from the Telegram server
        url = URL + f'getupdates?offset={latest_update_id + 1}' if latest_update_id else URL + 'getupdates'
        response = requests.get(url)
        updates = json.loads(response.content)['result']

        # Process each new message
        for update in updates:
            handle_message(update['message'])
            latest_update_id = update['update_id']

        # schedule.run_pending()
        # Wait for a short time before checking for new updates again
        time.sleep(1)
