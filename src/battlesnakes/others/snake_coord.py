
excel_coord = """

$J$11
$J$12
$I$12
$H$12
$G$12
$F$12
$E$12
$D$12
$D$11
$E$11
$F$11
$G$11
$H$11
$I$11














"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

