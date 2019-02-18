

import json
import math
from copy import deepcopy


file1_bandwidth_normalized_normal = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
ases_to_ips = {}
ips_to_bandwidthN= {}
ips_to_bandwidth = {}
ip_weighted_prob = {}
ip_to_resilience = {}
asIP_to_resilience = {}
ips_to_bandwidthNormal = {}

change_value = .01
change_value_resilience = .01


for line in file1_bandwidth_normalized_normal:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthNormal[key] = float(value)
file1_bandwidth_normalized_normal.close()
for line in file1_bandwidth:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidth[key] = float(value)
file1_bandwidth.close()
for line in file2_as:
	info = line.split('|')
	key = info[0].strip(' ')
	value = info[1].strip('\n').strip(' ')
	if key in ases_to_ips:
		ases_to_ips[key].append(value)
	else:
		ases_to_ips[key] = [value]
	ips_to_as[value] = key
file2_as.close()
with open("cg_resilience.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			asIP_to_resilience[key] = dict()
			while values:
				to_as, resilience = values.popitem()
				if to_as in ases_to_ips:
					to_ips_in_as = ases_to_ips[to_as]
					for ip in to_ips_in_as:
						if ip in asIP_to_resilience[key]:
							asIP_to_resilience[key][ip].append(resilience)
						else:
							asIP_to_resilience[key][ip] = [resilience]

ratio = .625
alpha = .25 # Starting value for alpha 
exp1 = 4 # Starting value for exp1
exp2 = 4 # Starting value fo exp2
opt_value = 0
from random import random 
from random import uniform
for i in range(0,1000000):
	old_alpha = alpha
	old_exp1 = exp1
	old_exp2 = exp2
	value = random()
	if (value < 1/6.0):
		alpha+=.01
	elif (value <2/6.0 and alpha >0):
		alpha-=.01
	elif (value <3/6.0):
		exp1+=uniform(0,.25)
	elif (value < 4/6.0):
		exp1-=uniform(0,.25)
	elif (value <5.0/6):
		exp2+= uniform(0,.25)
	else:
		exp2-= uniform(0,.25)
	with open("cg_resilience.json") as data_file: 
		data = json.load(data_file)
		weights = {}
		for key, values in data.items():
			client_as_weights = {}
			while values:
				to_as, resilience = values.popitem()
				if to_as in ases_to_ips:
					to_ips_in_as = ases_to_ips[to_as]
					for to_ip in to_ips_in_as:
						raptor_weight = 0
						if ips_to_bandwidthNormal[to_ip] != 0:
							raptor_weight = (resilience**exp1)*alpha + (1-alpha)*(ips_to_bandwidthNormal[to_ip]**exp2)
							raptor_weight = math.exp(raptor_weight*ratio/alpha)
						else:
							raptor_weight = 0
						if to_ip in client_as_weights:
							client_as_weights[to_ip].append(raptor_weight)
						else:
							client_as_weights[to_ip] = [raptor_weight]
			weights[key] = deepcopy(client_as_weights)
	data_file.close()
	# Determine the probabilities of selecting a given ip
	total_as_resilience = 0
	as_to_ip_probability = {}
	ip_to_as_probability = {}
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
				as_to_ip_probability[key][ip][index] = weight/total_weight
				ip_to_as_probability[ip][key][index] = weight/total_weight
	as_bandwidths = dict()
	as_to_resilience = dict()
	number_ases = 0
	for key in as_to_ip_probability:
		number_ases+=1
		resilience = 0 
		as_bandwidths[key] = 0
		for ip in as_to_ip_probability[key]:
			num_in_list = 0 
			for index,weight in enumerate(as_to_ip_probability[key][ip]):
				num_in_list += 1
				resilience += weight*asIP_to_resilience[key][ip][index]
				as_bandwidths[key]+= weight*ips_to_bandwidth[ip]
		as_to_resilience[key] = resilience
	average_bandwidth = 0
	for key in as_bandwidths:
		average_bandwidth += as_bandwidths[key]
	average_bandwidth = average_bandwidth/number_ases
	average_resilience = 0 
	for key in as_to_resilience:
		average_resilience +=as_to_resilience[key]
	average_resilience = average_resilience/len(as_to_resilience)
	if (average_bandwidth/100000*.5+average_resilience*.5 > opt_value):
		opt_value = average_bandwidth/100000+average_resilience
	elif(random() < .05):
		opt_value = average_bandwidth/100000*.5+average_resilience*.5
	else: 
		alpha = old_alpha
		exp1 = old_exp1
		exp2 = old_exp2
	print(alpha)
	print(exp1)
	print(exp2)
	print(opt_value)
	print(average_resilience)
	print(average_bandwidth)