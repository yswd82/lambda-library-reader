from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


from library_reader import BaseLibraryReader


class SuginamiLibraryReader(BaseLibraryReader):
    """
    杉並区立図書館のWebサイトから貸出中・予約中の資料情報を取得するクラス。
    """

    URL = "https://www.library.city.suginami.tokyo.jp/"
    LENT_UNIT = 8
    RESERVE_UNIT = 12

    def _login(self, context: BrowserContext) -> Page:
        page: Page = context.new_page()
        page.goto(self.URL)

        page.get_by_role("banner").get_by_role("link", name="利用者ログイン").click()
        page.get_by_role("button", name="ログイン").click()
        page.get_by_role("textbox", name="図書館利用カード番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()

        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.get_by_title("あなたが現在借りている資料です").click()

        _locator = "div.main > table > tbody > tr > td"
        page.wait_for_selector(_locator)

        elements: List[str] = page.locator(_locator).all_inner_texts()

        rows = self._chunk(elements, self.LENT_UNIT)

        return [
            LentItem(
                title=row[0],
                category=row[1],
                checkout_location=row[2],
                checkout_date=row[3],
                return_date=row[4],
                reserved_count=row[5],
                extend_count=row[6],
                is_reserved=int(row[5]) > 0,
            )
            for row in rows
        ]

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.get_by_title("あなたが現在予約している資料です").click()

        _locator = "table#ItemDetaTable > tbody > tr > td"
        page.wait_for_selector(_locator)

        elements: List[str] = page.locator(_locator).all_inner_texts()

        rows = self._chunk(elements, self.RESERVE_UNIT)

        items = []
        for row in rows:
            # 受取場所と連絡方法が2要素の場合は内容が確定している。
            _receive_location = (
                row[2].split("\n")[0] if len(row[2].split("\n")) == 2 else "選択可"
            )
            _notification_method = (
                row[2].split("\n")[1] if len(row[2].split("\n")) == 2 else "選択可"
            )

            item = ReserveItem(
                title=row[0].strip(),
                category=row[1],
                receive_location=_receive_location,
                notification_method=_notification_method,
                reserve_date=row[3].split("\n")[0],
                reserve_rank=row[4],
                reserve_status=row[5],
                reserve_cancel_reason=row[6],
                reserve_expire_date=row[7],
            )
            items.append(item)

        return items
