
import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

ases_to_ips = {}
asIP_to_reslience = {}
ips_to_bandwidthN= {}
ips_to_bandwidth= {}
ipResilience = {}
file1_bandwidth_normalized = open('guard_ips_with_bandwidth_yixin.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')

for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)
file1_bandwidth.close()

for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)

for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
file2_as.close()

g = .1 
N = 2075
alpha = .5
def check_resilince_for_tille(ip_to_resilience):
	for ip in ip_to_resilience:
		if ip_to_resilience[ip] > 1:
			return True 
	return False 

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

def get_ip_to_reslience(as_to_reslience):
	ip_to_resilience = {}
	while as_to_reslience:
		to_as, resilience = as_to_reslience.popitem()
		if to_as in ases_to_ips:
			to_ips_in_as = ases_to_ips[to_as]
			for ip in to_ips_in_as:
				ip_to_resilience[ip] = resilience
	return ip_to_resilience

def tille_sampling(ip_to_resilience):
	current_k = g*len(ip_to_resilience)
	new_ip_resilience = {}
	current_reslience_set = set(ip_to_resilience.keys())
	for ip in ip_to_resilience:
		ip_resilience = current_k*ip_to_resilience[ip]
		#print(ip_resilience)
		resilience_denom = 0
		for relay in current_reslience_set:
			resilience_denom += ip_to_resilience[relay]
		ip_resilience = ip_resilience/resilience_denom
		new_ip_resilience[ip] = ip_resilience
	for ip in new_ip_resilience:
		if new_ip_resilience[ip] > 1:
			new_ip_resilience[ip] = 1
			current_reslience_set.remove(ip)
			current_k -= 1
	while check_resilince_for_tille(new_ip_resilience):
		for ip in new_ip_resilience:
			ip_resilience = current_k*new_ip_resilience[ip]
			resilience_denom = 0
			for relay in current_reslience_set:
				resilience_denom += new_ip_resilience[relay]
			ip_resilience = ip_resilience/resilience_denom
			new_ip_resilience[ip] = ip_resilience
		for ip in new_ip_resilience:
			if new_ip_resilience[ip] > 1:
				new_ip_resilience = 1
				current_reslience_set.remove(ip)
				current_k -= 1
	for ip in new_ip_resilience:
		new_ip_resilience[ip] = new_ip_resilience[ip]/(g*len(ip_to_resilience))
	return new_ip_resilience
	
as_to_ip_tille_reslience = dict()

## Performs tille's algorithm 
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		print(key)
		client_as_weights = {}
		ipResilience[key] = dict()
		asIP_to_reslience[key] = dict()
		as_to_reslience = deepcopy(values)
		as_to_ip_tille_reslience[key] = {}
		tilleIpResilience = get_ip_to_reslience(as_to_reslience)
		tille_ip_to_resiliece = tille_sampling(tilleIpResilience)
		while values:
			to_as, resilience = values.popitem()
			if to_as in ases_to_ips:
				to_ips_in_as = ases_to_ips[to_as]
				for to_ip in to_ips_in_as:
					as_to_ip_tille_reslience[key][to_ip] = tille_ip_to_resiliece[to_ip]
			else:
				print("sorry we cannot find the to client asn %s ips" % to_as)
data_file.close()
file_out = open('tille_resiliences_yixin.json', 'w+')
json.dump(as_to_ip_tille_reslience, file_out)
file_out.close()

