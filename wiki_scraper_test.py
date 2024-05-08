import requests
from bs4 import BeautifulSoup as sp
import re

def recommand_list(soup):
    mw_content = soup.find("div", class_="mw-content-ltr mw-parser-output")
    mw_headline = soup.find_all("span", class_="mw-headline")
    mw_ul = mw_content.find_all("ul")
    for headline in mw_headline:
        print(headline.text)
        for ul in mw_ul:
            for li in ul.find_all("li"):
                print(li.find("a")['title'])

def goto_(url):
    response = requests.get(url)
    soup = sp(response.text, "html.parser")
    content = soup.find('div', class_="mw-content-ltr mw-parser-output")
    paragraphs = content.find_all('p')[1]
    for paragraph in paragraphs:
        if paragraph.text.strip():
            return paragraph.text.strip()
    return "No content found."

def search_result_info(soup):
    results = []
    for result in soup.find_all("div", class_="mw-search-result-heading"):
        title = result.find("a")['title']
        link = f"https://en.wikipedia.org{result.find('a')['href']}"
        first_paragraph = goto_(link)
        results.append({"title": title, "link": link, "content": first_paragraph})
    return results

def search_wikipedia(key_word):
    key_word = key_word.replace(" ", "+")
    url = f"https://en.wikipedia.org/w/index.php?search={key_word}&title=Special:Search&profile=advanced&fulltext=1&ns0=1"
    print(url)
    response = requests.get(url)
    soup = sp(response.text, "html.parser")

    # 檢查是否有錯誤訊息
    search_result = soup.find("div", class_="mw-search-results-info")
    if search_result and "does not exist" in search_result.text:
        print(search_result.text.strip())
    else:
        return search_result_info(soup)

