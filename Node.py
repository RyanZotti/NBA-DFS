from utilities import sort_items_by_efficiency

class Node:
    
    def _calculate_weight_(self,all_items,included_item_ids):
        weight = 0
        for included_item_id in included_item_ids:
            weight = weight + all_items[included_item_id]['weight']
        return weight
    
    def _calculate_value_(self,all_items,included_item_ids):
        value = 0
        for included_item_id in included_item_ids:
            value = value + all_items[included_item_id]['value']
        return value
    
    def _calculate_bound_(self,all_items,constraints):
        remaining_items_sorted = sort_items_by_efficiency(all_items,self.included_item_ids,self.excluded_item_ids)
        weight = self.weight
        value = self.value
        for item in remaining_items_sorted:
            if item['weight'] + weight <= constraints['weight']:
                value = value + item['value']
                weight = weight + item['weight']
            else:
                leftover_weight = constraints['weight'] - weight
                bound = value + ((leftover_weight/item['weight']) * item['value'])
                return bound
           
    def set_child_ids(self,child_ids):
        self.child_ids = child_ids
           
    def __init__(self,own_id,parent_id,all_items,included_item_ids,excluded_item_ids,constraints):
        self.id = own_id
        self.parent_id = parent_id
        self.included_item_ids = included_item_ids
        self.excluded_item_ids = excluded_item_ids
        self.weight = self._calculate_weight_(all_items,included_item_ids)
        self.value = self._calculate_value_(all_items,included_item_ids)
        self.bound = self._calculate_bound_(all_items,constraints)
        self.child_ids = []
    