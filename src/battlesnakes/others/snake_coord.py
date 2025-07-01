
excel_coord = """


$B$7
$C$7
$D$7
$E$7
$E$6
$E$5
$E$4
$F$4
$G$4
$H$4
$H$3
$G$3
$F$3
$F$2
$E$2
$D$2
$C$2
$B$2
$B$3
$C$3
$C$4


"""

coord = excel_coord.splitlines()
coord = [line.strip() for line in coord if len(line.strip()) != 0]
coord = [line.replace("$", " ") for line in coord]
coord = [line.split() for line in coord]
coord = [(ord(a)-ord("A"), int(b)) for a,b in coord]
coord = [(a-1, 12-b) for a,b in coord]
#for item in coord: print(item)
print(coord)

