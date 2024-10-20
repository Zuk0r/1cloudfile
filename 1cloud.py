import pyfiglet
import requests
import os
import random
import string
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
import time


init(autoreset=True)


VALID_URLS_FILE = "valid_1cloudfile_urls.txt"
INVALID_URLS_FILE = "trash_urls.txt"
CHECKED_URLS_FILE = "checked_urls.txt"


BASE_URLS = [
    "https://1cloudfile.com/"
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.1.0; Nexus 5X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
]


INVALID_URL_REDIRECTS = [
    "https://1cloudfile.com/error?e=File+has+been+removed",
    "https://1cloudfile.com/error?e=File+has+been+removed+by+the+site+administrator",
    "https://1cloudfile.com/error?e=File+has+been+removed+due+to+inactivity.",
    "https://1cloudfile.com/error?e=File+has+been+removed+due+to+copyright+issues.",
    "https://1cloudfile.com/error?e=File+has+been+removed+by+the+site+administrator.",
    "https://1cloudfile.com/error?e=File+has+been+removed.",
    "https://1cloudfile.com/error?e=File+is+not+publicly+available."
]

def load_checked_urls():
    """Load checked URLs from a file to avoid rechecking them."""
    if os.path.exists(CHECKED_URLS_FILE):
        with open(CHECKED_URLS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def generate_random_1cloudfile_url(base_url, length=4):
    """Generate a random URL."""
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{base_url}{random_chars}"

def save_url_to_file(url, file_name, file_info=None):
    """Save a URL to a specified file, with additional info if provided."""
    with open(file_name, "a") as file:
        if file_info:
            file.write(f"{url} - {file_info}\n")
        else:
            file.write(url + "\n")

def extract_file_name(html_content):
    """Extract the file name from the page content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        return title_text.split(" - ")[0].strip()
    return "Unknown File Name"

def check_1cloud_url(url, checked_urls, valid_url_count, delay=1):
    """Check if a URL is valid and retrieve the file name if available."""
    if url in checked_urls:
        print(f"[SKIPPED] {url} - Already checked.")
        return

    user_agent = random.choice(USER_AGENTS)
    headers = {"User-Agent": user_agent}

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        if response.url in INVALID_URL_REDIRECTS:
            print(f"{Fore.RED}[INVALID] {url} - Redirected to file removed error page.")
            save_url_to_file(url, INVALID_URLS_FILE)
        elif response.status_code == 200:
            file_name = extract_file_name(response.text)
            print(f"{Fore.GREEN}[VALID] {url} - File Name: {file_name}{Style.RESET_ALL}")
            save_url_to_file(url, VALID_URLS_FILE, file_name)
            
            valid_url_count.append(1)
        else:
            print(f"{Fore.RED}[INVALID] {url} - Status code {response.status_code}{Style.RESET_ALL}")
            save_url_to_file(url, INVALID_URLS_FILE)

        save_url_to_file(url, CHECKED_URLS_FILE)

    except requests.RequestException as e:
        print(f"{Fore.YELLOW}[ERROR] Failed to check {url}: {e}{Style.RESET_ALL}")
        save_url_to_file(url, INVALID_URLS_FILE)
    
    
    time.sleep(delay)

def main():
    
    ascii_banner = pyfiglet.figlet_format("1Cloud Checker", font="banner3-D")
    print(Fore.MAGENTA + ascii_banner + Style.RESET_ALL)
    print(Fore.MAGENTA + "             Have Fun :)\n" + Style.RESET_ALL)  

    
    num_urls = int(input("Enter the number of random URLs to generate: "))
    num_threads = int(input("Enter the number of threads to use: "))
    delay = float(input("Enter delay between URL checks (in seconds): "))
    checked_urls = load_checked_urls()
    
    
    valid_url_count = []

    
    generated_urls = [generate_random_1cloudfile_url(random.choice(BASE_URLS)) for _ in range(num_urls)]

    print("\n[INFO] Checking generated URLs with threading...\n")

    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(check_1cloud_url, url, checked_urls, valid_url_count, delay) for url in generated_urls]
        for i, future in enumerate(futures):
            
            print(f"{Fore.YELLOW}[INFO] Progress: {i+1}/{num_urls} URLs checked.{Style.RESET_ALL}", end='\r')
            future.result()

    
    print(f"\n\n{Fore.BLUE}[INFO] Total Valid URLs Found: {len(valid_url_count)}{Style.RESET_ALL}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
