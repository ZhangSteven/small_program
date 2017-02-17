# coding=utf-8



class MatchedItemNotFound(Exception):
	pass



def match(list_a, list_b):
	"""
	Match items in list_a to items in list_b. If all items in list_a find a 
	matched item in list_b, then a list of tuples are returned, as:

	(item_a1, item_b1), (item_a2, item_b2), ... (item_aN, item_bN)

	where item_a1 and item_b1 are matched items, etc. Two items in list_a
	cannot match to the same item in list_b.

	but if any item in list_a doesn't find a matched item in list_b, then 
	an exception is thrown.
	"""
	matched_position = []
	for i in range(len(list_a)):
		if i < len(matched_position):
			continue

		matched = False
		for j in range(len(list_b)):
			if not j in matched_position and is_matched(list_a[i], list_b[j]):
				matched_position.append(j)
				matched = True
				break

		if not matched:
			print('item {0} in list_a: {1} does not find a matched item in list_b'.
					format(i, list_a[i]))
			raise MatchedItemNotFound()

	# print(matched_position)
	return create_matched_list(list_a, list_b, matched_position)



def is_matched(item_a, item_b):
	if abs(item_a + item_b) < 0.1:
		return True

	return False



def create_matched_list(list_a, list_b, matched_position):
	matched_list = []
	for i in range(len(list_a)):
		# print(i)
		matched_list.append((list_a[i], list_b[matched_position[i]]))

	return matched_list



def show_list(list_items):
	for item in list_items:
		print(item)



if __name__ == '__main__':
	list_a = [1, 2, 3]
	list_b = [-1, -2, -3, -4]
	show_list(match(list_a, list_b))
	print('')

	list_a = [1, 4, 3]
	list_b = [-1, -2, -3, -4]
	show_list(match(list_a, list_b))
	print('')

	list_a = [2, 3, 1]
	list_b = [-4, -1, -3, -2]
	show_list(match(list_a, list_b))

	# list_a = [1, 3, 1]
	# list_b = [-1, -2, -3, -4]
	# show_list(match(list_a, list_b))

	list_a = [1, 2, 3, 2]
	list_b = [-1, -2, -3]
	show_list(match(list_a, list_b))