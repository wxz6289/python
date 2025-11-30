from csv import writer

with open('test.csv', '+w') as csv_file:
  writer = writer(csv_file)
  writer.writerow(('a', 'b', 'c'))
  for i in range(3):
    writer.writerow((i, i**2, i+2))
