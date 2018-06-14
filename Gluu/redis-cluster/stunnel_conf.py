import sys

s = open(sys.argv[1]).read()
s = s.replace('$NODE_01', sys.argv[2])
s = s.replace('$NODE_02', sys.argv[3])
s = s.replace('$NODE_03', sys.argv[4])
f = open(sys.argv[1], 'w')
f.write(s)
f.close()
