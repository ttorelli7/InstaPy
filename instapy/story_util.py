import time
import math
from random import randint
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from .util import click_element
from .util import web_address_navigator
from .util import update_activity
from .util import get_action_delay
from .settings import Settings
from .xpath import read_xpath
import random

import requests


def get_story_data(browser, elem, action_type, logger, simulate=False, comments: list = None):
    """
    get the JSON data from the graphql URL
    output the amount of segments we can watch
    """

    # if things change in the future, modify here:
    query_hash = "cda12de4f7fd3719c0569ce03589f4c4"
    elem_id = ""

    if action_type == "user":
        try:
            reel_id = browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id"
            )
            # correct formating for elem_id
            elem_id = '"' + reel_id + '"'
            # and elem needs to be nothing
            elem = ""
        except WebDriverException:
            try:
                reel_id = browser.execute_script(
                    "return window._sharedData."
                    "entry_data.ProfilePage[0]."
                    "graphql.user.id"
                )
                # correct formating for elem_id
                elem_id = '"' + reel_id + '"'
                # and elem needs to be nothing
                elem = ""
            except WebDriverException:
                logger.error(
                    "---> Sorry, this page isn't available!\t~either "
                    + "link is broken or page is removed\n"
                )
                return {"status": "not_ok", "reels_cnt": 0}
    else:
        reel_id = "tag:{}".format(elem)

    graphql_query_url = (
        "https://www.instagram.com/graphql/query/?query_hash={}"
        '&variables={{"reel_ids":[{}],"tag_names":["{}"],"location_ids":[],'
        '"highlight_reel_ids":[],"precomposed_overlay":false,"show_story_viewer_list":true,'
        '"story_viewer_fetch_count":50,"story_viewer_cursor":"",'
        '"stories_video_dash_manifest":false}}'.format(query_hash, elem_id, elem)
    )

    cookies = browser.get_cookies()
    session = requests.Session()
    csrftoken = ""

    # prepare the cookies for the requests session
    for cookie in cookies:
        all_args = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "secure": cookie["secure"],
            "rest": {"HttpOnly": cookie["httpOnly"]},
            "path": cookie["path"],
        }
        if cookie["name"] == "csrftoken":
            csrftoken = cookie["value"]
        if not (cookie["name"] == "urlgen") and not (cookie["name"] == "rur"):
            all_args["expires"] = cookie["expiry"]

        session.cookies.set(**all_args)

    headers = {"User-Agent": Settings.user_agent, "X-Requested-With": "XMLHttpRequest"}

    data = session.get(graphql_query_url, headers=headers)
    response = data.json()
    update_activity(browser, state=None)

    reels_cnt = 0
    if response["status"] == "ok":
        # we got a correct response from the server
        # check how many reels we got
        media_cnt = len(response["data"]["reels_media"])

        if media_cnt == 0:
            # then nothing to watch, we received no stories
            return {"status": "ok", "reels_cnt": 0}
        else:
            # we got content
            # check if there is something new to watch otherwise we just return 0
            seen = 0
            if (action_type != "tag") and (
                response["data"]["reels_media"][0]["seen"] is not None
            ):
                seen = response["data"]["reels_media"][0]["seen"]
            index = 1
            if simulate is True:
                for item in response["data"]["reels_media"][0]["items"]:
                    if item["taken_at_timestamp"] <= seen:
                        continue
                    else:
                        headers = {
                            "User-Agent": Settings.user_agent,
                            "X-CSRFToken": csrftoken,
                            "X-Requested-With": "XMLHttpRequest",
                            "Content-Type": "application/x-www-form-urlencoded",
                        }
                        response = session.post(
                            "https://www.instagram.com/stories/reel/seen",
                            data={
                                "reelMediaId": item["id"],
                                "reelMediaOwnerId": item["owner"]["id"],
                                "reelId": reel_id,
                                "reelMediaTakenAt": item["taken_at_timestamp"],
                                "viewSeenAt": math.floor(time.time()),
                            },
                            headers=headers,
                        )
                        logger.info("  --> simulated watch reel # {}".format(index))
                        update_activity()
                        index += 1
                        time.sleep(randint(3, 6))
                        reels_cnt += 1
            else:
                story_elem = browser.find_element_by_xpath(
                    read_xpath(
                        watch_story.__name__ + "_for_{}".format(action_type),
                        "explore_stories",
                    )
                )

                click_element(browser, story_elem)

                count = 0
                browser.implicitly_wait(2)
                logger.info("Watching stories...")
                for item in response["data"]["reels_media"][0]["items"]:
                    count += 1
                    #if False:
                    if item["taken_at_timestamp"] <= seen:
                        continue
                    else:
                        reels_cnt += 1
                        index += 1
                        if count == len(response["data"]["reels_media"][0]["items"]):
                            reply_story(browser, comments=comments)
                        time.sleep(1)
                        try:
                            next_elem = browser.find_element_by_xpath('/html/body/div[1]/section/div/div/section/div[1]/div/div/div/div[2]/div/div/button[4]')
                        except NoSuchElementException:
                            try:
                                next_elem = browser.find_element_by_xpath('/html/body/div[1]/section/div/div/section/div[1]/div/div/div/div/div/div[1]/button[4]')
                            except NoSuchElementException:
                                continue
                        click_element(browser, next_elem)
                
                if reels_cnt > 0:
                    try:
                        close_elem = browser.find_element_by_xpath('/html/body/div[1]/section/div/div/section/div[2]/header/div[2]/div[2]/button/span')
                        click_element(browser, close_elem)
                    except:
                        pass

                browser.implicitly_wait(25)

            return {"status": "ok", "reels_cnt": reels_cnt}
    else:
        return {"status": "not_ok", "reels_cnt": 0}

def reply_story(browser, comments: list = None):
    try:
        rand_comment = random.choice(comments)
        comment_input = browser.find_element_by_xpath("//textarea[@placeholder='Send Message']")
        comment_input.send_keys(rand_comment)
        time.sleep(1)
        comment_button = browser.find_element_by_xpath("//button[text()='Send']")
        comment_button.click()
    except NoSuchElementException:
        print("--> Unable to reply story...")

def watch_story(browser, elem, logger, action_type, simulate=False, comments: list = None):
    """
        Load Stories, and watch it until there is no more stores
        to watch for the related element
    """

    # make sure we work with a lower case elem
    elem = elem.lower()

    if action_type == "tag":
        story_link = "https://www.instagram.com/explore/tags/{}".format(elem)

    else:
        story_link = "https://www.instagram.com/{}".format(elem)

    web_address_navigator(browser, story_link)
    # wait for the page to load
    time.sleep(randint(2, 6))
    # order is important here otherwise we are not on the page of the story we want to watch
    story_data = get_story_data(browser, elem, action_type, logger, simulate, comments=comments)

    if story_data["status"] == "not ok":
        raise NoSuchElementException

    if story_data["reels_cnt"] == 0:
        # nothing to watch, there is no stories
        logger.info(
            "no stories to watch (either there is none) or we have already watched everything"
        )
        return 0

    logger.info(
        "watched {} reels from {}: {}".format(
            story_data["reels_cnt"], action_type, elem.encode("utf-8")
        )
    )

    # get the post-story delay time to sleep
    naply = get_action_delay("story")
    time.sleep(naply)

    return story_data["reels_cnt"]
