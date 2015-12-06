def sort_items_by_efficiency(items,included_item_ids,excluded_item_ids):
    for item_id in items.keys():
        items[item_id]['item_id']=item_id
    remaining_item_ids = set(items.keys()) - set(included_item_ids) - set(excluded_item_ids)
    remaining_items = [items[item_id] for item_id in remaining_item_ids]
    sorted_remaining_items = sorted(remaining_items, key=lambda item: item['value-ratio'],reverse=True)
    return sorted_remaining_items