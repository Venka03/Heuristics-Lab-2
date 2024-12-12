lst = [1, 2, 3]
print(*lst)  # Equivalent to print(1, 2, 3)

lst = [1, 2, 3]
new_lst = [0, *lst, 4]  # [0, 1, 2, 3, 4]
print(new_lst)

lst = [1, 2, 3, 4, 5]
a, *b, c = lst
print(a)  # Output: 1
print(b)  # Output: [2, 3, 4]
print(c)  # Output: 5

lst1 = [1, 2, 3]
lst2 = [4, 5, 6]
combined = [*lst1, *lst2]  # Combines both lists
print(combined)
