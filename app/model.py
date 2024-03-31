from dataclasses import dataclass, field
from datetime import date
from dateutil import parser


@dataclass
class LentItem:
    title: str = field(default=None)
    category: str = field(default=None)
    checkout_location: str = field(default=None)
    checkout_date: str = field(default=None)
    return_date: str = field(default=None)
    reserved_count: int = field(default=None)
    is_extendable: bool = field(default=None)
    extend_count: int = field(default=None)

    @property
    def is_expired(self) -> bool:
        return parser.parse(self.return_date).date() < date.today()


@dataclass
class ReserveItem:
    title: str = field(default=None)
    category: str = field(default=None)
    receive_location: str = field(default=None)
    notification_method: str = field(default=None)
    reserve_date: str = field(default=None)
    reserve_rank: str = field(default=None)
    reserve_status: str = field(default=None)
    reserve_cancel_reason: str = field(default=None)
    reserve_expire_date: str = field(default=None)
