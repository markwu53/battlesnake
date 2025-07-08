
excel_coord = """

$F$10
$E$10
$D$10
$D$9
$D$8
$D$7
$D$6
$C$6
$B$6
$B$5
$B$4
$C$4
$D$4

"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

