def path_connected(a, occupied=None):
    if occupied == None:
        occupied = 5
    print(a+occupied)

path_connected(3)
path_connected(3, 4)
path_connected(3, occupied=4)