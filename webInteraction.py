import re
import torch
import numpy as np
from io import BytesIO
from PIL import ImageOps, Image
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright


class DoLogin:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
                "username": ("STRING", {"default": ""}),
                "password": ("STRING", {"default": ""}),
                "loginLocators": ("JSON", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "JSON")
    RETURN_NAMES = ("Return URL", "Page Text", "Page Raw", "Browser Context")
    FUNCTION = "doLogin"
    CATEGORY = "web"

    def doLogin(self, url, username, password, loginLocators):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            page.fill(f"input[name='{loginLocators['login']}']", username)
            page.fill(f"input[name='{loginLocators['password']}']", password)
            page.locator(f'#{loginLocators['loginButton']}').click()
            page.wait_for_load_state()
            page.wait_for_load_state(state="networkidle")
            return_url = page.url
            page_text = page.inner_text("html")
            page_raw = page.content()
            context = page.context.storage_state()
            browser.close()

        return (
            return_url,
            page_text,
            page_raw,
            context,
        )


class HttpRequest:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "urls": ("STRING", {"default": ""}),
                "depth": ("INT", {"default": 1}),
                "loop_context": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "contexts": ("JSON", {"forceInput": True})
            },
        }

    CATEGORY = "web"
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True, True, True, True)
    RETURN_TYPES = ("STRING", "STRING", "STRING", "JSON")
    RETURN_NAMES = ("Return URL", "Page Text", "Page Raw", "Browser Context")
    FUNCTION = "httpRequest"

    def httpRequest(self, urls, depth, loop_context, contexts=[]):
        print(urls, depth, loop_context, contexts)
        urlsOut = []
        textsOut = []
        contentsOut = []
        contextsOut = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            browser_context = browser.new_context()
            for index, url in enumerate(urls):
                if not loop_context and len(contexts) > 1 and index > 0:
                    browser_context = browser.new_context(storage_state=contexts[index])
                elif not loop_context or (len(contexts) > 0 and index == 0):
                    browser_context = browser.new_context(storage_state=contexts[0])
                if index == 0 or not loop_context:
                    page = browser_context.new_page()
                page.goto(url)
                page.wait_for_load_state()
                page.wait_for_load_state(state="networkidle")
                urlsOut.append(page.url)
                textsOut.append(page.inner_text("html"))
                contentsOut.append(page.content())
                if loop_context:
                    contextsOut = [browser_context.storage_state()]
                else:
                    contextsOut.append(browser_context.storage_state())
            browser.close()

        return (
            urlsOut,
            textsOut,
            contentsOut,
            contextsOut,
        )


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
                "ignoreQueryParams": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "context": ("JSON", {"forceInput": True})
            },
        }

    CATEGORY = "web"
    RETURN_TYPES = ("JSON", "JSON")
    RETURN_NAMES = ("Web Data", "Browser Context")
    FUNCTION = "crawl"

    def crawl(self, url, depth, offsite, ignoreQueryParams, context=None):
        print(url, depth, offsite, context)
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
                page.goto(current_url)
                page.wait_for_load_state()
                # page.wait_for_load_state(state="networkidle")
                loadedUrl = self.cleanup_urls(page.url, ignoreQueryParams)
                current_url = self.cleanup_urls(current_url, ignoreQueryParams)
                webData.update({
                    loadedUrl: {
                        "url": loadedUrl,
                        "data": page.content(),
                        "screenshot": self.convertImage(page.screenshot(full_page=True)),
                        "links": {},
                        "rev_links": {},
                        "depths_found": [current_depth-1],
                    }
                })
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
        return (
            webData,
            contextOut,
        )

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

    def convertImage(self, image):
        """
        Converts an image to Tensor format for ComfyUI.
        """
        image = ImageOps.exif_transpose(Image.open(BytesIO(image))).convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return torch.cat([image], dim=0)
