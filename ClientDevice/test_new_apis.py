import requests
from api_call import DeliveryDetectorBox

def test():
    box = DeliveryDetectorBox(1)
    slot_index = 0
    all_users = box.get_all_assigned_users()
    all_orders = box.get_all_assigned_orders()
    num_slots = 8
    user_slots = []
    user_order_dict = {}
    if len(all_users) > num_slots:
        # throw an error here and do not proceed
        # too many users are assigned to this box
        # need to implement error logic
        user_slots.append({'error': 'too many users assigned to this box'})
        return 

    # populate the order dict
    for order in all_orders.values():
        order_num = order[0]
        user_name = order[1]
        # check if the user is assigned to this box
        if user_name in all_users:
            print('Looking at ' + user_name + ' Keys are: ' + str(user_order_dict.keys()))
            if user_name in user_order_dict.keys():
                user_order_dict[user_name].append(order_num)
            else:
                user_order_dict.update({user_name: [order_num]})

    # assign the users to slots and add valid order numbers
    for user in all_users:
        orders = user_order_dict[user] if user in user_order_dict.keys() else -1 
        user_slots.append({'user_name': user, 'order_numbers': orders, 'slot': slot_index})
        slot_index += 1
    
    print(user_slots)



if __name__ == '__main__':
    test()
