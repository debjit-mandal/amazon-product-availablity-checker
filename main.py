import csv
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import time

def check_product_availability(url, retry_attempts=3, timeout=10):
    for _ in range(retry_attempts):
        try:
            # Send a GET request to the Amazon product page
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an exception for any HTTP errors

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the availability element on the page
            availability = soup.find('span', {'class': 'a-size-medium a-color-success'})

            if availability:
                return availability.text.strip()  # Return the availability text if found

            return 'Unavailable'  # If availability information is not found, return 'Unavailable'

        except requests.exceptions.RequestException as e:
            print('An error occurred while fetching the page:', e)
            time.sleep(2)  # Wait for 2 seconds before retrying

    return 'Error'  # If all retry attempts fail, return 'Error'

# Load product URLs from a CSV file
def load_product_urls(file_path):
    urls = []
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                urls.append(row[0])  # Assume the URL is in the first column
    except IOError as e:
        print('Error loading the CSV file:', e)
    return urls

# Send email notification
def send_email_notification(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)
        smtp_server.send_message(msg)
        smtp_server.quit()

        print('Email notification sent to', recipient_email)
    except smtplib.SMTPException as e:
        print('An error occurred while sending the email:', e)
    except ConnectionError as e:
        print('A network error occurred while sending the email:', e)
    except Exception as e:
        print('An error occurred:', e)

# Load configuration from a file
def load_configuration(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

# Example usage
config_file_path = 'config.ini'
product_urls_file_path = 'product_urls.csv'
output_file_path = 'product_availability.csv'

# Load configuration from the file
config = load_configuration(config_file_path)

# Retrieve email settings from the configuration
sender_email = config.get('Email', 'SenderEmail')
sender_password = config.get('Email', 'SenderPassword')
recipient_email = config.get('Email', 'RecipientEmail')

# Retrieve product URLs from the CSV file
product_urls = load_product_urls(product_urls_file_path)

# Keep track of previous availability status and email notification timestamp
previous_availability = {}
notification_timestamp = time.time()
notification_interval = 3600  # 1 hour

while True:
    # Open the CSV file in write mode
    try:
        with open(output_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Product URL', 'Availability'])

            for url in product_urls:
                availability = check_product_availability(url)

                if url in previous_availability:
                    if availability != previous_availability[url]:
                        # Availability has changed, send email notification if notification interval has passed
                        writer.writerow([url, availability])  # Write the URL and availability to the CSV file
                        if time.time() - notification_timestamp >= notification_interval:
                            # Prepare email content
                            subject = 'Product Availability Update'
                            body = f"URL: {url}\nAvailability: {availability}"

                            # Send email notification
                            send_email_notification(sender_email, sender_password, recipient_email, subject, body)

                            notification_timestamp = time.time()  # Update the notification timestamp
                else:
                    # First time checking availability, store the initial status
                    writer.writerow([url, availability])  # Write the URL and availability to the CSV file

                previous_availability[url] = availability  # Update the previous availability status

        print('Product availability data has been written to', output_file_path)

    except IOError as e:
        print('Error writing to or reading from the CSV file:', e)

    # Wait for 1 minute before checking availability again
    time.sleep(60)
