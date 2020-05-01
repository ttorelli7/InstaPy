""" Module that handles the post features """
import pyautogui
from time import sleep
from .util import update_activity
from selenium.webdriver.common.action_chains import ActionChains
import os
from pathlib import Path
import glob

def post_media(browser, file="", caption=""):
    new_post_btn = browser.find_element_by_xpath("//div[@role='menuitem']").click()
    sleep(1)
    pyautogui.write(file)
    pyautogui.press('return')
    next_btn = browser.find_element_by_xpath("//button[contains(text(),'Next')]").click()
    #sleep(1)
    caption_field = browser.find_element_by_xpath("//textarea[@aria-label='Write a caption…']")
    caption_field.send_keys(caption)
    share_btn = browser.find_element_by_xpath("//button[contains(text(),'Share')]").click()
    sleep(5)

def post_media_by_path(browser, path=""):
    paths = sorted(Path(path).iterdir(), key=os.path.dirname)
    for path in paths:
        if path.is_file():
            continue
        subpaths = sorted(Path(path).iterdir(), key=os.path.dirname)
        for subpath in subpaths:
            if subpath.is_file():
                continue
            #print(subpath)
            os.chdir(subpath)
            caption = ""
            media = ""
            for file in glob.glob("*"):
                file_extension = os.path.splitext(file)
                if file_extension[1] == ".txt":
                    caption = Path(str(subpath) + "/" + str(file)).read_text()
                else:
                    media = str(subpath) + "/" + str(file)
            post_media(browser, media, caption)

    #image_path = '/var/www/html/instapost/content/emagrecendonasuacasa/2265745190100786720/1.jpg'
    #input = browser.find_element_by_xpath("//input[@type='file']")
    #browser.execute_script("arguments[0].style.display = 'block';",input)
    #input.send_keys(image_path)

    #ele = browser.find_element_by_xpath("//textarea[@aria-label='New Post']")
    #ele = browser.find_element_by_xpath("//input[@type='file']")
    #browser.execute_script("arguments[0].form.action = 'https://www.instagram.com/create/style/';",ele)
    #browser.execute_script("arguments[0].setAttribute('onchange','this.form.submit()');",ele)
    #browser.find_element_by_xpath("//input[@type='file']").send_keys("/var/www/html/instapost/content/emagrecendonasuacasa/2258497770698771862/1.jpg")