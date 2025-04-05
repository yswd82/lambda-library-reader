from typing import List
from abc import ABCMeta
from playwright.sync_api import sync_playwright, Playwright
from playwright.sync_api._generated import Browser, BrowserContext, Locator, Page
from model import LentItem, ReserveItem

from time import sleep


def create_browser(playwright: Playwright):
    browser: Browser = playwright.chromium.launch(
        headless=False,
        # downloads_path="/tmp",
        args=[
            # "--autoplay-policy=user-gesture-required",
            "--disable-gpu",
            # "--disable-background-networking",
            # "--disable-background-timer-throttling",
            # "--disable-backgrounding-occluded-windows",
            # "--disable-breakpad",
            # "--disable-client-side-phishing-detection",
            # "--disable-component-update",
            # "--disable-default-apps",
            # "--disable-dev-shm-usage",
            # "--disable-domain-reliability",
            # "--disable-extensions",
            # "--disable-features=AudioServiceOutOfProcess",
            # "--disable-hang-monitor",
            # "--disable-ipc-flooding-protection",
            # "--disable-notifications",
            # "--disable-offer-store-unmasked-wallet-cards",
            # "--disable-popup-blocking",
            # "--disable-print-preview",
            # "--disable-prompt-on-repost",
            # "--disable-renderer-backgrounding",
            # "--disable-setuid-sandbox",
            # "--disable-speech-api",
            # "--disable-sync",
            # "--disk-cache-size=33554432",
            # "--hide-scrollbars",
            # "--ignore-gpu-blacklist",
            # "--metrics-recording-only",
            # "--mute-audio",
            # "--no-default-browser-check",
            # "--no-first-run",
            # "--no-pings",
            # "--no-sandbox",
            # "--no-zygote",
            # "--password-store=basic",
            # "--use-gl=swiftshader",
            # "--use-mock-keychain",
            "--single-process",
        ],
    )

    return browser


class LibraryReader(metaclass=ABCMeta):
    URL: str

    def __init__(self, user: str, password: str) -> None:
        self.card: str = user
        self.password: str = password
        self.page: Page = None

    def _login(self) -> Page:
        pass

    @property
    def lent(self) -> list[LentItem]:
        pass

    @property
    def reserve(self) -> list[ReserveItem]:
        pass


class SuginamiLibraryReader(LibraryReader):
    URL = "https://www.library.city.suginami.tokyo.jp/"

    def _login(self, context) -> Page:
        # ログインする
        page: Page = context.new_page()
        page.goto(self.URL)

        page.get_by_role("banner").get_by_role("link", name="利用者ログイン").click()

        page.get_by_role("button", name="ログイン").click()
        page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        # page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("button", name="ログイン").click()

        return page

    @property
    def lent(self) -> list:
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 貸出中に移動
            page.get_by_title("あなたが現在借りている資料です").click()
            page.wait_for_load_state()

            sleep(1)

            # ページをスクレイピング
            elements = page.locator(
                "div.main > table > tbody > tr > td"
            ).all_inner_texts()

            # 8要素で1アイテム
            cnt_unit = 8
            cnt = len(elements) // cnt_unit

            items = []
            for i in range(cnt):
                items.append(
                    LentItem(
                        title=elements[i * cnt_unit + 0],
                        category=elements[i * cnt_unit + 1],
                        checkout_location=elements[i * cnt_unit + 2],
                        checkout_date=elements[i * cnt_unit + 3],
                        return_date=elements[i * cnt_unit + 4],
                        reserved_count=elements[i * cnt_unit + 5],
                        extend_count=elements[i * cnt_unit + 6],
                    )
                )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self) -> list:
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            page.get_by_title("あなたが現在予約している資料です").click()
            page.wait_for_load_state()

            sleep(1)

            # ページをスクレイピング
            elements = page.locator(
                "table#ItemDetaTable > tbody > tr > td"
            ).all_inner_texts()

            # 12要素で1アイテム
            cnt_unit = 12
            cnt = len(elements) // cnt_unit

            # アイテムを作る
            items = []
            for i in range(cnt):
                item = ReserveItem(
                    title=elements[i * cnt_unit + 0],
                    category=elements[i * cnt_unit + 1],
                    receive_location="",
                    notification_method="",
                    reserve_date=elements[i * cnt_unit + 3].split("\n")[0],
                    reserve_rank=elements[i * cnt_unit + 4],
                    reserve_status=elements[i * cnt_unit + 5],
                    reserve_cancel_reason=elements[i * cnt_unit + 6],
                    reserve_expire_date=elements[i * cnt_unit + 7],
                )
                items.append(item)

            context.close()
            browser.close()

            return items


class MinatoLibraryReader(LibraryReader):
    URL = "https://www.lib.city.minato.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"

    def _login(self, context) -> Page:
        page: Page = context.new_page()

        page.goto(self.URL)
        page.get_by_role("link", name="マイ図書館メニューを開きます").click()
        page.get_by_role("link", name="ログイン").click()
        page.get_by_label("利用者番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()
        page.wait_for_load_state()

        return page

    @property
    def lent(self):
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            page.click('a[id="stat-lent"]')
            page.wait_for_load_state()

            # ページをスクレイピング
            locator: Locator = page.locator("div.title > a > strong")
            titles: List[str] = locator.all_inner_texts()

            titles = [title.replace("\u3000", " ") for title in titles]
            tmp: List[str] = page.locator("div.matter").all_inner_texts()
            contents: List[List[str]] = [tmp[i : i + 6] for i in range(0, len(tmp), 6)]

            # アイテムを作る
            items: List = []
            for t, d in zip(titles, contents):
                items.append(
                    LentItem(
                        title=t,
                        category=d[0],
                        checkout_location=d[1].replace("貸出館： ", ""),
                        checkout_date=d[2].replace("貸出日： ", ""),
                        return_date=d[3].replace("返却期日： ", ""),
                        reserved_count=d[4].replace("予約数： ", ""),
                        extend_count=d[5].replace("延長回数： ", ""),
                    )
                )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self):
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            page.click('a[id="stat-resv"]')
            page.wait_for_load_state()

            # ページをスクレイピング
            locator: Locator = page.locator(
                "div.main > div > div > div > div.title > strong"
            )
            titles: List[str] = [
                title.replace("\u3000", " ").lstrip()
                for title in locator.all_inner_texts()
            ]
            categories: List[str] = page.locator("div.intro").all_inner_texts()

            locator2: Locator = page.locator("div.matter")
            tmp: List[str] = locator2.all_inner_texts()
            # tmp: List[str] = page.locator("div.matter").all_inner_texts()
            contents: List[List[str]] = [tmp[i : i + 7] for i in range(0, len(tmp), 7)]

            # アイテムを作る
            items: List = []
            for t, c, d in zip(titles, categories, contents):
                items.append(
                    ReserveItem(
                        title=t,
                        category=c,
                        receive_location="",
                        notification_method="",
                        reserve_date=d[2].replace("予約日:", ""),
                        reserve_rank=d[4].replace("予約順位:", ""),
                        reserve_status=d[5].replace("予約状態:", ""),
                        reserve_expire_date=d[6].replace("取置期限:", ""),
                    )
                )

            context.close()
            browser.close()

            return items


class NerimaLibraryReader(LibraryReader):
    URL = "https://www.lib.nerima.tokyo.jp/"

    def _login(self, context) -> Page:
        # ログイン
        page: Page = context.new_page()
        page.goto(self.URL)
        page.get_by_role("link", name="利用者ログイン").click()
        page.get_by_placeholder("利用者ID").fill(self.card)
        page.get_by_placeholder("パスワード").fill(self.password)
        page.get_by_role("button", name="送信").click()
        page.wait_for_load_state()

        return page

    @property
    def lent(self):
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 表示切替え
            page.click("#ContentLend-tab")
            page.wait_for_load_state()

            # ページをスクレイピング
            items: List[LentItem] = []
            for i in range(1, 20):
                locator: Locator = page.locator(
                    f"#ContentLend > form > div > table > tbody > tr:nth-child({i * 2}) > td"
                )

                # 行の中のテキストを取得できたらアイテムにする
                content: List[str] = locator.all_inner_texts()
                if content:
                    items.append(
                        LentItem(
                            is_extendable=True if content[1] == "延長" else False,
                            title=content[2],
                            category=content[3],
                            checkout_location=content[5],
                            checkout_date=content[6],
                            return_date=content[7],
                        )
                    )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self):
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 表示切替え
            page.click("#ContentRsv-tab")
            page.wait_for_load_state()

            # ページをスクレイピング
            items: List[ReserveItem] = []
            for i in range(1, 20):
                locator: Locator = page.locator(
                    f"#ContentRsv > form > div > table > tbody > tr:nth-child({i}) > td"
                )

                # 行の中のテキストを取得できたらアイテムにする
                content: List[str] = locator.all_inner_texts()

                if content:
                    items.append(
                        ReserveItem(
                            reserve_status=content[1],
                            reserve_rank=content[2],
                            title=content[3],
                            category=content[4],
                            reserve_date=content[6],
                            reserve_expire_date=content[7],
                            receive_location=content[9],
                            notification_method=content[10],
                        )
                    )

            context.close()
            browser.close()

            return items
