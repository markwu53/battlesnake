
excel_coord = """

$H$10
$H$9
$H$8
$H$7
$G$7
$G$6
$G$5
$F$5
$F$6
$E$6
$D$6
$D$7
$D$8
$E$8
$E$9
$D$9

"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

