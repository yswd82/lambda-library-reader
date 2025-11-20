from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class MinatoLibraryReader(BaseLibraryReader):
    URL = "https://www.lib.city.minato.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"

    def _login(self, context: BrowserContext) -> Page:
        page = context.new_page()
        page.goto(self.URL)
        page.get_by_role("link", name="マイ図書館メニューを開きます").click()
        page.get_by_role("link", name="ログイン").click()
        page.get_by_label("利用者番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()
        page.wait_for_load_state()
        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.click('a[id="stat-lent"]')

        _locator_title = "div.title > a > strong"
        _locator_body = "div.matter"

        page.wait_for_selector(_locator_title)
        page.wait_for_selector(_locator_body)

        titles = [
            t.replace("\u3000", " ")
            for t in page.locator(_locator_title).all_inner_texts()
        ]
        tmp = page.locator(_locator_body).all_inner_texts()
        contents = self._chunk(tmp, 6)
        return [
            LentItem(
                title=t,
                category=d[0],
                checkout_location=d[1].replace("貸出館： ", ""),
                checkout_date=d[2].replace("貸出日： ", ""),
                return_date=d[3].replace("返却期日： ", ""),
                reserved_count=d[4].replace("予約数： ", ""),
                extend_count=d[5].replace("延長回数： ", ""),
                is_reserved=int(d[4].replace("予約数： ", "")) > 0,
            )
            for t, d in zip(titles, contents)
        ]

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.click('a[id="stat-resv"]')

        _locator_title = "div.title > strong"
        _locator_category = "div.intro"
        _locator_body = "div.matter"

        page.wait_for_selector(_locator_title)
        page.wait_for_selector(_locator_category)
        page.wait_for_selector(_locator_body)

        titles = [
            t.replace("\u3000", " ").lstrip()
            for t in page.locator(_locator_title).all_inner_texts()
        ]
        categories = page.locator(_locator_category).all_inner_texts()
        tmp = page.locator(_locator_body).all_inner_texts()
        contents = self._chunk(tmp, 7)
        return [
            ReserveItem(
                title=t,
                category=c,
                receive_location="",
                notification_method="",
                reserve_date=d[2].replace("予約日:", ""),
                reserve_rank=d[4].replace("予約順位:", ""),
                reserve_status=d[5].replace("予約状態:", ""),
                reserve_expire_date=d[6].replace("取置期限:", "").strip(),
            )
            for t, c, d in zip(titles, categories, contents)
        ]
