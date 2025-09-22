from abc import ABC, abstractmethod
from typing import List, Callable

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, BrowserContext, Page
from model import LentItem, ReserveItem


def create_browser(playwright):
    """Playwright ブラウザを起動する共通関数"""
    return playwright.chromium.launch(
        args=[
            "--disable-gpu",
            "--single-process",
        ],
    )


class BaseLibraryReader(ABC):
    """
    各区立図書館の共通基底クラス。
    - ログイン処理はサブクラスで実装
    - 貸出中・予約中一覧のスクレイピング処理もサブクラスで実装
    """

    URL: str

    def __init__(self, user: str, password: str) -> None:
        self.card: str = user
        self.password: str = password

    # -------------------------
    # サブクラスで必須実装
    # -------------------------
    @abstractmethod
    def _login(self, context: BrowserContext) -> Page:
        """ログイン処理を実装する"""
        raise NotImplementedError

    @abstractmethod
    def _parse_lent(self, page: Page) -> List[LentItem]:
        """貸出中一覧のスクレイピング処理"""
        raise NotImplementedError

    @abstractmethod
    def _parse_reserve(self, page: Page) -> List[ReserveItem]:
        """予約中一覧のスクレイピング処理"""
        raise NotImplementedError

    # -------------------------
    # 共通ユーティリティ
    # -------------------------
    def _with_login(self, action: Callable[[Page], List]) -> List:
        """ブラウザを起動しログイン後、指定の処理を実行して結果を返す"""
        with sync_playwright() as playwright:
            browser: Browser = create_browser(playwright)
            context: BrowserContext = browser.new_context()
            try:
                page = self._login(context)
                return action(page)
            finally:
                context.close()
                browser.close()

    @staticmethod
    def _chunk(data: List[str], size: int) -> List[List[str]]:
        """リストを size ごとに分割して返す"""
        return [data[i : i + size] for i in range(0, len(data), size)]

    # -------------------------
    # 公開プロパティ
    # -------------------------
    @property
    def lent(self) -> List[LentItem]:
        """現在貸出中の資料一覧を取得"""
        return self._with_login(self._parse_lent)

    @property
    def reserve(self) -> List[ReserveItem]:
        """現在予約中の資料一覧を取得"""
        return self._with_login(self._parse_reserve)
