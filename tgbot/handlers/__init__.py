"""Import all routers and add them to routers_list."""
from .calendar import calendar_router

routers_list = [
    calendar_router,
]


__all__ = [
    "routers_list",
]
