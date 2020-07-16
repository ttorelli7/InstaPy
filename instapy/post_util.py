""" Module that handles the post features """
import pyautogui
from time import sleep
from .util import update_activity
from selenium.webdriver.common.action_chains import ActionChains
import os
from pathlib import Path
import glob
import pathlib

def delete_folder(pth) :
    for sub in pth.iterdir() :
        if sub.is_dir() :
            delete_folder(sub)
        else :
            sub.unlink()
    pth.rmdir() # if you just want to delete dir content, remove this line

def post_media(browser, file="", caption=""):
    new_post_btn = browser.find_element_by_xpath("//div[@role='menuitem']").click()
    #sleep(3)
    pyautogui.write(file)
    pyautogui.press('return')
    next_btn = browser.find_element_by_xpath("//button[contains(text(),'Next')]").click()
    #sleep(1)
    caption_field = browser.find_element_by_xpath("//textarea[@aria-label='Write a caption…']")
    caption_field.send_keys(caption)
    share_btn = browser.find_element_by_xpath("//button[contains(text(),'Share')]").click()
    sleep(5)

def post_media_by_path(browser, path=""):
    last_id_file = str(path) + "/last_media_published_id.txt"
    last_id = 0

    if os.path.exists(last_id_file):
        f_in = open(last_id_file, "r+")
        last_id = int(f_in.read())
        f_in.close()

    folders = reversed(sorted(Path(path).iterdir(), key=os.path.dirname))
    for folder in folders:
        if folder.is_file():
            continue
        current_id = int(str(folder).replace(path, ''))
        if current_id <= last_id:
            continue
        files = sorted(Path(folder).iterdir(), key=os.path.dirname)
        caption = Path(str(folder) + "/caption_new.txt").read_text()
        #print(caption)
        medias = []
        for file in files:
            file_extension = os.path.splitext(file)
            if file_extension[1] not in [".jpg"]:
                continue
            media = str(file)
            medias.append(media)
        if len(medias) > 1:
            continue
        for media in medias:
            post_media(browser, media, caption)
        f_out = open(last_id_file, "w+")
        f_out.write(str(current_id))
        f_out.close
        delete_folder(folder)
        break

    #image_path = '/var/www/html/instapost/content/emagrecendonasuacasa/2265745190100786720/1.jpg'
    #input = browser.find_element_by_xpath("//input[@type='file']")
    #browser.execute_script("arguments[0].style.display = 'block';",input)
    #input.send_keys(image_path)

    #ele = browser.find_element_by_xpath("//textarea[@aria-label='New Post']")
    #ele = browser.find_element_by_xpath("//input[@type='file']")
    #browser.execute_script("arguments[0].form.action = 'https://www.instagram.com/create/style/';",ele)
    #browser.execute_script("arguments[0].setAttribute('onchange','this.form.submit()');",ele)
    #browser.find_element_by_xpath("//input[@type='file']").send_keys("/var/www/html/instapost/content/emagrecendonasuacasa/2258497770698771862/1.jpg")