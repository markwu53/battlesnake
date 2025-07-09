
excel_coord = """

$D$10
$E$10
$F$10
$G$10
$H$10
$I$10
$I$11
$J$11
$J$12
$I$12
$H$12
$H$11
$G$11
$F$11























"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

