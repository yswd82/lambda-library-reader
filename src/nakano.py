from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class NakanoLibraryReader(BaseLibraryReader):
    """
    中野区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    URL = "https://www.kn.licsre-saas.jp/tokyo-nakano/webopac/usermenu.do?target=adult/"
    LENT_UNIT = 10
    RESERVE_UNIT = 8

    def _login(self, context: BrowserContext) -> Page:
        page: Page = context.new_page()
        page.goto(self.URL)

        page.get_by_label("利用者番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログインする").click()

        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.get_by_role("link", name="●貸出中一覧").click()

        _locator = (
            "#main > form:nth-child(2) > fieldset > div > table > tbody > tr > td"
        )
        page.wait_for_selector(_locator)

        elements: List[str] = page.locator(_locator).all_inner_texts()

        # タブ除去＋改行分割
        elements = [e.replace("\t", "").strip().split("\n") for e in elements]
        rows = [
            elements[i : i + self.LENT_UNIT]
            for i in range(0, len(elements), self.LENT_UNIT)
        ]

        items: List[LentItem] = []
        for row in rows:
            print(row)

            title = "".join(row[2])
            is_reserved = len(row[8][0]) > 0
            checkout_location = row[5][0]
            checkout_date = row[3][0]
            return_date = row[4][0]

            items.append(
                LentItem(
                    title=title,
                    category="",
                    checkout_location=checkout_location,
                    checkout_date=checkout_date,
                    return_date=return_date,
                    reserved_count="",
                    extend_count="",
                    is_reserved=is_reserved,
                )
            )
        return items

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.get_by_role("link", name="●予約中一覧").click()

        _locator = (
            "#main > form:nth-child(7) > fieldset > div > table > tbody > tr > td"
        )
        page.wait_for_selector(_locator)

        elements: List[str] = page.locator(_locator).all_inner_texts()

        elements = [e.replace("\t", "").strip().split("\n") for e in elements]

        items: List[ReserveItem] = []
        i, i_offset = 0, 0

        while i < len(elements):
            if elements[i][0] in ("予約中", "取置済"):
                # 要素数調整（必ず8要素に揃える）
                if i_offset + 2 == i:
                    del elements[i_offset + 1]
                    i -= 1

                title = "".join(elements[i_offset + 4])
                receive_location = elements[i_offset + 3][1]
                notification_method = (
                    elements[i_offset + 6][0]
                    if len(elements[i_offset + 6]) == 1
                    else elements[i_offset + 6][1]
                )
                reserve_date = elements[i_offset + 2][0]
                reserve_rank = (
                    elements[i_offset + 2][2]
                    if len(elements[i_offset + 2]) == 3
                    else ""
                )
                reserve_status = elements[i_offset + 1][0]
                reserve_expire_date = elements[i_offset + 5][0]

                items.append(
                    ReserveItem(
                        title=title,
                        category="",
                        receive_location=receive_location,
                        notification_method=notification_method,
                        reserve_date=reserve_date,
                        reserve_rank=reserve_rank,
                        reserve_status=reserve_status,
                        reserve_cancel_reason="",
                        reserve_expire_date=reserve_expire_date,
                    )
                )
                i_offset += self.RESERVE_UNIT
            i += 1

        return items
