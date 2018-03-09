# Simple script to pull differences between LDIF data. Used mostly as a sanity check for data.

import sys
from ldif import LDIFParser,LDIFWriter

file1="idp1.ldif"
file2="idp2.ldif"

ld1 = ldif.LDIFRecordList.parse(file1)
ld2 = ldif.LDIFRecordList.parse(file2)

for line in ld1:
    if line in ld2:
        continue
    elif line not in ld2:
        print(LDIFWriter.unparse(line))
