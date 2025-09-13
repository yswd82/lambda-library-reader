from library_reader import LibraryReader, create_browser
from model import LentItem, ReserveItem

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Locator, Page

from typing import List


class MinatoLibraryReader(LibraryReader):
    """
    港区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。

    LibraryReader を継承し、Playwright を用いて自動的にログイン・スクレイピングを行う。

    Attributes:
        URL (str): 港区立図書館のトップページURL。
        card (str): 図書館利用カード番号（親クラスで設定）。
        password (str): ログイン用パスワード（親クラスで設定）。
    """

    URL = "https://www.lib.city.minato.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"

    def _login(self, context) -> Page:
        """
        港区立図書館サイトにログインし、ログイン後のページオブジェクトを返す。

        Args:
            context (BrowserContext): Playwright のブラウザコンテキスト。

        Returns:
            Page: ログイン後のページオブジェクト。
        """
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
            page.wait_for_load_state()

            # 貸出中ページへ移動
            page.click('a[id="stat-lent"]')
            page.wait_for_load_state()

            # タイトル一覧を取得
            locator: Locator = page.locator("div.title > a > strong")
            titles: List[str] = locator.all_inner_texts()
            titles = [title.replace("\u3000", " ") for title in titles]

            # その他の情報を取得
            tmp: List[str] = page.locator("div.matter").all_inner_texts()
            contents: List[List[str]] = [tmp[i : i + 6] for i in range(0, len(tmp), 6)]

            # アイテムを作成
            items: List[LentItem] = []
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
                        is_reserved=True
                        if int(d[4].replace("予約数： ", "")) > 0
                        else False,
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

            # 予約中ページへ移動
            page.click('a[id="stat-resv"]')
            page.wait_for_load_state()

            # タイトルとカテゴリを取得
            locator: Locator = page.locator(
                "div.main > div > div > div > div.title > strong"
            )
            titles: List[str] = [
                title.replace("\u3000", " ").lstrip()
                for title in locator.all_inner_texts()
            ]
            categories: List[str] = page.locator("div.intro").all_inner_texts()

            # その他の情報を取得
            locator2: Locator = page.locator("div.matter")
            tmp: List[str] = locator2.all_inner_texts()
            contents: List[List[str]] = [tmp[i : i + 7] for i in range(0, len(tmp), 7)]

            # アイテムを作成
            items: List[ReserveItem] = []
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
