# amazon-product-availablity-checker
It is an Amazon product availability checker made using Python.This script uses web scraping techniques to extract the availability information from the Amazon product page.

To run this script, you will need to install the `beautifulsoup4` and `requests` libraries. You can install them using pip:

`pip install beautifulsoup4 requests`
The code runs in an infinite loop, periodically checking the availability of the products and waiting for 1 hour before checking again. You can adjust the interval by modifying the `time.sleep()` duration.

Please make sure to have a valid `config.ini` file with the appropriate email settings, and ensure that the `product_urls.csv` file contains the correct product URLs. Modify the file paths and configuration options as needed.

Also make sure to provide valid email credentials and modify the email content and configuration according to your requirements.

To run this code locally:

`git clone https://github.com/debjit-mandal/amazon-product-availablity-checker`

`cd amazon-product-availablity-checker`

`python main.py`

Please feel free to suggest any kind of improvements.
