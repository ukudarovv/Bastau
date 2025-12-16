"""Pagination utilities"""
from typing import List, Any


def paginate(items: List[Any], page: int, items_per_page: int) -> tuple[List[Any], int, bool, bool]:
    """
    Paginate items list
    
    Returns:
        tuple: (page_items, total_pages, has_prev, has_next)
    """
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page if total_items > 0 else 1
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    
    page_items = items[start_idx:end_idx]
    has_prev = page > 0
    has_next = end_idx < total_items
    
    return page_items, total_pages, has_prev, has_next


def get_page_info(page: int, total_pages: int, total_items: int) -> str:
    """Get pagination info text"""
    if total_items == 0:
        return "Страница 1 из 1 (0 элементов)"
    
    return f"Страница {page + 1} из {total_pages} ({total_items} элементов)"

