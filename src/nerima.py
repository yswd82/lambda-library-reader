from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class NerimaLibraryReader(BaseLibraryReader):
    """
    練馬区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    MAX_ROWS = 20  # テーブルの最大行数目安

    def _login(self, context: BrowserContext) -> Page:
        page: Page = context.new_page()

        URL = "https://www.lib.nerima.tokyo.jp/"
        page.goto(URL)

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
            SELECTOR_UPPER = f"#ContentLend > form > div > table > tbody > tr:nth-child({i * 2}) > td"
            SELECTOR_LOWER = f"#ContentLend > form > div > table > tbody > tr:nth-child({i * 2 + 1}) > td"

            elements_upper: List[str] = page.locator(SELECTOR_UPPER).all_inner_texts()
            elements_lower: List[str] = page.locator(SELECTOR_LOWER).all_inner_texts()

            # print("elements:", elements_upper)
            # print("elements:", elements_lower)

            if elements_upper:
                _title = elements_upper[2]
                _category = elements_upper[3]
                _checkout_location = elements_upper[5]
                _checkout_date = elements_upper[6]
                _return_date = elements_upper[7]
                _is_extendable = True if "延長" == elements_upper[1] else False
                _extend_count = (
                    1 if "すでに延長されています" in elements_upper[1] else 0
                )
                _is_reserved = (
                    True if "予約待ちあり" in elements_lower[1].strip() else False
                )

                items.append(
                    LentItem(
                        title=_title,
                        category=_category,
                        checkout_location=_checkout_location,
                        checkout_date=_checkout_date,
                        return_date=_return_date,
                        is_extendable=_is_extendable,
                        extend_count=_extend_count,
                        is_reserved=_is_reserved,
                    )
                )

                # print(items[-1])
        return items

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.click("#ContentRsv-tab")
        page.wait_for_load_state()

        items: List[ReserveItem] = []
        for i in range(1, self.MAX_ROWS):
            SELECTOR = (
                f"#ContentRsv > form > div > table > tbody > tr:nth-child({i}) > td"
            )

            elements: List[str] = page.locator(SELECTOR).all_inner_texts()

            if elements:
                _reserve_status = elements[1].replace("\n", "")
                _reserve_rank = (
                    int(elements[2].split(" ")[0])
                    if elements[2].split(" ")[0].isnumeric()
                    else None
                )
                _title = elements[3].strip()
                _category = elements[4]
                _reserve_date = elements[6]
                _reserve_expire_date = (
                    elements[7].replace("\u00a0", "")
                    if elements[7].replace("\u00a0", "")
                    else None
                )
                _receive_location = elements[9]
                _notification_method = elements[10]

                _is_canceled = (
                    False
                    if _reserve_status
                    in ("予約解除可能", "移送中です", "ご用意できました")
                    else None
                )
                items.append(
                    ReserveItem(
                        reserve_status=_reserve_status,
                        reserve_rank=_reserve_rank,
                        title=_title,
                        category=_category,
                        reserve_date=_reserve_date,
                        reserve_expire_date=_reserve_expire_date,
                        receive_location=_receive_location,
                        notification_method=_notification_method,
                        is_canceled=_is_canceled,
                    )
                )
        return items
