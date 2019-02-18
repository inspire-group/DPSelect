import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np

file1_bandwidth_normalized = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file_ouput = open('mdUDPOverTime.txt','w+')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidthN= {}
ips_to_bandwidth= {}
ip_weighted_prob = {}
epsilon_dict = {}
alpha = .175
for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)

for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)

for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
total_as_weight = 0
zeroes =set()
max_resilience = 0
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	for key, values in data.items():
		while values:
			to_as, resilience = values.popitem()
			if resilience > max_resilience:
				max_resilience = resilience
print(max_resilience)
alpha = .175
ratio = .625/alpha
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		while values:
			to_as, resilience = values.popitem()
			weighted_resilience = resilience/max_resilience
			if to_as in ases_to_ips:
				to_ips_in_as = ases_to_ips[to_as]
				for to_ip in to_ips_in_as:
					raptor_weight = 0
					if ips_to_bandwidthN[to_ip] != 0:
						raptor_weight = (((weighted_resilience**2))*alpha)+ (1-alpha)*((ips_to_bandwidthN[to_ip]**.75))
						raptor_weight = math.exp(raptor_weight*ratio)
						if to_ip in client_as_weights:
							client_as_weights[to_ip].append(raptor_weight)
						else:
							client_as_weights[to_ip] = [raptor_weight]
			else:
				print("sorry we cannot find the to client asn %s ips" % to_as)
		weights[key] = deepcopy(client_as_weights)
ip_weights = {}
ip_epsilons = {}
as_to_ip_probability = dict()
ip_to_as_probability = dict()
weights_copy = deepcopy(weights)
while weights_copy:
	key, values = weights_copy.popitem()
	as_to_ip_probability[key] = dict()
	total_weight = 0 
	while values:
		ip, weight = values.popitem()
		if ip not in ip_to_as_probability:
			ip_to_as_probability[ip] = dict()
		for wei in weight:
			total_weight += wei
		as_to_ip_probability[key][ip] =weight 
		ip_to_as_probability[ip][key] = weight
	for ip in as_to_ip_probability[key]:
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			# Probabilility a as client from key chooses the ip 
			as_to_ip_probability[key][ip][index] = weight/total_weight
			#  Probabilility a as client from key chooses the ip 
			ip_to_as_probability[ip][key][index] = weight/total_weight
ip_epsilons =dict()
for ip in  ip_to_as_probability:
	max_probability =0
	min_probability = 500000
	for key in ip_to_as_probability[ip]:
		for index, weight in enumerate(ip_to_as_probability[ip][key]):
			if weight > max_probability:
				max_probability = weight
			if weight  < min_probability:
				min_probability = weight
	if (max_probability == 0 and min_probability == 0):
		ip_epsilons[ip] = 0
	else:
		ip_epsilons[ip] = math.log(max_probability/min_probability)
average_epsilon = 0
for ip in ip_epsilons:
	average_epsilon += ip_epsilons[ip]
print(average_epsilon/len(ip_epsilons))
graph_ips = ip_epsilons.keys()
graph_epsilons = []
graph_ips = sorted(graph_ips)
file_ouput.write("[")
for ip in ip_epsilons:
	file_ouput.write(str(float(ip_epsilons[ip]))+",")
file_ouput.write("]")
file_ouput.write("\n")
