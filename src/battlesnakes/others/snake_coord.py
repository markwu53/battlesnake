
excel_coord = """

$F$10
$F$9
$G$9
$H$9
$I$9
$J$9
$J$8
$J$7
$I$7
$I$6
$I$5
$I$4
$H$4
$G$4










"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

