import csv

f = open('UT_vector.csv', 'r')
rdr = csv.reader(f)
lines = []
idx = 0
for line in rdr:
    if idx == 0: 
        lines.append(line)
        idx = 1
        continue
    line[0] = line[0].split('_')[0] + '.jpg'
    lines.append(line)

f = open('UT_vector_rename.csv', 'w', newline='')
wr = csv.writer(f)
wr.writerows(lines)

f.close()
    
