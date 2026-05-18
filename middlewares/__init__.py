from loader import dp
from .throttling import ThrottlingMiddleware

dp.middleware.setup(ThrottlingMiddleware())
