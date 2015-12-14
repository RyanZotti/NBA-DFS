def sort_items_by_efficiency(items,included_item_ids,excluded_item_ids,constraints,constraint_name):
    for item_id in items.keys():
        items[item_id]['item_id']=item_id
    filtered_items = {}
    for item_id, item in items.items():
        if item[constraint_name] > 0:
            filtered_items[item_id] = item
    remaining_item_ids = set(filtered_items.keys()) - set(included_item_ids) - set(excluded_item_ids)
    remaining_items = [items[item_id] for item_id in remaining_item_ids]
    sorted_remaining_items = sorted(remaining_items, key=lambda item: item['value-ratio'],reverse=True)
    return sorted_remaining_items

# Only to relevant for backtesting
def calculate_target_value(items,included_item_ids):
    total_dfs_points = 0
    for item_id in included_item_ids:
        total_dfs_points = total_dfs_points + items[item_id]['DFS_target']
    return total_dfs_points