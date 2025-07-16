from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


class HttpRequest:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "urls": ("STRING", {"default": ""}),
            },
            "optional": {
                "contexts": ("JSON", {"forceInput": True})
            },
        }

    CATEGORY = "web"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "JSON")
    RETURN_NAMES = ("Return URL", "Page Text", "Page Raw", "Browser Context")
    FUNCTION = "httpRequest"

    async def httpRequest(self, urls, contexts=[]):
        print(urls, contexts)
        urlsOut = []
        textsOut = []
        contentsOut = []
        contextsOut = []
        if not isinstance(urls, list):
            urls = [urls]
        if not isinstance(contexts, list):
            contexts = [contexts]

        ap = async_playwright();
        p = await ap.start()
        #with sync_playwright() as p:
        if True:
            browser = await p.chromium.launch(headless=False)
            browser_context = await browser.new_context()
            for index, url in enumerate(urls):
                if len(contexts) > index:
                    browser_context = await browser.new_context(storage_state=contexts[index])
                    page = await browser_context.new_page()
                elif index == 0:
                    page = await browser_context.new_page()
                await page.goto(url, {'timeout': 120000})
                await page.wait_for_load_state()
                await urlsOut.append(page.url)
                await textsOut.append(page.inner_text("html"))
                await contentsOut.append(page.content())
                if len(contexts) < 2:
                    contextsOut = [await browser_context.storage_state()]
                else:
                    contextsOut.append(await browser_context.storage_state())
            await browser.close()

        if len(urlsOut) == 1:
            return (
                urlsOut[0],
                textsOut[0],
                contentsOut[0],
                contextsOut[0],
            )
        return (
            urlsOut,
            textsOut,
            contentsOut,
            contextsOut,
        )


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
    DESCRIPTION = "Logs into a webpage, loginLocators should be a JSON object with keys 'username', 'password', and 'loginButton' that correspond to the input field names and button ID on the login page."

    async def doLogin(self, url, username, password, loginLocators):
        ap = async_playwright();
        p = await ap.start()
        #with sync_playwright() as p:
        if True:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url)
            # page.fill(f"input[name='{loginLocators['username']}']", username)
            # page.fill(f"input[name='{loginLocators['password']}']", password)
            # page.locator(f'#{loginLocators['loginButton']}').click()
            await page.locator(loginLocators['username']).fill(username)
            await page.locator(loginLocators['password']).fill(password)
            await page.locator(loginLocators['loginButton']).click()
            await page.wait_for_load_state()
            await page.wait_for_load_state(state="networkidle")
            return_url = page.url
            page_text = await page.inner_text("html")
            page_raw = await page.content()
            context = await page.context.storage_state()
            await browser.close()

        return (
            return_url,
            page_text,
            page_raw,
            context,
        )
