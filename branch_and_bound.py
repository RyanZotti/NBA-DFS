from Node import Node
from utilities import sort_items_by_efficiency

items = {0:{'value':727,'weight':32},1:{'value':763,'weight':40},2:{'value':60,'weight':44},
         3:{'value':606,'weight':20},4:{'value':45,'weight':1},5:{'value':370,'weight':29},
         6:{'value':414,'weight':3},7:{'value':880,'weight':13},8:{'value':133,'weight':6},
         9:{'value':820,'weight':39}}

for item_id,item in items.items():
    items[item_id]['value-ratio'] = item['value']/item['weight']

constraints = {'weight':113}
nodes = {}
origin = Node(own_id=0,parent_id=None,all_items=items,included_item_ids=[],excluded_item_ids=[],
              constraints=constraints)
nodes[len(nodes)]=origin
node = nodes[0]
included_item_ids = []
excluded_item_ids = []
remaining_items_sorted = sort_items_by_efficiency(items,included_item_ids,excluded_item_ids)
most_efficient_item = remaining_items_sorted[0]
candidate_included_items = included_item_ids[:]
candidate_included_items.append(most_efficient_item['item_id'])
candidate_excluded_items = excluded_item_ids[:]
candidate_excluded_items.append(most_efficient_item['item_id'])
included_item_node = Node(own_id=len(nodes),parent_id=node.id,all_items=items,
                          included_item_ids=candidate_included_items,
                          excluded_item_ids=excluded_item_ids,
                          constraints=constraints)
print(included_item_node.bound)
excluded_item_node = Node(own_id=len(nodes),parent_id=node.id,all_items=items,
                          included_item_ids=included_item_ids,
                          excluded_item_ids=candidate_excluded_items,
                          constraints=constraints)
print(excluded_item_node.bound)
print('test')