import re

words=['123,123','323','abc','1234,123']
for word in words:
  print(re.match('^\d{1,3}(,\d{3})*$',word)
