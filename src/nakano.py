from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class NakanoLibraryReader(BaseLibraryReader):
    """
    中野区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    URL = "https://www.kn.licsre-saas.jp/tokyo-nakano/webopac/usermenu.do?target=adult/"
    # 貸出アイテムの構成要素数
    LENT_UNIT = 10
    # 予約アイテムの構成要素数
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
            _title = "".join(row[2])
            _is_reserved = len(row[8][0]) > 0
            _checkout_location = row[5][0]
            _checkout_date = row[3][0]
            _return_date = row[4][0]
            _is_extendable = "貸出延長" in row[9][0]
            _extend_count = 0 if _is_extendable else 1

            items.append(
                LentItem(
                    title=_title,
                    # category="",
                    checkout_location=_checkout_location,
                    checkout_date=_checkout_date,
                    return_date=_return_date,
                    # reserved_count="",
                    is_extendable=_is_extendable,
                    extend_count=_extend_count,
                    is_reserved=_is_reserved,
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

        i = 0
        while i < len(elements):
            parse_elements = []
            if elements[i][0] and elements[i][0] in ("予約中", "取置済"):
                # 予約中または取り置き済みの場合は、i-1 から i+6 までの要素を取得する
                parse_elements = elements[i - 1 : i + 7]

            elif elements[i][0] and elements[i][0] in ("回送中"):
                # 回送中の場合は、i-2 から i+6 までの要素を取得し、1番目の要素を削除する
                del elements[i - 1]
                i = i - 1

                parse_elements = elements[i - 1 : i + 7]

            if parse_elements:
                # print(i, elements[i], parse_elements)

                _title = "".join(parse_elements[4])
                _receive_location = parse_elements[3][1]
                _notification_method = (
                    parse_elements[6][0]
                    if len(parse_elements[6]) == 1
                    else parse_elements[6][1]
                )
                _reserve_date = parse_elements[2][0]
                _reserve_rank = (
                    parse_elements[2][2] if len(parse_elements[2]) == 3 else ""
                )
                _reserve_status = parse_elements[1][0]
                _reserve_expire_date = parse_elements[5][0]

                items.append(
                    ReserveItem(
                        title=_title,
                        # category="",
                        receive_location=_receive_location,
                        notification_method=_notification_method,
                        reserve_date=_reserve_date,
                        reserve_rank=_reserve_rank,
                        reserve_status=_reserve_status,
                        # reserve_cancel_reason="",
                        reserve_expire_date=_reserve_expire_date,
                        is_canceled=None,
                    )
                )

            i += 1

        return items
