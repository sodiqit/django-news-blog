from functools import reduce
from .models import Category


def group_by_id(prev: list, current: Category):
    """
    Group categories by related id.
    Example: [<Category 1>, <Category 1.3>, <Category 6>, <Category 6.5>] -> [[<Category 1>, <Category 1.3>], [<Category 6>, <Category 6.5>]]
    """
    parent_category_id = current.category_id[0]
    try:
        group: list = list(
            filter(
                lambda x: len(
                    list(
                        filter(
                            lambda y: y.category_id.startswith(parent_category_id), x
                        )
                    )
                )
                > 0,
                prev,
            )
        )[0]
    except IndexError:
        group = []
    if len(group) == 0:
        prev.append(group)
    group.append(current)
    return prev


def find_related_item(parent_id: int):
    """
    Find child categories. Without inner childs.
    """

    def has_child_item_without_childs(ids: list[int], parent_index: int):
        try:
            ids[parent_index + 1]
            try:
                ids[parent_index + 2]
                return False
            except IndexError:
                return True
        except IndexError:
            return False

    def inner_fn(item: Category):
        ids = list(map(int, item.category_id.split(".")))
        parent_index = None
        try:
            parent_index = ids.index(parent_id)
        except ValueError:
            return False
        if parent_index == -1:
            return False
        return has_child_item_without_childs(ids, parent_index)

    return inner_fn


def group_by_parent_category(group: list[Category], item: Category | None = None):
    """
    Group by parent category

    Example:
    [<Category 1>, <Category 1.2>, <Category 1.2.3>]
    ->
    {
        "id": '1',
        "name": 'Category 1',
        "items": [
            {
                "id": '1.2',
                "name": 'Category 1.2',
                "items": [
                    {
                        "id": '1.2.3',
                        "name": 'Category 1.2.3',
                        "items": []
                    }
                ]
            }
        ]
    }
    """
    parent_id = None
    is_first_iteration = item is None
    if is_first_iteration:
        try:
            item = group[0]
        except KeyError:
            return
    parent_id = item.id
    related_items = list(filter(find_related_item(parent_id), group))

    if len(related_items) == 0:
        return {"id": item.category_id, "name": item.title, "items": []}

    return {
        "id": item.category_id,
        "name": item.title,
        "items": [group_by_parent_category(group, x) for x in related_items],
    }


def convert_categories_to_tree(categories: list[Category]):
    grouped_categories: list[list[Category]] = reduce(group_by_id, categories, [])
    data = []

    for group in grouped_categories:
        group.sort(key=lambda category: category.id)
        data.append(group_by_parent_category(group))

    return data
