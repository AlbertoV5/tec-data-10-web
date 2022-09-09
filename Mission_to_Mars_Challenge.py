# %%
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# %%
# Set the executable path and initialize Splinter
executable_path = {"executable_path": ChromeDriverManager().install()}
browser = Browser("chrome", **executable_path, headless=False)

# %% [markdown]
# ### Visit the NASA Mars News Site

# %%
# Visit the mars nasa news site
url = "https://redplanetscience.com/"
browser.visit(url)

# Optional delay for loading the page
browser.is_element_present_by_css("div.list_text", wait_time=1)

# %%
# Convert the browser html to a soup object and then quit the browser
html = browser.html
news_soup = soup(html, "html.parser")

slide_elem = news_soup.select_one("div.list_text")

# %%
slide_elem.find("div", class_="content_title")

# %%
# Use the parent element to find the first a tag and save it as `news_title`
news_title = slide_elem.find("div", class_="content_title").get_text()
news_title

# %%
# Use the parent element to find the paragraph text
news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
news_p

# %% [markdown]
# ### JPL Space Images Featured Image

# %%
# Visit URL
url = "https://spaceimages-mars.com"
browser.visit(url)

# %%
# Find and click the full image button
full_image_elem = browser.find_by_tag("button")[1]
full_image_elem.click()

# %%
# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, "html.parser")
img_soup

# %%
# find the relative image url
img_url_rel = img_soup.find("img", class_="fancybox-image").get("src")
img_url_rel

# %%
# Use the base url to create an absolute url
img_url = f"https://spaceimages-mars.com/{img_url_rel}"
img_url

# %% [markdown]
# ### Mars Facts

# %%
df = pd.read_html("https://galaxyfacts-mars.com")[0]
df.head()

# %%
df.columns = ["Description", "Mars", "Earth"]
df.set_index("Description", inplace=True)
df

# %%
df.to_html()

# %% [markdown]
# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

# %% [markdown]
# ### Hemispheres

# %%
# We are going to help vscode with lists of soups
from typing import List


def get_jpeg(element: soup) -> str:
    """Find the link for jpeg in a given downloads element."""
    links: List[soup] = element.find_all("a", target="_blank")
    return [a.get("href") for a in links if a.get_text() == "Sample"][0]


def visit_content(browser, element: soup) -> soup:
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


def get_items(browser, element: soup):
    """Iterate over all thumbnail divs in given element.
    Returns iterator of dict of title, url."""
    items: List[soup] = element.find_all("div", class_="item")
    for item in items:
        try:
            content: soup = item.find("div", class_="description")
            downloads = visit_content(browser, content)
            # for use with list comprehensions
            yield {
                "img_url": f"{url}{get_jpeg(downloads)}",
                "title": content.find("h3").get_text(),
            }
        except BaseException as e:
            print(f"Could not get src image from {item}", e)


def get_image_urls():
    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)
    # 1. Use browser to visit the URL
    url = "https://marshemispheres.com/"
    browser.visit(url)

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    sp = soup(html, "html.parser")
    results = sp.find("div", class_="collapsible results")

    # 2. Create a list to hold the images and titles.
    return [img for img in get_items(browser, results)]


# %%
# 5. Quit the browser
browser.quit()
# 4. Print the list that holds the dictionary of each image url and title.

# %%
