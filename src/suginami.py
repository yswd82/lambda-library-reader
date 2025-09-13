from src.library_reader import LibraryReader, create_browser
from src.model import LentItem, ReserveItem

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Page

from time import sleep


class SuginamiLibraryReader(LibraryReader):
    """
    杉並区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。

    LibraryReader を継承し、Playwright を用いて自動的にログイン・スクレイピングを行う。

    Attributes:
        URL (str): 杉並区立図書館のトップページURL。
        card (str): 図書館利用カード番号（親クラスで設定）。
        password (str): ログイン用パスワード（親クラスで設定）。
    """

    URL = "https://www.library.city.suginami.tokyo.jp/"

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

        page.get_by_role("banner").get_by_role("link", name="利用者ログイン").click()
        page.get_by_role("button", name="ログイン").click()
        page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()

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
            page.get_by_title("あなたが現在借りている資料です").click()
            page.wait_for_load_state()
            sleep(1)

            # ページ内容を取得
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
                        is_reserved=True if elements[i * cnt_unit + 5] > 0 else False,
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
            page.get_by_title("あなたが現在予約している資料です").click()
            page.wait_for_load_state()
            sleep(1)

            # ページ内容を取得
            elements = page.locator(
                "table#ItemDetaTable > tbody > tr > td"
            ).all_inner_texts()

            # 12要素で1アイテム
            cnt_unit = 12
            cnt = len(elements) // cnt_unit

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
