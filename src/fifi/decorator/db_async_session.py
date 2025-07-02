import functools

from ..data.database_provider import DatabaseProvider


def db_async_session(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with DatabaseProvider().get_new_seddion() as session:
            try:
                result = await func(*args, session=session, **kwargs)
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper
