from utilities import sort_items_by_efficiency

class Node:
    
    def _calculate_weight_(self,all_items,included_item_ids,constraints):
        weights = {}
        for constraint in constraints.keys():
            weight = 0
            for included_item_id in included_item_ids:
                weight = weight + all_items[included_item_id][constraint]
            weights[constraint]=weight
        return weights
    
    def _calculate_value_(self,all_items,included_item_ids):
        value = 0
        for included_item_id in included_item_ids:
            value = value + all_items[included_item_id]['value']
        return value
    
    def _calculate_bound_(self,all_items,constraints):
        remaining_items_sorted = sort_items_by_efficiency(all_items,self.included_item_ids,self.excluded_item_ids)
        weights = self.weights
        value = self.value
        for item in remaining_items_sorted:
            for constraint_name, constraint_value in constraints.items():
                if item[constraint_name] + weights[constraint_name] <= constraint_value:
                    value = value + item['value']
                    weights[constraint_name] = weights[constraint_name] + item[constraint_name]
                else:
                    leftover_weight = constraint_value - weights[constraint_name]
                    bound = value + ((leftover_weight/item[constraint_name]) * item['value'])
        return bound
           
    def set_child_ids(self,child_ids):
        self.child_ids = child_ids
           
    def __init__(self,own_id,parent_id,all_items,included_item_ids,excluded_item_ids,constraints):
        self.id = own_id
        self.parent_id = parent_id
        self.included_item_ids = included_item_ids
        self.excluded_item_ids = excluded_item_ids
        self.weights = self._calculate_weight_(all_items,included_item_ids,constraints)
        self.value = self._calculate_value_(all_items,included_item_ids)
        self.bound = self._calculate_bound_(all_items,constraints)
        self.child_ids = []
    