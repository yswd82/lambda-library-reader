from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


from library_reader import BaseLibraryReader


class SuginamiLibraryReader(BaseLibraryReader):
    """
    杉並区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    def _login(self, context: BrowserContext) -> Page:
        page: Page = context.new_page()

        URL = "https://www.library.city.suginami.tokyo.jp/"
        page.goto(URL)

        page.get_by_role("banner").get_by_role("link", name="利用者ログイン").click()
        page.get_by_role("button", name="ログイン").click()
        page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()

        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.get_by_title("あなたが現在借りている資料です").click()

        # セレクタと構成要素数
        SELECTOR = "div.main > table > tbody > tr > td"
        LENT_UNIT = 8

        page.wait_for_selector(SELECTOR)

        elements: List[str] = page.locator(SELECTOR).all_inner_texts()

        rows = self._chunk(elements, LENT_UNIT)

        items = []
        for row in rows:
            title = row[0]
            category = row[1]
            checkout_location = row[2]
            checkout_date = row[3]
            return_date = row[4]
            extend_count = int(row[6])
            reserved_count = int(row[5])
            is_reserved = reserved_count > 0
            is_extendable = extend_count == 0 and not is_reserved

            items.append(
                LentItem(
                    title=title,
                    category=category,
                    checkout_location=checkout_location,
                    checkout_date=checkout_date,
                    return_date=return_date,
                    reserved_count=reserved_count,
                    extend_count=extend_count,
                    is_reserved=is_reserved,
                    is_extendable=is_extendable,
                )
            )

        return items

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.get_by_title("あなたが現在予約している資料です").click()

        # セレクタと構成要素数
        SELECTOR = "table#ItemDetaTable > tbody > tr > td"
        RESERVE_UNIT = 12

        page.wait_for_selector(SELECTOR)

        elements: List[str] = page.locator(SELECTOR).all_inner_texts()

        rows = self._chunk(elements, RESERVE_UNIT)

        items = []
        for row in rows:
            # 受取場所と連絡方法が2要素の場合は内容が確定している。
            _receive_location = (
                row[2].split("\n")[0] if len(row[2].split("\n")) == 2 else "選択可"
            )
            _notification_method = (
                row[2].split("\n")[1] if len(row[2].split("\n")) == 2 else "選択可"
            )

            title = row[0].strip()
            category = row[1]
            reserve_date = row[3].split("\n")[0]
            reserve_rank = row[4]
            reserve_status = row[5]
            reserve_cancel_reason = row[6]
            reserve_expire_date = row[7]

            items.append(
                ReserveItem(
                    title=title,
                    category=category,
                    receive_location=_receive_location,
                    notification_method=_notification_method,
                    reserve_date=reserve_date,
                    reserve_rank=reserve_rank,
                    reserve_status=reserve_status,
                    reserve_cancel_reason=reserve_cancel_reason,
                    reserve_expire_date=reserve_expire_date,
                )
            )

        return items
