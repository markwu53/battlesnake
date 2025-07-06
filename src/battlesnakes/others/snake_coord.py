
excel_coord = """

$G$7
$G$8
$G$9
$F$9
$E$9
$E$10
$F$10
$G$10
$H$10
$H$11
$G$11
$F$11
$E$11
$D$11
$C$11
$C$10
$C$9
$C$8
$C$7

"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

