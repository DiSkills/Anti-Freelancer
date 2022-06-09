import typing
from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


def paginate(get_function, exist_function, url: str, *filter_params):
    """
        Paginate
        :param get_function: Get function
        :param exist_function: Exist function
        :param url: URL
        :type url: str
        :param filter_params: Filter params
        :return: Paginate wrapper
    """

    def paginate_wrapper(function):
        """
            Paginate wrapper
            :param function: Function
            :return: Wrapper
        """

        @wraps(function)
        async def wrapper(*args, page: int, page_size: int, db: AsyncSession, **kwargs) -> dict[str, typing.Any]:
            """
                Wrapper
                :param args: args
                :param page: Page
                :type page: int
                :param page_size: Page size
                :type page_size: int
                :param db: DB
                :type db: AsyncSession
                :param kwargs: kwargs
                :return: Pagination results
                :rtype: dict
                :raise HTTPException 400: Results not found
            """

            skip: int = page_size * (page - 1)
            queryset: list = await get_function(
                db=db, skip=skip, limit=page_size, **{param: kwargs[param] for param in filter_params}
            )

            if not queryset:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Results not found')

            next_page: typing.Optional[str] = None
            previous_page: typing.Optional[str] = None

            if await exist_function(
                    db=db, skip=skip + page_size, limit=page_size, **{param: kwargs[param] for param in filter_params}
            ):
                next_page = f'{url}?page={page + 1}&page_size={page_size}'
                for param in filter_params:
                    next_page += f'&{param}={kwargs[param]}'

            if (page - 1) > 0:
                previous_page = f'{url}?page={page - 1}&page_size={page_size}'
                for param in filter_params:
                    previous_page += f'&{param}={kwargs[param]}'

            return {
                'next': next_page,
                'previous': previous_page,
                'page': page,
                'results': await function(*args, page=page, page_size=page_size, queryset=queryset, db=db, **kwargs)
            }

        return wrapper

    return paginate_wrapper
