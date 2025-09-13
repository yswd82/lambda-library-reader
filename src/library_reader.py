from abc import ABCMeta
from playwright.sync_api import Playwright
from playwright.sync_api._generated import Browser, Page
from model import LentItem, ReserveItem


def create_browser(playwright: Playwright):
    browser: Browser = playwright.chromium.launch(
        # headless=False,
        # downloads_path="/tmp",
        args=[
            # "--autoplay-policy=user-gesture-required",
            "--disable-gpu",
            # "--disable-background-networking",
            # "--disable-background-timer-throttling",
            # "--disable-backgrounding-occluded-windows",
            # "--disable-breakpad",
            # "--disable-client-side-phishing-detection",
            # "--disable-component-update",
            # "--disable-default-apps",
            # "--disable-dev-shm-usage",
            # "--disable-domain-reliability",
            # "--disable-extensions",
            # "--disable-features=AudioServiceOutOfProcess",
            # "--disable-hang-monitor",
            # "--disable-ipc-flooding-protection",
            # "--disable-notifications",
            # "--disable-offer-store-unmasked-wallet-cards",
            # "--disable-popup-blocking",
            # "--disable-print-preview",
            # "--disable-prompt-on-repost",
            # "--disable-renderer-backgrounding",
            # "--disable-setuid-sandbox",
            # "--disable-speech-api",
            # "--disable-sync",
            # "--disk-cache-size=33554432",
            # "--hide-scrollbars",
            # "--ignore-gpu-blacklist",
            # "--metrics-recording-only",
            # "--mute-audio",
            # "--no-default-browser-check",
            # "--no-first-run",
            # "--no-pings",
            # "--no-sandbox",
            # "--no-zygote",
            # "--password-store=basic",
            # "--use-gl=swiftshader",
            # "--use-mock-keychain",
            "--single-process",
        ],
    )

    return browser


class LibraryReader(metaclass=ABCMeta):
    URL: str

    def __init__(self, user: str, password: str) -> None:
        self.card: str = user
        self.password: str = password
        self.page: Page = None

    def _login(self) -> Page:
        pass

    @property
    def lent(self) -> list[LentItem]:
        pass

    @property
    def reserve(self) -> list[ReserveItem]:
        pass
