# Import Splinter, BeautifulSoup, and Pandas
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as soup
from splinter import Browser
import datetime as dt
import pandas as pd


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    img = featured_image(browser)
    image_list = get_image_urls(browser)
    browser.quit()
    return {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": img,
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "images": image_list,
    }


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = "https://redplanetscience.com/"
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("div.list_text", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, "html.parser")

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("div.list_text")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = "https://spaceimages-mars.com"
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag("button")[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, "html.parser")

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find("img", class_="fancybox-image").get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f"https://spaceimages-mars.com/{img_url_rel}"

    return img_url


def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html("https://galaxyfacts-mars.com")[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns = ["Description", "Mars", "Earth"]
    df.set_index("Description", inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


from typing import List


def get_jpeg(element: soup) -> str:
    """Find the link for jpeg in a given downloads element."""
    links: List[soup] = element.find_all("a", target="_blank")
    return [a.get("href") for a in links if a.get_text() == "Sample"][0]


def visit_content(url: str, browser, element: soup) -> soup:
    """Given an html element, find its href and visit it.
    Returns a div element with class_='downloads' from the new site."""
    try:
        href = element.find("a", class_="itemLink product-item").get("href")
        new_url = f"{url}{href}"  # NOTE: url is a global variable
        browser.visit(new_url)
        page = soup(browser.html, "html.parser")
        return page.find("div", class_="downloads")
    except BaseException as e:
        print(f"Could not visit {new_url}")


def get_items(url: str, browser, element: soup):
    """Iterate over all thumbnail divs in given element.
    Returns iterator of dict of title, url."""
    items: List[soup] = element.find_all("div", class_="item")
    for item in items:
        try:
            content: soup = item.find("div", class_="description")
            downloads = visit_content(url, browser, content)
            # for use with list comprehensions
            yield {
                "img_url": f"{url}{get_jpeg(downloads)}",
                "title": content.find("h3").get_text(),
            }
        except BaseException as e:
            print(f"Could not get src image from {item}", e)


def get_image_urls(browser):
    """From Mission_to_mars.py"""
    url = "https://marshemispheres.com/"
    browser.visit(url)
    sp = soup(browser.html, "html.parser")
    results = sp.find("div", class_="collapsible results")
    return [img for img in get_items(url, browser, results)]


if __name__ == "__main__":
    print(scrape_all())
