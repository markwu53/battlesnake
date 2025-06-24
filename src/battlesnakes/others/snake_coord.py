
excel_coord = """
$G$6
$H$6
$I$6
$I$7
$I$8
$I$9
$I$10
$I$11
$H$11
$H$12

"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

