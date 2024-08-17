
from urllib.parse import urlencode
from typing import TypeVar
from fastapi import Request
from fastapi_pagination import Page, Params, add_pagination, paginate
from fastapi_pagination.default import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi_pagination.links import Page

from movies.schemas import CustomPage

T = TypeVar("T")


def get_custom_page(
    page: Page[T], request: Request, params: Params
) -> CustomPage:
    """
    override the default Page fastapi _pagination
    """
    total_pages = (
        page.total if page.total else 0 + params.size - 1
    ) // params.size  # Calculate total pages
    current_page = params.page
    pages_remaining = total_pages - current_page  # Calculate pages remaining

    base_url = str(request.url).split("?")[0]
    query_params = request.query_params

    def create_url(page_num: int) -> str:
        query_params._dict["page"] = page_num #type: ignore
        return f"{base_url}?{urlencode(query_params)}"

    next_url = (
        create_url(current_page + 1) if current_page < total_pages else None
    )
    prev_url = create_url(current_page - 1) if current_page > 1 else None
    return CustomPage(
        results=page.items, #type: ignore
        total=page.total,
        next=next_url,
        prev=prev_url,
        total_pages=total_pages,
        pages_remaining=pages_remaining,
        page_size=page.size, #type: ignore
    )


class CustomParams(Params):
    size: int = 20