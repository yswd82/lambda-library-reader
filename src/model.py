from dataclasses import dataclass, field
from datetime import date
from dateutil import parser


@dataclass
class LentItem:
    """
    図書館などで貸出中のアイテムを表すデータクラス。

    Attributes:
        title (str): アイテムのタイトル（書籍名など）。
        category (str): アイテムのカテゴリ（本、DVDなど）。
        checkout_location (str): 貸出場所（図書館名など）。
        checkout_date (str): 貸出日（文字列形式）。
        return_date (str): 返却期限日（文字列形式）。
        reserved_count (int): 他の利用者による予約件数。
        is_extendable (bool): 延長可能かどうか。
        extend_count (int): 延長した回数。
    """

    title: str = field(default=None)
    category: str = field(default=None)
    checkout_location: str = field(default=None)
    checkout_date: str = field(default=None)
    return_date: str = field(default=None)
    reserved_count: int = field(default=None)
    is_extendable: bool = field(default=None)
    extend_count: int = field(default=None)
    is_reserved: bool = field(default=None)

    @property
    def is_expired(self) -> bool:
        """
        返却期限が過ぎているかどうかを判定する。

        Returns:
            bool: 期限切れの場合は True、まだ期限内の場合は False。
        """
        return parser.parse(self.return_date).date() < date.today()


@dataclass
class ReserveItem:
    """
    図書館などで予約中のアイテムを表すデータクラス。

    Attributes:
        title (str): アイテムのタイトル（書籍名など）。
        category (str): アイテムのカテゴリ（本、DVDなど）。
        receive_location (str): 受取場所（図書館名など）。
        notification_method (str): 通知方法（メール、電話など）。
        reserve_date (str): 予約日（文字列形式）。
        reserve_rank (str): 予約順位（何番目に受け取れるか）。
        reserve_status (str): 予約の状態（受付中、準備中など）。
        reserve_cancel_reason (str): 予約キャンセル理由（キャンセルされた場合）。
        reserve_expire_date (str): 予約の有効期限日（文字列形式）。
    """

    title: str = field(default=None)
    category: str = field(default=None)
    receive_location: str = field(default=None)
    notification_method: str = field(default=None)
    reserve_date: str = field(default=None)
    reserve_rank: str = field(default=None)
    reserve_status: str = field(default=None)
    reserve_cancel_reason: str = field(default=None)
    reserve_expire_date: str = field(default=None)
