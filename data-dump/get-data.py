from html.parser import HTMLParser

from datetime import datetime
from time import sleep

import requests, json, sys, argparse, re

CAPI="http://content.guardianapis.com/search"
TOTAL_PAGES=None

# set up the command line args
parser = argparse.ArgumentParser(description="./get-data.py")
parser.add_argument('--api-key', type=str, dest="api_key",
                    required=True,
                    help="API Key for accessing CAPI")
parser.add_argument('--resume-point', type=int, default=1,
                    dest="current_page", help="The page to resume fetching from")
parser.add_argument('--content-type', type=str, default="article", dest="content_type",
                    help="The content-type to fetch, defaults to article")
parser.add_argument('--dump-file', type=str, dest="dump_file",
                    help="Optional file to output to, defaults to capi-dump + the current isotime")


class Stripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = Stripper()
    s.feed(html)
    return s.get_data()


def buildDumpFileName(content_type):
    return "capi-dump-" + content_type + "-" + datetime.now().isoformat()


def fetchContent(page, dump_file, api_key, content_type):
    params = {'api-key': api_key, 'page-size': '50',
              'page': page, 'show-fields': 'body',
              'type': content_type}

    response = requests.get(CAPI, params=params)

    if response.status_code == 503 or response.status_code == 400:
        print("Got 503 or 400 status code ... retrying ...")
        sleep(2)
        return fetchContent(page, dump_file, api_key, content_type)

    json_data = json.loads(response.text)['response']

    print(json_data['pages'])

    stripped = ""
    for content in json_data['results']:
        if 'fields' in content:
            stripped += strip_tags(content['fields']['body'])


    return stripped

def getTotalPages(apiKey):
    params = {'api-key': apiKey, 'page-size': '50',
              'type': 'article'}
    response = requests.get(CAPI, params=params)
    json_data = json.loads(response.text)['response']
    return json_data['pages']

def writeToFile(dump_file, contents):
    with open(dump_file, "a+", encoding='utf-8') as myfile:
        myfile.write(contents)


if __name__ == "__main__":
    args = vars(parser.parse_args())

    totalPages = getTotalPages(args['api_key'])
    currentPage = args['current_page']

    dumpFileName = ""
    if not args['dump_file']:
        dumpFileName = buildDumpFileName(args['content_type'])
    else:
        dumpFilename = args['dump_file']


    print("Fetching total: " + str(totalPages))
    while currentPage <= totalPages:
        data = fetchContent(currentPage, dumpFileName, args['api_key'], args['content_type'])

        print ("Writing page " + str(currentPage) + " to " + dumpFileName)

        currentPage += 1
        writeToFile(dumpFileName, data)
        if currentPage % 10 == 0:
            sleep(1)

    print ("Done...")
