from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class NerimaLibraryReader(BaseLibraryReader):
    """
    練馬区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    URL = "https://www.lib.nerima.tokyo.jp/"
    MAX_ROWS = 20  # テーブルの最大行数目安

    def _login(self, context: BrowserContext) -> Page:
        page: Page = context.new_page()
        page.goto(self.URL)

        page.get_by_role("link", name="利用者ログイン").click()
        page.get_by_placeholder("利用者ID").fill(self.card)
        page.get_by_placeholder("パスワード").fill(self.password)
        page.get_by_role("button", name="送信").click()
        page.wait_for_load_state()

        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.click("#ContentLend-tab")
        page.wait_for_load_state()

        items: List[LentItem] = []
        for i in range(1, self.MAX_ROWS):
            elements: List[str] = page.locator(
                f"#ContentLend > form > div > table > tbody > tr:nth-child({i * 2}) > td"
            ).all_inner_texts()

            if elements:
                items.append(
                    LentItem(
                        title=elements[2],
                        category=elements[3],
                        checkout_location=elements[5],
                        checkout_date=elements[6],
                        return_date=elements[7],
                        is_extendable=(elements[1] == "延長"),
                        extend_count="",  # 未対応
                        is_reserved=False,  # 未対応
                    )
                )
        return items

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.click("#ContentRsv-tab")
        page.wait_for_load_state()

        items: List[ReserveItem] = []
        for i in range(1, self.MAX_ROWS):
            elements: List[str] = page.locator(
                f"#ContentRsv > form > div > table > tbody > tr:nth-child({i}) > td"
            ).all_inner_texts()

            if elements:
                items.append(
                    ReserveItem(
                        reserve_status=elements[1],
                        reserve_rank=elements[2],
                        title=elements[3],
                        category=elements[4],
                        reserve_date=elements[6],
                        reserve_expire_date=elements[7],
                        receive_location=elements[9],
                        notification_method=elements[10],
                    )
                )
        return items
