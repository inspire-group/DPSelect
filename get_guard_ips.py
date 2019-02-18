

import re

guard_examined =""
file = open('guard_ips.txt', 'w')
ip_regex = r'(?:\d{1,3}\.)+(?:\d{1,3})'
consensus = open('2017-09-01-23-00-00-consensus','r')
#Writes begin and noasname so that the document can be used in 
#netcat whois command
file.write("begin")
file.write('\n')
file.write("noasname")
file.write('\n')
for line in consensus:
	if line[0] == 'r' and line[1] == ' ':
		guard_examined = line
	elif line[0] == 's' and len(guard_examined) > 0 :
		if 'Guard' in line:
			guard_ip = str(re.search(ip_regex,guard_examined).group(0)) 
			file.write(guard_ip)
			file.write('\n')
file.write("end")
file.write('\n')
file.close()


