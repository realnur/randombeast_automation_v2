import asyncio
from patchright.async_api import async_playwright


class AutomationDisposableUrlWithPlaywright:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        if not self.browser:
            await self.start()
        self.context = await self.browser.new_context()

    async def single_threaded_context(self, gift_link):
        self.page = await self.context.new_page()
        await self.page.goto(gift_link, timeout=900000)
        #await self.page.wait_for_timeout(10000000)
        # это самый эффективный
        # и безопасный вариант
        # проверит каждый раз
        # наличие элемента - завершен  и тд
        # чем запихнув в функцию
        # без головной боли
        while True:
            if await self.page.locator("//p[@class='text-center mb-0 drawjoin_infoblock']").count() > 0:
                return False
            await asyncio.sleep(2)
        ###########################
    async def open_captcha(self):
        try:
            await self.page.locator("//button[@class='but accent w-100 mt-2']").click(timeout=15000)
            return True
        except:
            return False
    async def screenshot_captcha(self):
        captcha_image = self.page.locator("//img[@alt='Captcha']")
        await captcha_image.wait_for(state="visible",timeout=60000)
        await captcha_image.screenshot(path="captcha_png/entrance.png")
        await asyncio.sleep(2)
    async def bypass_captcha(self, captcha_code):
        await self.page.locator("(//input[@maxlength='1'])[1]").click()
        await self.page.keyboard.type(f"{captcha_code}", delay=1500)
        await self.page.locator("//span[text()='Подтвердить']").click()
        await asyncio.sleep(2)
    async def reload_captcha(self):
        await self.page.locator("//span[@class='iconify i-mdi:refresh refresh_button_icon']").click()
        await asyncio.sleep(2)
    async def check_true_captcha(self):
        await asyncio.sleep(5)
        if await self.page.locator("//div[text()='Осталось попыток: 2']").count() < 1:
            return True
        return False
    async def close_context(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def max(self):
        if await self.page.locator("//button[@class='but accent small lightray niceborder h-auto']").count() > 0:
            await self.page.locator("//button[@class='but accent small lightray niceborder h-auto']").click()
            await self.page.locator("//button[@class='but lightened small lightray niceborder h-auto']").click()
            await asyncio.sleep(1)
            return True
        return False
