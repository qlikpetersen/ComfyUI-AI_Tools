import re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from .utils import AnyType


def removeCircularReferences(spiderDataInput):
    outputData = {}
    print("Creating save structure")
    for page in spiderDataInput:
        if spiderDataInput[page]['url'] == page:
            print(f"Appending {page} to outputData")
            outputData[page] = {
                "links": {},
                "rev_links": {},
            }
            for item in spiderDataInput[page]:
                if item not in outputData[page]:
                    outputData[page][item] = spiderDataInput[page][item]
            for link in spiderDataInput[page]['links']:
                outputData[page]['links'][link] = None
            for link in spiderDataInput[page]['rev_links']:
                outputData[page]['rev_links'][link] = None
        else:
            print(f"Noting {page} points to {spiderDataInput[page]['url']}")
            outputData[page] = spiderDataInput[page]['url']
    return outputData


def fixLinksAndRevLinks(spiderDataInput):
    print("Now fixing links and rev_links")
    for page in spiderDataInput:
        if isinstance(spiderDataInput[page], str):
            spiderDataInput[page] = spiderDataInput[spiderDataInput[page]]
        elif spiderDataInput[page] is not None:
            for link in spiderDataInput[page]['links']:
                if spiderDataInput[page]['links'][link] is None and link in spiderDataInput:
                    spiderDataInput[page]['links'][link] = spiderDataInput[link]
            for link in spiderDataInput[page]['rev_links']:
                if spiderDataInput[page]['rev_links'][link] is None and link in spiderDataInput:
                    spiderDataInput[page]['rev_links'][link] = spiderDataInput[link]
    print("Links fixed.")
    print(f"Total of {len(list(set([spiderDataInput[page]['url'] for page in spiderDataInput])))} individual pages.")
    return spiderDataInput


class SpiderCrawl:
    def __init__(self):
        pass

    downloadables = (
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
        ".ico", ".tiff", ".tif", ".pdf", ".xls", ".xlsx", ".csv",
        ".ods", ".doc", ".docx", ".ppt", ".pptx", ".zip", ".rar",
        ".tar", ".gz", ".7z", ".mp3", ".wav", ".mp4", ".avi", ".mov",
        ".wmv", ".flv", ".mkv", ".exe", ".dmg", ".iso", ".apk", ".msi",
        ".xml", ".json", ".txt", ".css", ".js", ".mso", ".woff", ".woff2",
        ".ttf", ".eot", ".otf", ".webm", ".mpg", ".mpeg", ".3gp",
        ".ogg", ".ogv", ".flac", ".aac", ".m4a", ".opus", ".amr",
        ".swf", ".psd", ".ai", ".indd", ".eps", ".raw", ".cr2",
        ".nef", ".orf", ".arw", ".dng", ".jxr", ".heic", ".heif",
        ".avif", ".webp", ".svgz", ".jsonld", ".md", ".markdown",
        ".yaml", ".yml", ".bat", ".sh", ".ps1", ".cmd", ".vbs",
        ".py", ".rb", ".pl", ".php", ".jsp", ".asp", ".aspx",
        ".cfm", ".thmx"
    )

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
                "depth": ("INT", {"default": 0}),
                "offsite": ("BOOLEAN", {"default": False}),
                "resetContextToBase": ("BOOLEAN", {"default": False}),
                "ignoreQueryParams": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "context": ("JSON", {"forceInput": True})
            },
        }

    CATEGORY = "web"
    RETURN_TYPES = ("SPIDERDATA", "JSON")
    RETURN_NAMES = ("Web Data", "Browser Context")
    FUNCTION = "crawl"

    def crawl(self, url, depth, offsite, resetContextToBase, ignoreQueryParams, context=None):
        print(url, depth, offsite, context, resetContextToBase, ignoreQueryParams)
        url = self.cleanup_urls(url, ignoreQueryParams)
        purl = urlparse(url)
        baseURL = f"{purl.scheme}://{purl.netloc}/"
        webData = {}
        urlsToScrape = [(url, 1)]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            browser_context = browser.new_context()
            if context:
                browser_context = browser.new_context(storage_state=context)
            page = browser_context.new_page()
            while urlsToScrape:
                current_url, current_depth = urlsToScrape.pop(0)
                print(f"URLs to scrape: {len(urlsToScrape)} | Current URL: {current_url} | Depth: {current_depth}")
                if resetContextToBase and current_depth != 0:
                    page.close()
                    if context:
                        browser_context = browser.new_context(storage_state=context)
                    else:
                        browser_context = browser.new_context()
                    page = browser_context.new_page()
                page.goto(current_url, timeout=120000)
                page.wait_for_load_state()
                try:
                    page.wait_for_load_state(state="networkidle")
                except Exception as e:
                    print(f"Warning: wait_for_load_state(networkidle) failed: {e}")
                loadedUrl = self.cleanup_urls(page.url, ignoreQueryParams)
                current_url = self.cleanup_urls(current_url, ignoreQueryParams)
                webData.update({
                    loadedUrl: {
                        "url": loadedUrl,
                        "data": page.content(),
                        "screenshot": page.screenshot(full_page=True),
                        "links": {},
                        "rev_links": {},
                        "depths_found": [current_depth-1],
                    }
                })
                if resetContextToBase:
                    webData[loadedUrl].update({"context": browser_context.storage_state()})
                if loadedUrl != current_url:
                    webData.update({current_url: webData[loadedUrl]})
                for storedPage in webData:
                    if loadedUrl in webData[storedPage]['links']:
                        webData[storedPage]['links'][loadedUrl] = webData[loadedUrl]
                        webData[loadedUrl]['rev_links'][storedPage] = webData[storedPage]
                        webData[loadedUrl]['depths_found'].append(webData[storedPage]['depths_found'][0]+1)

                links = self.extract_links(page.content(), loadedUrl)
                for link in links:
                    cleaned_link = self.cleanup_urls(link, ignoreQueryParams)
                    cleaned_urlsTBS = self.cleanup_urls([sUrl for sUrl, d in urlsToScrape], ignoreQueryParams)
                    if cleaned_link not in webData and cleaned_link not in cleaned_urlsTBS:
                        if (
                            (depth == 0 or current_depth < depth)
                            and (offsite or link.startswith(baseURL))
                            and (not link.startswith('javascript:'))
                            and not any(cleaned_link.lower().endswith(ext) for ext in self.downloadables)
                        ):
                            urlsToScrape.append((link, current_depth + 1))
                        if (not link.startswith('javascript:')):
                            webData[loadedUrl]['links'][cleaned_link] = None
            contextOut = browser_context.storage_state()
            if resetContextToBase:
                contextOut = context
            contextOut = browser_context.storage_state()
            browser.close()

            print("Crawling completed.")
            print("Now fixing links and rev_links")

            for page in webData:
                for link in webData[page]['links']:
                    if link in webData:
                        if webData[page]['links'][link] is None:
                            webData[page]['links'][link] = webData[link]
                        if page not in webData[link]['rev_links']:
                            webData[link]['rev_links'][page] = webData[page]
            print("Links fixed.")
            print(f"Total of {len(list(set([webData[page]['url'] for page in webData])))} individual pages.")
        return (webData, contextOut,)

    def cleanup_urls(self, urls, stripQueryParams=True):
        """
        Cleans up the URL by removing query parameters and trailing slashes.
        """
        outputUrls = []
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            if stripQueryParams:
                parsed_url = urlparse(url)
                cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                outputUrls.append(cleaned_url.rstrip('/'))
        if len(outputUrls) == 1:
            return outputUrls[0]
        return outputUrls

    def extract_links(self, html, original_url=None):
        # Regular expression to find all href links in the HTML content
        link_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, html)

        # Extract URLs from form submissions (action attributes)
        form_action_pattern = r'<form[^>]+action=["\']([^"\']+)["\']'
        form_actions = re.findall(form_action_pattern, html)
        links.extend(form_actions)

        # Extract URLs from JavaScript (e.g., window.location, open, etc.)
        js_url_pattern = r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']|location\.assign\(\s*["\']([^"\']+)["\']\s*\)|location\.replace\(\s*["\']([^"\']+)["\']\s*\)|open\(\s*["\']([^"\']+)["\']'
        js_links = re.findall(js_url_pattern, html)
        # Flatten and filter empty matches
        js_links_flat = [url for url in js_links if url]
        links.extend(js_links_flat)

        # Resolve relative URLs if original_url is provided
        if original_url:
            links = [urljoin(original_url, link) if not link.startswith(('http://', 'https://')) else link for link in links]

        # Remove duplicates
        return list(set(links))


class SaveSpiderData:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename": ("STRING", {"defailt": "SpiderData.spider"}),
                "data": ("SPIDERDATA", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "save_data"
    OUTPUT_NODE = True

    def save_data(self, filename, data):
        outputData = removeCircularReferences(data)
        print(f"Done creating save structure, saving to file... as {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(repr(outputData))
        print("Save Complete!")
        return (filename,)


class LoadSpiderData:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename": ("STRING", {"defailt": "SpiderData.spider"}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ("SPIDERDATA",)
    RETURN_NAMES = ("data",)
    FUNCTION = "load_data"

    def load_data(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = eval(f.read())
        data = fixLinksAndRevLinks(data)
        return (data,)


class RemoveCircularReferences:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("SPIDERDATA", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("dataOut",)
    FUNCTION = "fix_data"
    OUTPUT_NODE = True

    def fix_data(self, data):
        return (removeCircularReferences(data),)


class FixLinksAndRevLinks:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ("SPIDERDATA",)
    RETURN_NAMES = ("data",)
    FUNCTION = "fix_data"

    def fix_data(self, data):
        return (fixLinksAndRevLinks(data),)


class SpiderSplit:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("SPIDERDATA", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ("SPIDERDATA",)
    RETURN_NAMES = ("UniquePageData",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "spider_split"
    OUTPUT_NODE = True

    def spider_split(self, data):
        outputData = []
        for page in data:
            if data[page]['url'] == page:
                print(f"Appending {page} to outputData")
                outputData.append({page: data[page]})
        return (outputData,)


class IncludeInSpiderData:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("SPIDERDATA", {"forceInput": True}),
                "itemName": ("STRING", {"default": "LLM"}),
                "newData": (AnyType("*"), {"forceInput": True, "tooltip": "This has to be an itterative run that includes all unique pages"}),
            },
        }

    CATEGORY = "utils"
    INPUT_IS_LIST = (False, False, True)
    RETURN_TYPES = ("SPIDERDATA",)
    RETURN_NAMES = ("spiderDataPlus",)
    FUNCTION = "spider_add"
    OUTPUT_NODE = True

    def spider_add(self, data, itemName, newData):
        data = data[0]
        itemName = itemName[0]
        pages = []
        for page in data:
            if data[page]['url'] == page:
                pages.append(page)

        for page, newItem in zip(pages, newData):
            data[page].update({
                itemName: newItem,
            })

        return (data,)
