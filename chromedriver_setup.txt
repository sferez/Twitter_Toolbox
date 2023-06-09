# 1. Update the packages list
sudo apt-get update

# 2. Install unzip and curl (if not already installed)
sudo apt-get install -y unzip curl


# 3. Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install

# 4. Get installed Google Chrome version
chrome_version=$(google-chrome-stable --version | cut -d ' ' -f3 | cut -d '.' -f1)

# 5. Get latest ChromeDriver version corresponding to the installed Google Chrome
chromedriver_version=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$chrome_version")

# 6. Download and unzip ChromeDriver
wget "https://chromedriver.storage.googleapis.com/$chromedriver_version/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip

# 7. Make ChromeDriver executable
chmod +x chromedriver

# 8. Move ChromeDriver to a directory in your PATH so it's easily accessible
sudo mv chromedriver /usr/bin/chromedriver

# 9. Install additional dependencies for running headless Selenium
sudo apt-get install -y xvfb
