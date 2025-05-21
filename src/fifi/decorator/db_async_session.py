import functools
from sqlalchemy.orm import sessionmaker


def db_async_session(session_maker: sessionmaker):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with session_maker() as session:
                try:
                    result = await func(*args, session=session, **kwargs)
                    await session.commit()
                    return result
                except Exception:
                    await session.rollback()
                    raise

        return wrapper

    return decorator
