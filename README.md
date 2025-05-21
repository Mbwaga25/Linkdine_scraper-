LinkedIn Search Scraper: Getting Started
This guide will walk you through setting up and running the LinkedIn Search Scraper for the very first time. We'll go step-by-step to ensure a smooth experience!

🚀 Quick Start Guide (For First-Time Users)
Follow these simple steps to get the scraper up and running on your computer.

Step 1: Install Google Chrome
This scraper uses Google Chrome to browse LinkedIn. If you don't have it, download and install it from here:
Download Google Chrome

Step 2: Install Python (If You Don't Have It)
This script is written in Python.

For Windows/macOS: Download the latest version of Python 3.x (e.g., Python 3.10, 3.11, or 3.12) from the official website: Download Python
IMPORTANT for Windows: During installation, make sure to check the box that says "Add Python to PATH". This is crucial!
For Linux: Python 3 is usually pre-installed. You can check by opening your terminal and typing python3 --version.
Step 3: Download the Scraper Files
You need to get the actual scraper code onto your computer.

Click this link to download the entire project as a ZIP file: Download Scraper (ZIP) (Note: Replace https://github.com/your-username/your-repository-name/archive/main.zip with the actual download link to your GitHub repository's main branch.)
Unzip the downloaded file. You'll get a folder like your-repository-name-main.
Open this unzipped folder. You should see files like your_script_name.py (your main Python file) and requirements.txt.
Step 4: Install ChromeDriver (Crucial Step!)
Selenium needs a special program called ChromeDriver to control your Chrome browser. It must match your Chrome browser's version.

Find your Chrome browser version:

Open Google Chrome.
Click the three dots (⋮) in the top-right corner.
Go to Help > About Google Chrome.
Note down the exact version number (e.g., 125.0.6422.112).
Download the correct ChromeDriver:

Go to the official ChromeDriver download page: ChromeDriver Downloads
Look for the section that matches your Chrome version. For example, if your Chrome is 125.0.6422.112, look for "v125.0.6422.112".
Under the "Stable" version (or the one matching your Chrome), find the "ChromeDriver" link.
Choose the download link for your operating system:
chromedriver-win64.zip for 64-bit Windows
chromedriver-mac-arm64.zip for newer Macs (M1/M2/M3 chip)
chromedriver-mac-x64.zip for older Macs (Intel chip)
chromedriver-linux64.zip for Linux
Extract ChromeDriver:

Unzip the downloaded chromedriver-*.zip file. You will find a file named chromedriver.exe (Windows) or chromedriver (macOS/Linux) inside.
Place ChromeDriver in the Scraper Folder:

Copy the chromedriver (or chromedriver.exe) file you just extracted.
Paste this file into the same folder where your your_script_name.py and requirements.txt files are located. This is the simplest way for the script to find it.
Step 5: Install Python Dependencies
The scraper uses specific Python libraries. You need to install them.

Open your terminal or Command Prompt:

Windows: Search for cmd or Command Prompt in your Start menu.
macOS/Linux: Open the Terminal application.
Navigate to your scraper folder:

In the terminal, type cd (note the space after cd) and then drag and drop your scraper folder (the one containing your_script_name.py) directly into the terminal window. This will automatically fill in the path.
Press Enter.
You should now see your terminal prompt change to show that you are inside that folder.
Install the required libraries:

In the terminal, type the following command and press Enter:
Bash

pip install -r requirements.txt
You will see text scrolling as the libraries are installed. Wait until it finishes.
Step 6: Run the Scraper!
Now you're ready to go!

Make sure your terminal or Command Prompt is still in your scraper folder (from Step 5).

Run the script:

Bash

python your_script_name.py
(Again, replace your_script_name.py with the actual file name).

Follow the on-screen prompts:

The script will ask for your LinkedIn Email and Password. Type them carefully. Your password will be hidden.
A Chrome browser window will open and attempt to log in to LinkedIn.
Important: If LinkedIn asks for Two-Factor Authentication (2FA) or shows a security check in the browser, complete it manually in the Chrome window. The script will wait for you. Press Enter in the terminal after you've manually completed any browser checks.
Once logged in, the script will ask for the first page URL of a LinkedIn search (e.g., https://www.linkedin.com/search/results/people/?keywords=software%20engineer%20london). Copy this from your browser's address bar after performing a search on LinkedIn.
It will then ask for the number of pages to scrape (e.g., 5 or all).
Finally, provide a filename for your results (e.g., london_engineers.csv).
Monitor the progress: The script will print messages to the terminal as it scrapes each page.

Find your results: Once the scraping is complete, a .csv file with the data will be saved directly into your scraper folder!

What to do if something goes wrong?
"chromedriver executable needs to be in PATH": Go back to Step 4 and double-check you downloaded the correct version of ChromeDriver for your Chrome browser and placed it in the same folder as the script.
Script opens Chrome but doesn't log in:
Check your internet connection.
Double-check your LinkedIn email and password (ensure no typos).
If LinkedIn requires 2FA or a security check in the browser, complete it manually in the Chrome window first, then press Enter in your terminal as instructed.
Script runs, but the CSV is empty or missing data:
LinkedIn frequently changes its website structure. The scraping rules inside the script (scrape_current_page function) might be outdated. This is harder to fix for a first-time user and might require someone with web scraping experience to update the code.
Make sure the LinkedIn search URL you provided is a valid "people" search results page.
"pip is not recognized" or "python is not recognized": Go back to Step 2 and ensure Python was installed correctly and "Add Python to PATH" was checked (on Windows). You might need to restart your terminal/Command Prompt after installing Python.