from library_reader import LibraryReader, create_browser
from model import LentItem, ReserveItem

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Locator, Page

from typing import List


class NerimaLibraryReader(LibraryReader):
    """
    練馬区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。

    LibraryReader を継承し、Playwright を用いて自動的にログイン・スクレイピングを行う。

    Attributes:
        URL (str): 練馬区立図書館のトップページURL。
        card (str): 図書館利用カード番号（親クラスで設定）。
        password (str): ログイン用パスワード（親クラスで設定）。
    """

    URL = "https://www.lib.nerima.tokyo.jp/"

    def _login(self, context) -> Page:
        """
        練馬区立図書館サイトにログインし、ログイン後のページオブジェクトを返す。

        Args:
            context (BrowserContext): Playwright のブラウザコンテキスト。

        Returns:
            Page: ログイン後のページオブジェクト。
        """
        page: Page = context.new_page()
        page.goto(self.URL)
        page.get_by_role("link", name="利用者ログイン").click()
        page.get_by_placeholder("利用者ID").fill(self.card)
        page.get_by_placeholder("パスワード").fill(self.password)
        page.get_by_role("button", name="送信").click()
        page.wait_for_load_state()

        return page

    @property
    def lent(self) -> List[LentItem]:
        """
        現在貸出中の資料一覧を取得する。

        Returns:
            List[LentItem]: 貸出中資料の LentItem オブジェクトのリスト。
        """
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 「貸出中」タブに切り替え
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
                            # TODO: 仮置き
                            is_reserved=False,
                        )
                    )

            context.close()
            browser.close()

            return items

    @property
    def reserve(self) -> List[ReserveItem]:
        """
        現在予約中の資料一覧を取得する。

        Returns:
            List[ReserveItem]: 予約中資料の ReserveItem オブジェクトのリスト。
        """
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()

            # ログイン
            page: Page = self._login(context)

            # 「予約中」タブに切り替え
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
