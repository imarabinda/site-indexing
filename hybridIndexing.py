import logging
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build 
from googleapiclient.http import BatchHttpRequest
import httplib2
import json
import advertools as adv
import pandas as pd
import warnings
import time
warnings.filterwarnings("ignore")

# Enter your XML Sitemap
sitemap = ""

# Enter your csv file path, csv file must contain url and request_type column
csv_path = ""

# JSON api key file path
JSON_KEY_FILE = "site-indexing-346915-88d2e7c5b264.json" 

# Time in seconds the script should wait between requests.
SLEEP = 1.0

# task name (optional), don't leave blank
TASK_NAME = "indexing"

# default request type for all urls.
REQUEST_TYPE = "URL_UPDATED"

# specific urls
URLs = [
    'https://imarabinda.in/contact',
]

# add specific url to remove from request.
EXCLUDE_URLS =[]

# add specific url to overwrite default request type.
OVERWRITE_URLS = {
    # i.e 'url':'request type'
} 

# result file name
RESULT_FILE_NAME = "indexing_result.csv"


#Don't change anything after this. If you don't know what you're doing.
SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# logging config
def setup_log(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = f"./{name}_logs.log"
    log_handler = logging.FileHandler(log_file,'w')
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    return logger

logger = setup_log(TASK_NAME)

url_statuscodes = []


def get_from_sitemap(site):
    global URLs
    if site:
        #get all urls from sitemap
        logger.info("Getting sitemap urls from `%s`....",site)
        sitemap = adv.sitemap_to_df(site)
        sitemap = sitemap.dropna(subset=["loc"]).reset_index(drop=True)
        url_list = list(sitemap['loc'].unique())
        logger.info("All Sitemap urls listed....")
        time.sleep(SLEEP)
        URLs = URLs + url_list

def get_from_csv(csv_path):
    if csv_path: 
        global OVERWRITE_URLS
        csv = pd.read_csv(csv_path)
        for index, row in csv.iterrows():
            URLs.append(row['url'])
            if 'request_type' in row and row['request_type'] != REQUEST_TYPE:
                OVERWRITE_URLS[row['url']] = row['request_type']
        

def filter_and_send():
    logger.info("Excluding URLs if available....")
    for index, url in enumerate(URLs):
        if url in EXCLUDE_URLS:
            URLs.pop(index)
            logger.info("url `%s` removed ....",url)
    urls = pd.Series(URLs, name='A').unique()
    if urls:
        sendIndexRequest(urls)
    else:
        logger.info("url list is empty...")

def insert_event(request_id, response, exception):
    if exception is not None:
      logger.warning(exception)
    else:
      store_in_csv(request_id, response)
      logger.info(response)

def store_in_csv(request_id,response):
    for key,value in response.items():
        url_statuscodes.append([request_id, value['url'], value['latestUpdate']
                                ['type'], value['latestUpdate']['notifyTime']])

def sendIndexRequest(urls):
    # Authorize credentials
    logger.info("Authorizing...")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    # Build service
    service = build('indexing', 'v3', credentials=credentials)
    logger.info("Authorized for indexing...")
    batch = service.new_batch_http_request(callback=insert_event)
    logger.info("Creating batch request....")
    for url in urls:
        request_type = REQUEST_TYPE
        if url in OVERWRITE_URLS:
            request_type = OVERWRITE_URLS[url]
        batch.add(service.urlNotifications().publish(
            body={"url": url, "type": request_type}))
        logger.info("Adding `%s` url request type `%s`....", url, request_type)
    logger.info("Batch request created....")
    logger.info("Batch request executing...")
    batch.execute()
    logger.info("Batch request execution finished...")

    if(len(url_statuscodes) > 0):
        logger.info("Creating result csv file...")
        url_statuscodes_df = pd.DataFrame(
            url_statuscodes, columns=['Request ID',"URL", "Type", "Notify Time"])
        url_statuscodes_df.to_csv(RESULT_FILE_NAME, index=False)
        logger.info("Result csv file saved...")


def main_engine():
    logger.info('Starting...')
    get_from_sitemap(sitemap)
    get_from_csv(csv_path)
    filter_and_send()
    logger.info("The END...")

main_engine()
