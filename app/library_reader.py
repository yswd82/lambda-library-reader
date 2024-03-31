from playwright.sync_api import sync_playwright, Playwright
from abc import ABCMeta
from model import LentItem, ReserveItem


def create_browser(playwright: Playwright):
    browser = playwright.chromium.launch(
        # headless=True,
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
    URL = ""

    def __init__(self, user, password) -> None:
        self.card = user
        self.password = password

    @property
    def lent(self) -> list[LentItem]:
        pass

    @property
    def reserve(self) -> list[ReserveItem]:
        pass


class SuginamiLibraryReader(LibraryReader):
    URL = (
        "https://www.library.city.suginami.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"
    )

    @property
    def lent(self):
        with sync_playwright() as playwright:
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="マイ図書館メニューを開きます").click()
            page.get_by_role("link", name="ログイン").click()

            # fill username/password
            page.fill('input[name="username"]', self.card)
            page.fill('input[name="j_password"]', self.password)
            page.get_by_role("button", name="ログイン").click()

            # load page
            page.click('a[id="stat-lent"]')
            page.wait_for_load_state()

            # scraping page
            titles = page.locator("div.title > a > strong").all_inner_texts()
            titles = [title.replace("\u3000", " ") for title in titles]
            tmp = page.locator("div.matter").all_inner_texts()
            contents = [tmp[i : i + 6] for i in range(0, len(tmp), 6)]

            # create items
            items = []
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
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="マイ図書館メニューを開きます").click()
            page.get_by_role("link", name="ログイン").click()
            page.fill('input[name="username"]', self.card)
            page.fill('input[name="j_password"]', self.password)
            page.get_by_role("button", name="ログイン").click()

            # goto page
            page.click('a[id="stat-resv"]')
            page.wait_for_load_state()

            # scraping page
            titles = page.locator("div.title > strong").all_inner_texts()
            titles = [title.replace("\u3000", " ").lstrip() for title in titles]
            categories = page.locator("div.intro").all_inner_texts()
            tmp = page.locator("div.matter").all_inner_texts()
            contents = [tmp[i : i + 9] for i in range(0, len(tmp), 9)]

            # create items
            items = []
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
                        reserve_cancel_reason=d[6].replace("予約取消理由:", ""),
                        reserve_expire_date=d[7].replace("取置期限:", ""),
                    )
                )

            context.close()
            browser.close()

            return items


class MinatoLibraryReader(LibraryReader):
    URL = "https://www.lib.city.minato.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"

    @property
    def lent(self):
        with sync_playwright() as playwright:
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="マイ図書館メニューを開きます").click()
            page.get_by_role("link", name="ログイン").click()
            page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
            page.get_by_label("パスワード", exact=True).fill(self.password)
            page.get_by_role("button", name="ログイン").click()

            # goto page
            page.click('a[id="stat-lent"]')
            page.wait_for_load_state()

            # scraping page
            titles = page.locator("div.title > a > strong").all_inner_texts()
            titles = [title.replace("\u3000", " ") for title in titles]
            tmp = page.locator("div.matter").all_inner_texts()
            contents = [tmp[i : i + 6] for i in range(0, len(tmp), 6)]

            # create items
            items = []
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
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="マイ図書館メニューを開きます").click()
            page.get_by_role("link", name="ログイン").click()
            page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
            page.get_by_label("パスワード", exact=True).fill(self.password)
            page.get_by_role("button", name="ログイン").click()

            # goto page
            page.click('a[id="stat-resv"]')
            page.wait_for_load_state()

            # scraping page
            titles = page.locator(
                "div.main > div > div > div > div.title > strong"
            ).all_inner_texts()
            titles = [title.replace("\u3000", " ").lstrip() for title in titles]
            categories = page.locator("div.intro").all_inner_texts()
            tmp = page.locator("div.matter").all_inner_texts()
            contents = [tmp[i : i + 7] for i in range(0, len(tmp), 7)]

            # create items
            items = []
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
    URL = "https://www.lib.nerima.tokyo.jp/index.html"

    @property
    def lent(self):
        with sync_playwright() as playwright:
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="利用者ログイン").click()
            page.get_by_placeholder("利用者ID").fill(self.card)
            page.get_by_placeholder("パスワード").fill(self.password)
            page.get_by_role("button", name="送信").click()
            page.wait_for_load_state()

            # goto page
            page.click('a[href="#ContentLend"]')
            page.wait_for_load_state()

            # scraping page
            tmp = page.locator(
                "#ContentLend > form > div:nth-child(7) > table > tbody > tr > td"
            ).all_inner_texts()
            contents = [tmp[i : i + 11] for i in range(0, len(tmp), 11)]

            # create items
            items = []
            for c in contents:
                items.append(
                    LentItem(
                        is_extendable=True if c[1] == "延長" else False,
                        title=c[2],
                        category=c[3],
                        checkout_location=c[5],
                        checkout_date=c[6],
                        return_date=c[7],
                    )
                )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self):
        with sync_playwright() as playwright:
            browser = create_browser(playwright)
            context = browser.new_context()

            # login
            page = context.new_page()
            page.goto(self.URL)
            page.get_by_role("link", name="利用者ログイン").click()
            page.get_by_placeholder("利用者ID").fill(self.card)
            page.get_by_placeholder("パスワード").fill(self.password)
            page.get_by_role("button", name="送信").click()
            page.wait_for_load_state()

            # goto page
            page.click('a[href="#ContentRsv"]')
            page.wait_for_load_state()

            # scraping page
            tmp = page.locator(
                "#ContentRsv > form > div:nth-child(9) > table > tbody > tr > td"
            ).all_inner_texts()
            contents = [tmp[i : i + 12] for i in range(0, len(tmp), 12)]

            # create items
            items = []
            for c in contents:
                items.append(
                    ReserveItem(
                        reserve_status=c[1],
                        reserve_rank=c[2],
                        title=c[3],
                        category=c[4],
                        reserve_date=c[6],
                        reserve_expire_date=c[7],
                        receive_location=c[9],
                        notification_method=c[10],
                    )
                )

            context.close()
            browser.close()

            return items
