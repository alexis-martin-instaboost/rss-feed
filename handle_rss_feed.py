import feedparser
import requests
from bs4 import BeautifulSoup
from managers.gpt_manager import GPTManager
from managers.google_manager import GoogleManager
from managers.key_value_store import KeyValueStore
from helpers.logger_setup import setup_logger
import time

logger = setup_logger()

original_article_name = "original_article.txt"
rewritten_article_name = "rewritten_article.txt"

def main(credentials):
    rss_feeds = ["https://www.google.com/alerts/feeds/08699332212152003597/15802767885484395124"]

    while True:
        for feed_url in rss_feeds:
            logger.info("Checking feeds...")
            try:
                handle_rss_feed(credentials, feed_url)
            except Exception as e:
                logger.error(f"Error handling RSS feed {feed_url}: {e}")
        logger.info("sleeping for 1 minute...")
        time.sleep(60)

def handle_rss_feed(credentials, feed_url):
    key_value_store = KeyValueStore()

    stored_feed = key_value_store.get(feed_url)
    fresh_feed = feedparser.parse(feed_url)

    stored_feed_length = len(stored_feed.entries) if stored_feed and stored_feed.entries else 0
    fresh_feed_length = len(fresh_feed.entries)

    if not stored_feed:
        key_value_store.set(feed_url, fresh_feed)

    if fresh_feed_length != stored_feed_length:
        number_of_new_articles = fresh_feed_length - stored_feed_length
        for i in range(number_of_new_articles):
            new_article = fresh_feed.entries[i]
            process_rss_feed(credentials, new_article)


def process_rss_feed(credentials, entry):
    title = get_title(entry)

    # Extract the real article URL from the Google search result URL
    article_url = entry.link
    if article_url:
        logger.info(f"URL: {article_url}")

        # Get the content of the article
        article_content = get_article_content(article_url)

        if article_content:
            rewritten_article = get_rewritten_article(article_content)
            # save_content_to_files(article_content, rewritten_article)
            handle_google_docs(credentials, title, rewritten_article)
    else:
        logger.error("No entries in the feed.")

def save_content_to_files(original_content, rewritten_content):
    save_to_file(original_content, original_article_name)
    save_to_file(rewritten_content, rewritten_article_name)

def save_to_file(content, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

def get_rewritten_article(article_content):
    gpt_manager = GPTManager()
    rewritten_article = gpt_manager.rewrite_article(article_content)
    rewritten_article += "\n\n"
    return rewritten_article

def get_title(entry):
    html_string = entry.title

    soup = BeautifulSoup(html_string, 'html.parser')
    raw_text = soup.get_text()

    title = raw_text
    logger.info(f"Title: {title}")
    return title + "\n\n"

def get_article_content(url):
    try:
        # Define a user agent to mimic a popular browser (in this case, Chrome)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        # Make a GET request using the requests library with custom headers
        response = requests.get(url, headers=headers)
        logger.info(f"response: {response}")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Use BeautifulSoup for parsing HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"soup: {soup}")

            # Check if there's a redirect script in the HTML
            redirect_meta = soup.find('meta', {'http-equiv': 'refresh', 'content': True})
            if redirect_meta:
                # Extract the redirect URL from the meta tag
                content = redirect_meta.get('content')
                if content:
                    # Split the content to get the URL after "url="
                    redirect_url = content.split('url=')[-1]
                    logger.info(f"Redirect URL: {redirect_url}")
                    response = requests.get(redirect_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    soup = BeautifulSoup(response.text, 'html.parser')
                    logger.info(f"soup: {soup}")

                # Remove any <script> elements from the HTML bodysa
                if soup.body:
                    for script in soup.body.find_all('script'):
                        script.decompose()

                    # Get the remaining HTML body content
                    body_content = soup.body.get_text(separator='\n', strip=True)
                else:
                    body_content = None

                return body_content
            else:
                logger.error(f"Failed to get redirect_meta")
                return None
        else:
            logger.error(f"HTTP Error {response.status_code}: {response.reason}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None

def handle_google_docs(credentials, title, rewritten_article):
    google_token = credentials["token"]

    key_value_store = KeyValueStore()
    document_id = key_value_store.get("document_id")
    # document_id = "1zuSzwddr5_egzbkXRgrh6yXhcrfBXIxZWqlWN_6s2c0"
    if not document_id:
        logger.warning("No document_id found, creating new document")
        document_id = handle_create_google_doc(google_token)
    update_google_doc(title, google_token, document_id, rewritten_article)

def handle_create_google_doc(google_token):
    document_id = create_google_doc(google_token)
    
    if document_id:
        logger.info(f"Document created, setting document_id in key value store: {document_id}")
        key_value_store = KeyValueStore()
        key_value_store.set("document_id", document_id)
        return document_id
    else:
        logger.error("Failed to create document")
        return

def create_google_doc(google_token):
    google_manager = GoogleManager()
    document_title = "RSS-FEED"
    logger.info(f"Creating document with title: {document_title}")
    return google_manager.create_document(google_token, document_title)

def update_google_doc(title, google_token, document_id, document_content):
    google_manager = GoogleManager()
    logger.info(f"Updating document with document_id: {document_id}")
    google_manager.update_document(title, google_token, document_id, document_content)