from library_reader import BaseLibraryReader
from model import LentItem, ReserveItem

from playwright.sync_api._generated import BrowserContext, Page

from typing import List


class MinatoLibraryReader(BaseLibraryReader):
    def _login(self, context: BrowserContext) -> Page:
        page = context.new_page()

        URL = "https://www.lib.city.minato.tokyo.jp/licsxp-opac/WOpacSmtMnuTopAction.do"
        page.goto(URL)

        page.get_by_role("link", name="マイ図書館メニューを開きます").click()
        page.get_by_role("link", name="ログイン").click()
        page.get_by_label("利用者番号").fill(self.card)
        page.get_by_label("パスワード").fill(self.password)
        page.get_by_role("button", name="ログイン").click()
        page.wait_for_load_state()
        return page

    def _parse_lent(self, page: Page) -> List[LentItem]:
        page.click('a[id="stat-lent"]')

        try:
            SELECTOR_TITLE = "div.title > a > strong"
            SELECTOR_BODY = "div.matter"

            page.wait_for_selector(SELECTOR_TITLE)
            page.wait_for_selector(SELECTOR_BODY)
        except Exception:
            # 借りている本が無い場合は空リストを返す
            return []

        titles = [
            t.replace("\u3000", " ")
            for t in page.locator(SELECTOR_TITLE).all_inner_texts()
        ]
        tmp = page.locator(SELECTOR_BODY).all_inner_texts()
        contents = self._chunk(tmp, 6)

        items = []
        for t, d in zip(titles, contents):
            _title = t
            _category = d[0]
            _checkout_location = d[1].replace("貸出館： ", "")
            _checkout_date = d[2].replace("貸出日： ", "")
            _return_date = d[3].replace("返却期日： ", "")
            _reserved_count = (
                int(d[4].replace("予約数： ", ""))
                if d[4].replace("予約数： ", "").isnumeric()
                else None
            )
            _extend_count = (
                int(d[5].replace("延長回数： ", ""))
                if d[5].replace("延長回数： ", "").isnumeric()
                else None
            )
            _is_reserved = int(d[4].replace("予約数： ", "")) > 0
            _is_extendable = _extend_count == 0 and not _is_reserved

            items.append(
                LentItem(
                    title=_title,
                    category=_category,
                    checkout_location=_checkout_location,
                    checkout_date=_checkout_date,
                    return_date=_return_date,
                    reserved_count=_reserved_count,
                    extend_count=_extend_count,
                    is_reserved=_is_reserved,
                    is_extendable=_is_extendable,
                )
            )

        return items

    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        page.click('a[id="stat-resv"]')

        try:
            SELECTOR_TITLE = "div.title > strong"
            SELECTOR_CATEGORY = "div.intro"
            SELECTOR_BODY = "div.matter"

            page.wait_for_selector(SELECTOR_TITLE)
            page.wait_for_selector(SELECTOR_CATEGORY)
            page.wait_for_selector(SELECTOR_BODY)

        except Exception:
            # 予約本が無い場合は空リストを返す
            return []

        titles = [
            t.replace("\u3000", " ").lstrip()
            for t in page.locator(SELECTOR_TITLE).all_inner_texts()
        ]
        categories = page.locator(SELECTOR_CATEGORY).all_inner_texts()
        tmp = page.locator(SELECTOR_BODY).all_inner_texts()
        contents = self._chunk(tmp, 7)

        items = []
        for _title, _category, content in zip(titles, categories, contents):
            # 受取館の文字列にクレンジング後、要素数が1の場合は決定済み。そうでない場合は選択可能状態なので空白にする
            _receive_location = (
                content[0].replace("受取館: \n受取館\n", "")
                if len(content[0].replace("受取館: \n受取館\n", "").split("\n")) == 1
                else "選択可"
            )

            # 連絡方法の文字列をクレンジング後、要素数が1の場合は決定済み。そうでない場合は選択可能状態なので空白にする
            _notification_method = (
                content[1].replace("連絡方法: \n連絡方法\n", "")
                if len(content[1].replace("連絡方法: \n連絡方法\n", "").split("\n"))
                == 1
                else "選択可"
            )
            _reserve_date = content[2].replace("予約日:", "")
            _reserve_rank = (
                int(content[4].replace("予約順位:", ""))
                if content[4].replace("予約順位:", "").isnumeric()
                else None
            )
            _reserve_status = content[5].replace("予約状態:", "").replace(" ", "")
            _reserve_expire_date = (
                content[6].replace("取置期限:", "").replace(" ", "")
                if content[6].replace("取置期限:", "").replace(" ", "")
                else None
            )

            items.append(
                ReserveItem(
                    title=_title,
                    category=_category,
                    receive_location=_receive_location,
                    notification_method=_notification_method,
                    reserve_date=_reserve_date,
                    reserve_rank=_reserve_rank,
                    reserve_status=_reserve_status,
                    reserve_expire_date=_reserve_expire_date,
                    is_canceled=None,
                )
            )

        return items
