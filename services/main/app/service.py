import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import CRUD


def paginate(crud: CRUD, url: str):
    """
        Paginate
        :param crud: CRUD
        :type crud: CRUD
        :param url: URL
        :type url: str
        :return: Generator
    """

    def paginate_wrapper(function):
        """
            Paginate wrapper
            :param function: Function
            :return: Wrapper
        """

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
            queryset = await crud.all(db, skip, page_size)

            if not queryset:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Results not found')

            next_page: typing.Optional[str] = None
            previous_page: typing.Optional[str] = None

            if await crud.exist_page(db, skip + page_size, page_size):
                next_page = f'{url}?page={page + 1}&page_size={page_size}'

            if (page - 1) > 0:
                previous_page = f'{url}?page={page - 1}&page_size={page_size}'

            return {
                'next': next_page,
                'previous': previous_page,
                'page': page,
                'results': await function(*args, page=page, page_size=page_size, queryset=queryset, db=db, **kwargs)
            }

        return wrapper

    return paginate_wrapper
