import json

#filter management




def add_to_filter(filter:str,item:str):
    with open(filter, "r") as item_list:
        items = json.load(item_list)
        if item not in items:
            items.append(item)
        with open(filter, "w") as item_list:
            item_list.write(json.dumps(items))

def remove_from_filter(filter:str,item:str):
    with open(filter, "r") as item_list:
        items = json.load(item_list)
        if item in items:
            items.remove(item)
        with open(filter, "w") as item_list:
            item_list.write(json.dumps(items))
            