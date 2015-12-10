from Node import Node
from utilities import sort_items_by_efficiency

items = {1:{'value':727,'weight':32},2:{'value':763,'weight':40},3:{'value':60,'weight':44},
         4:{'value':606,'weight':20},5:{'value':45,'weight':1},6:{'value':370,'weight':29},
         7:{'value':414,'weight':3},8:{'value':880,'weight':13},9:{'value':133,'weight':6},
         10:{'value':820,'weight':39}}

def n(index):
    node = nodes[index]
    print('id:{id} max:{value}, w:{weight} v:{v}, b:{bound} parent:{parent} children:{children}, incl:{incl}, excl:{excl}'.format(id=node.id,excl=node.excluded_item_ids,incl=node.included_item_ids,v=node.value,value=max_value,weight=node.weights,bound=node.bound,children=node.child_ids,parent=node.parent_id))

for item_id,item in items.items():
    items[item_id]['value-ratio'] = item['value']/item['weight']

constraints = {'weight':113}
nodes = {}
origin = Node(own_id=0,parent_id=None,all_items=items,included_item_ids=[],
              excluded_item_ids=[],constraints=constraints,generic_constraint='weight')
nodes[0]=origin
max_value = 0
node = origin
while origin.bound is not max_value:
    n(node.id)
    if len(node.child_ids) > 0: # Explore existing nodes
        if (nodes[node.child_ids[0]].bound <= max_value or any(nodes[node.child_ids[0]].weights[constraint_name] > constraint_value for constraint_name,constraint_value in constraints.items())) and (nodes[node.child_ids[1]].bound <= max_value or any(nodes[node.child_ids[1]].weights[constraint_name] > constraint_value for constraint_name,constraint_value in constraints.items())):
            possible_bounds = []
            if all(nodes[node.child_ids[1]].weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()):
                possible_bounds.append(nodes[node.child_ids[1]].bound)
            if all(nodes[node.child_ids[0]].weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()):
                possible_bounds.append(nodes[node.child_ids[0]].bound)
            nodes[node.id].bound = max(possible_bounds)
            if node.id > 0: 
                node = nodes[node.parent_id]
            else: # Searched has finished and you have arrived at origin, which has no parent
                continue
        elif nodes[node.child_ids[0]].bound > max_value and all(nodes[node.child_ids[0]].weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()):
            node = nodes[node.child_ids[0]]
        elif nodes[node.child_ids[1]].bound > max_value and all(nodes[node.child_ids[1]].weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()):
            node = nodes[node.child_ids[1]]
    else: # Create new nodes because this split hasn't been explored yet
        included_item_ids = node.included_item_ids
        excluded_item_ids = node.excluded_item_ids
        remaining_items_sorted = sort_items_by_efficiency(items,included_item_ids,excluded_item_ids,constraints,'weight')  
        most_efficient_item = remaining_items_sorted[0]
        candidate_included_items = included_item_ids[:]
        candidate_included_items.append(most_efficient_item['item_id'])
        included_item_node = Node(own_id=len(nodes),parent_id=node.id,all_items=items,
                                  included_item_ids=candidate_included_items,
                                  excluded_item_ids=excluded_item_ids,
                                  constraints=constraints,generic_constraint='weight')
        nodes[included_item_node.id]=included_item_node
        candidate_excluded_items = excluded_item_ids[:]
        candidate_excluded_items.append(most_efficient_item['item_id'])
        excluded_item_node = Node(own_id=len(nodes),parent_id=node.id,all_items=items,
                                  included_item_ids=included_item_ids,
                                  excluded_item_ids=candidate_excluded_items,
                                  constraints=constraints,generic_constraint='weight')
        nodes[excluded_item_node.id]=excluded_item_node
        nodes[node.id].set_child_ids([included_item_node.id,excluded_item_node.id])
        better_node = None
        if all(included_item_node.weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()) and all(excluded_item_node.weights[constraint_name] <= constraint_value for constraint_name,constraint_value in constraints.items()):
            if included_item_node.bound > excluded_item_node.bound:
                if included_item_node.bound > max_value:
                    better_node = included_item_node
                    worse_node = excluded_item_node
                    max_value = max(better_node.value,max_value)
                    print("Include: "+str(most_efficient_item['item_id'])+": profit "+str(included_item_node.value)+" weight "+str(included_item_node.weights['weight'])+" Exclude: profit "+str(excluded_item_node.value)+" weight "+str(excluded_item_node.weights['weight']))
                else:
                    node = nodes[node.parent_id]
                    continue
            else:
                better_node = excluded_item_node
                worse_node = included_item_node
                max_value = max(better_node.value,max_value)
                print("Exclude: "+str(most_efficient_item['item_id'])+" profit "+str(excluded_item_node.value)+" weight "+str(excluded_item_node.weights['weight'])+" bound: "+str(excluded_item_node.bound)+" Include: profit "+str(included_item_node.value)+" weight "+str(included_item_node.weights['weight'])+" bound: "+str(included_item_node.bound))
        elif any(included_item_node.weights[constraint_name] > constraint_value for constraint_name,constraint_value in constraints.items()):
            nodes[node.id].bound = node.value # 
            nodes[included_item_node.id].bound = included_item_node.value
            node = nodes[node.parent_id]
            continue
        if better_node is not None:
            node = better_node
print('Best node:')
for node_id, node in nodes.items():
    if node.value == max_value and len(node.child_ids) > 0:
        n(node_id)
