# --- Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re # Import regex for cleaning
import getpass # Import for hidden password input
import os # Import os for path operations (like checking filename)

class LinkedInScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome() # Ensure ChromeDriver is accessible
        self.current_search_data = [] # Data for the current search only
        self.wait = WebDriverWait(self.driver, 15) # Standard wait timeout

    def login(self):
        # Using WebDriverWait for more reliable login
        try:
            self.driver.get("https://www.linkedin.com/login")
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(self.username)
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            print("Login submitted. Waiting for feed/main page load...")
            self.wait.until(EC.presence_of_element_located((By.ID, "global-nav-search")))
            print("Login successful.")
        except TimeoutException:
             print("Login timed out or failed. Element indicating successful login not found.")
             print("Please check the browser for 2FA or other issues.")
             input("Press Enter after manually completing login/2FA if needed...")
             try:
                 self.wait.until(EC.presence_of_element_located((By.ID, "global-nav-search")))
                 print("Login confirmed after manual intervention.")
             except TimeoutException:
                 print("Still unable to confirm login. Exiting.")
                 self.close()
                 raise SystemExit
        except Exception as e:
            print(f"Error during login: {e}")
            self.close()
            raise

    def clear_current_search_data(self):
        """Resets the data list for a new search."""
        self.current_search_data = []
        print("Cleared data for the new search.")

    # scrape_current_page now uses selectors from the user's working script
    def scrape_current_page(self):
        """Scrapes profiles from the currently loaded page and adds unique ones (for this search) to self.current_search_data."""
        try:
            # --- Robust Scrolling Logic ---
            print("Scrolling down page...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 5 # Increased attempts for potentially slow loading pages
            stable_count = 0 # Counter for consecutive stable scrolls
            while scroll_attempts < max_scroll_attempts:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2.5) # Wait for content to potentially load after scroll
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    stable_count += 1
                    if stable_count >= 2: # Consider it stable if height doesn't change for 2 checks
                         print("Scroll height stabilized.")
                         break
                else:
                    last_height = new_height
                    stable_count = 0 # Reset counter if height changes
                scroll_attempts += 1
                if scroll_attempts == max_scroll_attempts:
                    print("Max scroll attempts reached.")
            time.sleep(1) # Final short pause

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            print("Parsing page source...")

            # --- Use Profile Container Selector ---
            # Adjusted based on common LinkedIn structures, but might need tweaking
            # Trying a more general approach that might contain the desired info
            # Often, list items `<li>` within a `<ul>` hold search results
            profile_list_items = soup.select('ul.reusable-search__entity-result-list > li.reusable-search__result-container')

            if not profile_list_items:
                # Fallback or alternative structure check (like the original 'div.linked-area')
                profile_list_items = soup.find_all('div', class_='linked-area') # Your original selector as fallback
                if not profile_list_items:
                    print("No profile containers found using common selectors ('li.reusable-search__result-container' or 'div.linked-area'). Structure might have changed.")
                    # Try finding *any* search result item structure if the specific ones fail
                    potential_results = soup.find_all(lambda tag: tag.name == 'li' and 'result' in tag.get('class', []))
                    if potential_results:
                        print(f"Found {len(potential_results)} potential result items using a generic 'li' search. Attempting to parse...")
                        profile_list_items = potential_results
                    else:
                         print("Could not find any likely profile result containers.")
                         return 0

            count_on_page = 0
            print(f"Found {len(profile_list_items)} potential profile containers/list items. Checking each...")

            for i, item in enumerate(profile_list_items):
                name = None
                title = None
                location = None
                profile_url = None

                try:
                    # --- Profile URL and Name (Often within the same link) ---
                    # Look for the main link containing the name
                    # This selector targets the primary link often associated with the person's name/profile
                    link_tag = item.select_one('span.entity-result__title-text a.app-aware-link')
                    if link_tag:
                        profile_url = link_tag.get('href', '').split('?')[0] # Get URL and clean params
                        # Name is often within spans inside this link
                        name_span = link_tag.select_one('span[aria-hidden="true"]')
                        if name_span:
                            name = name_span.text.strip()
                        else: # Fallback if name is directly in the link text
                            name = link_tag.text.strip()

                    # --- Title Selector ---
                    # Titles are often in a subsequent sibling div or paragraph
                    title_tag = item.select_one('div.entity-result__primary-subtitle')
                    if title_tag:
                        title = title_tag.text.strip()
                    else: # Alternative selector sometimes seen
                        title_tag = item.select_one('p.entity-result__summary') # Check this too
                        if title_tag:
                             title = title_tag.text.strip()


                    # --- Location Selector ---
                    location_tag = item.select_one('div.entity-result__secondary-subtitle')
                    if location_tag:
                        location = location_tag.text.strip()

                    # --- Basic Validation ---
                    # Check if essential info (name, URL) was found and looks like a real profile
                    is_real_profile = (name and profile_url and
                                       name != "LinkedIn Member" and
                                       '/in/' in profile_url and # Typical profile URLs contain /in/
                                       not profile_url.startswith('https://www.linkedin.com/search/')) # Exclude links back to search

                    if is_real_profile:
                        # --- Check for Duplicates *within this search* ---
                        if not any(d['Profile URL'] == profile_url for d in self.current_search_data):
                            self.current_search_data.append({
                                "Name": name,
                                "Title": title,      # Will be None if not found
                                "Location": location,  # Will be None if not found
                                "Profile URL": profile_url,
                            })
                            count_on_page += 1
                        # else: # Optional: uncomment to see which profiles are duplicates *on this page/search*
                        #     print(f"  - Duplicate profile skipped: {name} ({profile_url})")

                except Exception as e_parse:
                    print(f"[WARN] Error parsing one profile container (index {i}): {e_parse}")
                    # Optional: print problematic item's HTML for debugging
                    # print(f"Problematic HTML snippet:\n{item.prettify()}\n--------------------")


            print(f"Finished parsing page. Added {count_on_page} new, unique profiles to this search's data list.")
            return count_on_page

        except Exception as e_scrape:
            print(f"Error scraping current page state: {e_scrape}")
            return 0

    def save_to_csv(self, filename="linkedin_search_data.csv"):
        """Saves the data collected for the *current search* to a specified CSV file."""
        if not self.current_search_data:
            print(f"No data collected for the current search to save to {filename}.")
            return

        print(f"\nAttempting to save data for the current search...")
        try:
            df = pd.DataFrame(self.current_search_data)
            # Ensure final uniqueness check within the search's data before saving
            df.drop_duplicates(subset=['Profile URL'], keep='first', inplace=True)
            # Basic filename validation: ensure it ends with .csv
            if not filename.lower().endswith('.csv'):
                filename += ".csv"
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data for the current search successfully saved to '{filename}' ({len(df)} unique profiles)")
        except Exception as e:
            print(f"Error saving current search data to CSV '{filename}': {e}")

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed.")

# --- Function to sanitize filename ---
def sanitize_filename(name):
    """Removes or replaces characters potentially invalid in filenames."""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace common invalid characters with underscores
    name = re.sub(r'[<>:"/\\|?*]+', '_', name)
    # Replace multiple consecutive underscores with a single one
    name = re.sub(r'_+', '_', name)
    # Ensure it's not empty after sanitization
    if not name:
        name = "unnamed_search"
    return name

# --- Main Execution Logic ---
if __name__ == "__main__":

    # --- Get Credentials Securely ---
    print("-" * 30)
    print("Please enter your LinkedIn credentials:")
    linkedin_username = input("Email: ").strip()
    linkedin_password = getpass.getpass("Password: ").strip()
    print("-" * 30)

    if not linkedin_username or not linkedin_password:
        print("Email and password cannot be empty. Exiting.")
        exit()

    scraper = None # Initialize scraper variable outside try block
    current_search_filename = None # To hold the filename for the current search

    try:
        scraper = LinkedInScraper(linkedin_username, linkedin_password)
        scraper.login() # Attempt login

        # --- Main Interaction Loop ---
        while True:
            start_url = input("\nEnter the FIRST page URL of a LinkedIn search (or type 'quit' to exit): ").strip()

            if start_url.lower() == "quit":
                print("\n'quit' entered. Exiting program.")
                break # Exit the main program loop

            if not start_url.startswith("https://www.linkedin.com/search/results/"):
                print("Invalid URL. Please provide a valid LinkedIn search results page URL (starting with https://www.linkedin.com/search/results/).")
                continue

            # --- Ask for Page Limit for THIS search ---
            user_page_limit = float('inf') # Default to 'all'
            while True:
                limit_input = input("How many pages to scrape for THIS search? (e.g., 5, 10, or type 'all'): ").strip().lower()
                if limit_input == 'all':
                    user_page_limit = float('inf')
                    print("Okay, will scrape all available pages for this search.")
                    break
                else:
                    try:
                        user_page_limit = int(limit_input)
                        if user_page_limit > 0:
                            print(f"Okay, will scrape up to {user_page_limit} pages for this search.")
                            break
                        else:
                            print("Please enter a positive number (like 1, 2, 5...) or 'all'.")
                    except ValueError:
                        print("Invalid input. Please enter a whole number (e.g., 5) or 'all'.")

            # --- Ask for Filename for THIS search ---
            while True:
                raw_filename = input("Enter a filename for THIS search's results (e.g., 'marketing_managers_ny.csv'): ").strip()
                if raw_filename:
                    current_search_filename = sanitize_filename(raw_filename)
                    # Ensure .csv extension
                    if not current_search_filename.lower().endswith('.csv'):
                        current_search_filename += ".csv"
                    print(f"Data for this search will be saved to: '{current_search_filename}'")
                    break
                else:
                    print("Filename cannot be empty.")

            # --- Prepare for New Search ---
            scraper.clear_current_search_data() # Reset data list for the new search

            print(f"\nStarting search from: {start_url}")
            try:
                scraper.driver.get(start_url)
                # Wait for a key element of the results page to appear
                scraper.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.reusable-search__entity-result-list, div.search-results-container"))) # Check for common containers
                print("Initial search results page loaded.")
            except (TimeoutException, Exception) as nav_err:
                print(f"Error navigating to the start URL or loading initial results: {nav_err}")
                print("Please check the URL and your connection. Asking for URL again.")
                current_search_filename = None # Reset filename as this search failed
                continue

            # --- Pagination Loop for THIS search ---
            page_count = 1
            search_successful = True # Flag to track if scraping process completed without major errors
            while page_count <= user_page_limit:
                print(f"\n--- Scraping Page {page_count} for '{current_search_filename}' ---")
                # Optional: Add slight delay before scraping each page
                # time.sleep(random.uniform(1.5, 3.0))
                profiles_found_on_page = scraper.scrape_current_page()

                # Check if user limit reached *after* scraping the target page
                if page_count >= user_page_limit:
                    print(f"Reached user-defined page limit of {user_page_limit} for this search.")
                    break

                # --- Attempt to Paginate ---
                try:
                    next_button_selector = 'button[aria-label="Next"]'
                    # Use presence check first, then check if clickable, more robust
                    scraper.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, next_button_selector)))
                    next_button = scraper.driver.find_element(By.CSS_SELECTOR, next_button_selector)

                    # Check if the button is disabled (often indicates the last page)
                    if next_button.get_attribute("disabled"):
                         print("Next button is disabled. Reached the last available page.")
                         break

                    # Scroll the button into view slightly before clicking (can help)
                    scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.5) # Short pause after scroll

                    # Wait until the button is truly clickable
                    next_button_clickable = scraper.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector)))
                    print("Found 'Next' button, clicking...")
                    scraper.driver.execute_script("arguments[0].click();", next_button_clickable) # Use JS click for reliability

                    # --- Wait for Next Page Load Indicator ---
                    print("Waiting for next page to load...")
                    # It's hard to find a perfect universal indicator. Waiting for the old button
                    # to potentially go stale or for a results container element is common.
                    # Let's try waiting for a slight change or re-appearance of results container
                    time.sleep(2) # Give it a moment to start loading
                    scraper.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.reusable-search__entity-result-list, div.search-results-container")))
                    # Optional: Check if URL changed, though might not always happen reliably
                    # scraper.wait.until(lambda d: start_url not in d.current_url or f"page={page_count+1}" in d.current_url)

                    print("Next page appears to be loaded.")
                    page_count += 1 # Increment only on successful click and load indication

                except TimeoutException:
                    print("No 'Next' button found, clickable, or page didn't load within timeout. Assuming last page reached.")
                    break
                except NoSuchElementException:
                    print("No 'Next' button element found. Reached the last available page.")
                    break
                except Exception as e_button:
                    print(f"Error during pagination attempt: {e_button}")
                    print("Stopping pagination for this search due to error.")
                    search_successful = False # Mark that this search had issues
                    break

            # --- End of Pagination Loop for THIS search ---
            if search_successful:
                if page_count > user_page_limit and user_page_limit != float('inf'):
                    print(f"\nCompleted scraping up to the specified limit of {user_page_limit} pages for '{current_search_filename}'.")
                else: # Reached end naturally or via 'all' pages
                    print(f"\nFinished scraping all available pages for '{current_search_filename}'.")
            else:
                print(f"\nScraping for '{current_search_filename}' stopped due to an error during pagination.")

            # --- Save Data for THIS Search ---
            scraper.save_to_csv(current_search_filename)
            print(f"Total unique profiles collected *for this specific search* ({current_search_filename}): {len(scraper.current_search_data)}")
            current_search_filename = None # Reset for the next loop iteration

        # --- End of Main Interaction Loop ---

    except SystemExit:
        print("Exiting script due to login failure.")
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt detected.")
        # Attempt to save data from the search that was *in progress*
        if scraper and current_search_filename and scraper.current_search_data:
             print(f"Attempting to save data collected so far for '{current_search_filename}'...")
             scraper.save_to_csv(current_search_filename)
        else:
             print("No data from the current search to save.")
    except Exception as e:
        print(f"\nA critical error occurred in the main execution block: {e}")
        # Attempt to save data from the search that was *in progress*
        if scraper and current_search_filename and scraper.current_search_data:
            print(f"Attempting to save any data collected for '{current_search_filename}' before the error...")
            scraper.save_to_csv(current_search_filename)
        else:
            print("No data to save or scraper/filename not available.")
    finally:
        if scraper:
            scraper.close()
        print("\nScript finished.")