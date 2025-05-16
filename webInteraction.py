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
            # if len(contexts) > 0:
            #     browser_context = browser.new_context(storage_state=contexts[0])
            # page = browser_context.new_page()
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
