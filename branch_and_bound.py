from Node import Node

items = {0:{'value':727,'weight':32},1:{'value':763,'weight':40},2:{'value':60,'weight':44},
         3:{'value':606,'weight':20},4:{'value':45,'weight':1},5:{'value':370,'weight':29},
         6:{'value':414,'weight':3},7:{'value':880,'weight':13},8:{'value':133,'weight':6},
         9:{'value':820,'weight':39}}
for item_id,item in items.items():
    items[item_id]['value-ratio'] = item['value']/item['weight']
constraints = {'weight':113}
nodes = {}

origin = Node(own_id=0,parent_id=None,all_items=items,included_item_ids=[],excluded_item_ids=[],constraints=constraints)
nodes[len(nodes)]=origin
print('test')