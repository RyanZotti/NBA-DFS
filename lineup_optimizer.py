import pymysql
from Node import Node
from utilities import sort_items_by_efficiency
con = pymysql.connect(
    host='localhost', unix_socket='/tmp/mysql.sock', 
    user='root', passwd="", db='NBA')
mysql = con.cursor(pymysql.cursors.DictCursor)

mysql.execute("""
select full_name,target_dfs_points,salary,position,
if(position='PG',1,0) as PG,
if(position='SG',1,0) as SG,
if(position='SF',1,0) as SF,
if(position='PF',1,0) as PF,
if(position='C',1,0) as C
from dfs_optimizer_performance_test
""")

items = {}
for row_index,row in enumerate(mysql.fetchall()):
    items[row_index]={'full_name':row['full_name'],'value':row['target_dfs_points'],
                      'salary':row['salary'],'position':row['position'],'PG':row['PG'],
                      'SG':row['SG'],'SF':row['SF'],'PF':row['PF'],'C':row['C']}

def n(index):
    node = nodes[index]
    print('id:{id} max:{value}, w:{weight} b:{bound} parent:{parent} children:{children}'.format(id=node.id,value=max_value,weight=node.weights,bound=node.bound,children=node.child_ids,parent=node.parent_id))

for item_id,item in items.items():
    items[item_id]['value-ratio'] = item['value']/item['salary']

constraints = {'salary':60000,'PG':2,'SG':2,'SF':2,'PF':2,'C':1}
nodes = {}
origin = Node(own_id=0,parent_id=None,all_items=items,included_item_ids=[],
              excluded_item_ids=[],constraints=constraints)
nodes[0]=origin
max_value = 0
node = origin
node_count = 0
while origin.bound is not max_value:
    n(node.id)
    if len(node.child_ids) > 0: # Explore existing nodes
        # Check if all constraints are met
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
        remaining_items_sorted = sort_items_by_efficiency(items,included_item_ids,excluded_item_ids,constraints,'salary') 
        most_efficient_item = remaining_items_sorted[0]
        candidate_included_items = included_item_ids[:]
        candidate_included_items.append(most_efficient_item['item_id'])
        node_count = node_count + 1
        included_item_node = Node(own_id=node_count,parent_id=node.id,all_items=items,
                                  included_item_ids=candidate_included_items,
                                  excluded_item_ids=excluded_item_ids,
                                  constraints=constraints)
        nodes[included_item_node.id]=included_item_node
        candidate_excluded_items = excluded_item_ids[:]
        candidate_excluded_items.append(most_efficient_item['item_id'])
        node_count = node_count + 1
        excluded_item_node = Node(own_id=node_count,parent_id=node.id,all_items=items,
                                  included_item_ids=included_item_ids,
                                  excluded_item_ids=candidate_excluded_items,
                                  constraints=constraints)
        nodes[excluded_item_node.id]=excluded_item_node
        nodes[node.id].set_child_ids([included_item_node.id,excluded_item_node.id])
        better_node = None
        for constraint_name, constraint_value in constraints.items():
            if included_item_node.weights[constraint_name] <= constraint_value and excluded_item_node.weights[constraint_name] <= constraint_value:
                if included_item_node.bound > excluded_item_node.bound:
                    if included_item_node.bound > max_value:
                        better_node = included_item_node
                        worse_node = excluded_item_node
                        max_value = max(better_node.value,max_value)
                        #print("Include: "+str(most_efficient_item['item_id'])+": profit "+str(included_item_node.value)+" weight "+str(included_item_node.weight)+" Exclude: profit "+str(excluded_item_node.value)+" weight "+str(excluded_item_node.weight))
                    else:
                        node = nodes[node.parent_id]
                        continue
                else:
                    better_node = excluded_item_node
                    worse_node = included_item_node
                    max_value = max(better_node.value,max_value)
                    #print("Exclude: "+str(most_efficient_item['item_id'])+" profit "+str(excluded_item_node.value)+" weight "+str(excluded_item_node.weight)+" Include: profit "+str(included_item_node.value)+" weight "+str(included_item_node.weight))
            elif included_item_node.weights[constraint_name] > constraint_value:
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
        print(included_item_ids)
print('finished')
