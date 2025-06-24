
excel_coord = """
$I$10
$I$9
$J$9
$J$8
$I$8
$H$8
$G$8
$G$9
$F$9
$E$9

"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

