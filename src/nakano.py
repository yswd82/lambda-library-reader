from src.library_reader import LibraryReader, create_browser
from src.model import LentItem, ReserveItem

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Page

from time import sleep


class NakanoLibraryReader(LibraryReader):
    """
    杉並区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。

    LibraryReader を継承し、Playwright を用いて自動的にログイン・スクレイピングを行う。

    Attributes:
        URL (str): 杉並区立図書館のトップページURL。
        card (str): 図書館利用カード番号（親クラスで設定）。
        password (str): ログイン用パスワード（親クラスで設定）。
    """

    URL = "https://www.kn.licsre-saas.jp/tokyo-nakano/webopac/usermenu.do?target=adult/"

    def _login(self, context) -> Page:
        """
        杉並区立図書館サイトにログインし、ログイン後のページオブジェクトを返す。

        Args:
            context (BrowserContext): Playwright のブラウザコンテキスト。

        Returns:
            Page: ログイン後のページオブジェクト。
        """
        page: Page = context.new_page()
        page.goto(self.URL)

        page.get_by_label("利用者番号").click()
        page.get_by_label("利用者番号").fill(self.card)
        page.get_by_label("パスワード").click()
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログインする").click()

        return page

    @property
    def lent(self) -> list:
        """
        現在貸出中の資料一覧を取得する。

        Returns:
            list[LentItem]: 貸出中資料の LentItem オブジェクトのリスト。
        """
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 貸出中ページへ移動
            page.get_by_role("link", name="●貸出中一覧").click()
            page.wait_for_load_state()
            sleep(1)

            # ページ内容を取得
            elements = page.locator(
                "#main > form:nth-child(2) > fieldset > div > table > tbody > tr > td"
            ).all_inner_texts()

            elements = [
                e.replace("\t", "").replace("\n", "").replace("\r", "").strip()
                for e in elements
            ]

            # # DEBUG:
            # for i, e in enumerate(elements):
            #     t = e.replace("\t", "").replace("\n", "").replace("\r", "")
            #     # t = e.replace("\n", "").replace("\r", "").strip()
            #     print(i, t)

            # 10要素で1アイテム
            cnt_unit = 10
            cnt = len(elements) // cnt_unit

            items = []
            for i in range(cnt):
                items.append(
                    LentItem(
                        title=elements[i * cnt_unit + 2],
                        category=None,
                        checkout_location=elements[i * cnt_unit + 5],
                        checkout_date=elements[i * cnt_unit + 3],
                        return_date=elements[i * cnt_unit + 4],
                        reserved_count=None,
                        extend_count=None,
                        is_reserved=True
                        if len(elements[i * cnt_unit + 8]) > 0
                        else False,
                    )
                )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self) -> list:
        """
        現在予約中の資料一覧を取得する。

        Returns:
            list[ReserveItem]: 予約中資料の ReserveItem オブジェクトのリスト。
        """
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 予約中ページへ移動
            page.get_by_role("link", name="●予約中一覧").click()
            page.wait_for_load_state()
            sleep(1)

            # ページ内容を取得
            elements = page.locator(
                "#main > form:nth-child(7) > fieldset > div > table > tbody > tr > td"
            ).all_inner_texts()

            # # DEBUG:
            # for i, li in enumerate(elements):
            #     print(i, li)

            # 8要素で1アイテム
            cnt_unit = 8
            cnt = len(elements) // cnt_unit

            items = []
            for i in range(cnt):
                item = ReserveItem(
                    title=elements[i * cnt_unit + 4]
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip(),
                    category=None,
                    receive_location=elements[i * cnt_unit + 3].split("\n")[1],
                    notification_method=elements[i * cnt_unit + 6].split("\n")[1],
                    reserve_date=elements[i * cnt_unit + 2].split("\n")[0],
                    reserve_rank=elements[i * cnt_unit + 2].split("\n")[2],
                    reserve_status=elements[i * cnt_unit + 1],
                    reserve_cancel_reason=None,
                    reserve_expire_date=None,
                )
                items.append(item)

            context.close()
            browser.close()

            return items
