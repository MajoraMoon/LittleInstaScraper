from config import username, password, urlSite_toScrap, folder_path
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import wget
import os
import hashlib


options = webdriver.ChromeOptions()

options.add_experimental_option("detach", True)


# The extra options are for keeping the window open after the script has finished executing
# And yes, Chrome is used as the driver. Change it for your liking too :)
driver = webdriver.Chrome(
    options=options, service=Service(ChromeDriverManager().install())
)

driver.get("https://www.instagram.com/")

driver.maximize_window()
sleep(10)


# Note the 2fa verification below
def loginInstagram(u, p):

    cookie_decline = driver.find_element(
        By.XPATH,
        "/html/body/div[4]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[2]",
    ).click()

    # cookies needs some time to close themselves...
    sleep(5)

    usernameInput = driver.find_element(
        By.XPATH,
        '//*[@id="loginForm"]/div/div[1]/div/label/input',
    ).send_keys(u)
    sleep(2)

    passwordInput = driver.find_element(
        By.XPATH,
        '//*[@id="loginForm"]/div/div[2]/div/label/input',
    ).send_keys(p)
    sleep(2)

    login = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button/div",
    )
    sleep(2)
    login.click()

    # sleep for 30 seconds to copy or type the 2 factor authentification because security is nice ;)
    # Even if it's an automated process, put your code inside, I don't care lol

    sleep(30)


# I'm not that good at structure this stuff, so that's why this function exists
def ChangeToDesiredPage(url):

    driver.switch_to.new_window("tab")
    driver.get(url)
    sleep(10)


# The easiest method I saw is to download the images like that. It's downloading the images,
# scrolling down and downloads the images again. Insta isn't easy lol. But I'm sure there is a better way.
def download_images(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src")
            image_name = src.split("/")[-1]
            image_path = os.path.join(folder_path, image_name)
            if not os.path.exists(image_path):
                try:
                    # download the image
                    wget.download(src, out=folder_path)
                except:
                    pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# The method to download the images is not the best, because it is downloading images two times.
# So I thought instead of fixing the problem of doubled downloaded pictures by adjusing the scroll
# height or something else, I would just remove the duplicates. In simple terms, the function creates
# hashes of the picures, then these hashes get compared to each other and if a hash is two times there,
# one of the double hashes, better say pictures, gets deleted. sorry for my english...
# Hashes are super!


def removeDuplicates(directory):
    hashes = set()

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        digest = hashlib.sha1(open(path, "rb").read()).digest()
        if digest not in hashes:
            hashes.add(digest)
        else:
            os.remove(path)


# first login on the basic Instagram page. It's easier to login and open a new page than using Instagrams search..
loginInstagram(username, password)
ChangeToDesiredPage(urlSite_toScrap)
download_images(folder_path)
removeDuplicates(folder_path)
