import os
import glob
import csv

path = 'C:\\Users\\gfirest\\Box Sync\\C-Bo SciPar\\PE degradation\\Data\\oceanView\\9-20 cold box'

filenames = glob.glob(os.path.join(path, 'cold*.txt'))
i = 0
filelist = [open(os.path.join(path, 'inputWaves.csv'))]
readerlist = [ csv.reader(open(os.path.join(path, 'inputWaves.csv')), delimiter="\t") ]
while i < (len(filenames)-1):
  for x in range(i, min(i+1000,len(filenames))):
    filelist.append(open(filenames[x]))
    readerlist.append(csv.reader(open(filenames[x]), delimiter="\t"))
  i = min(i+3000,len(filenames))
  outfile = open(os.path.join(path,'output'+str(i)+'.csv'),'w',newline='')
  writer = csv.writer(outfile, quotechar = ' ', quoting=csv.QUOTE_MINIMAL)
  while True:
    try:
      row = []
      readeriter = iter(readerlist)
      first = next(readeriter)
      for entry in next(first):
        row.append(entry)
      for reader in readeriter:
        reader_line = next(reader)
        if(len(reader_line)>0):
          row.append(reader_line[len(reader_line)-1])
      writer.writerow(row)
    except StopIteration:
      break
  outfile.close()
  for file in filelist:
    file.close()
  filelist = [open(os.path.join(path,'output'+str(i)+'.csv'))]
  readerlist = [csv.reader(open(os.path.join(path,'output'+str(i)+'.csv')), delimiter=",") ]


#readerlist = [csv.reader(open(filename), delimiter="\t") for filename in glob.glob(os.path.join(path, 'cold*.txt'))]
#readerWL = csv.reader(open(os.path.join(path, 'dark box_FLMT028651_09-20-27-002.txt')), delimiter="\t") 
#
#with open(os.path.join(path,'output.csv'),'w', newline='') as csvfile:
#  writer = csv.writer(csvfile, quotechar = ' ', quoting=csv.QUOTE_MINIMAL)
#  row = [' ']
#  next(readerWL)
#  for item in readerlist:
#    row.append(next(item)[0])
#  writer.writerow(row)  
#  
#  next(readerWL)
#  for item in readerlist:
#    row.append(next(item))  # this is the most convenient way to skip a line without thinking about it too much
#  
#  for x in range(2,14):
#    next(readerWL)
#    row = [' ']
#    for item in readerlist:
#      row.append(next(item)[0])
#    writer.writerow(row)
#  
#  while True:
#    try:
#      row = [next(readerWL)[0]]
#      for item in readerlist:
#        row.append(next(item)[1])
#      writer.writerow(row)
#    except StopIteration:#
#      break
 
 
#writer.writerow(row.append(next(item)[0]) for item in readerlist)

#  for x in range(0,1):
#      writer.writerow( col[x][0]+', ' for col in datalist)
#  for x in range(2,13):
#      writer.writerow( col[x][0]+', ' for col in datalist)
#  for x in range(14,len(datalist[0])):
#      writer.writerow( col[x][0]+' ,' + col[x][1] for col in datalist)
      