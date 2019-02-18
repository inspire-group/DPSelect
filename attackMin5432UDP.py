import json
import math
import numpy
import random
from decimal import *
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go



def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

bandwidths = []
file1_bandwidth_normalized_normal = open('guard_ips_with_bandwidth_normalized.txt', 'r')
file1_bandwidth_normalized = open('guard_ips_with_bandwidth_yixin.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
shannon_decrease =  open('min5_decreaseOct5432UDP','w+')
ases_to_ips = {}
ips_to_bandwidthN= {}
ips_to_bandwidth = {}
ip_weighted_prob = {}
epsilon_dict = {}
ip_to_resilience = {}
asIP_to_resilience = {}
alpha = .25
epsilon = 5
test_as = 3
ips_to_bandwidthNormal = {}

change_value = .01
change_value_resilience = .01
ips_to_as = {}
for line in file1_bandwidth_normalized:
	info = line.split(":")
	key =info[0]
	value = info[1]
	ips_to_bandwidthN[key] = float(value)
file1_bandwidth_normalized.close()

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

total_graph = []

'''
Non differentially private Alpha = 0

'''
#Create dictionary of client weights given as 
ratio = .625
alpha = .175
exp1 = 2
exp2 = .75
opt_value = 0
from random import random 
from random import uniform
with open("cg_resilience.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		num_tilted = 0
		while values:
			to_as, resilience = values.popitem()
			if to_as in ases_to_ips:
				to_ips_in_as = ases_to_ips[to_as]
				for to_ip in to_ips_in_as:
					raptor_weight = 0
					if ips_to_bandwidthNormal[to_ip] != 0:
						raptor_weight = (resilience**exp1)*alpha + (1-alpha)*(ips_to_bandwidthNormal[to_ip]**exp2)
						raptor_weight = math.exp(raptor_weight*ratio/alpha)
						#raptor_weight = ips_to_bandwidthNormal[to_ip]
						#raptor_weight = Decimal(ips_to_bandwidthNormal[to_ip]*.5+resilience*.5)
						#raptor_weight = (resilience**exp1)*alpha + (1-alpha)*(ips_to_bandwidthNormal[to_ip]**exp2)
					else:
						raptor_weight = 0
					if to_ip in client_as_weights:
						continue;#client_as_weights[to_ip].append(raptor_weight)
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
			total_weight += Decimal(wei)
		as_to_ip_probability[key][ip] = weight
		ip_to_as_probability[ip][key] = weight
	for ip in as_to_ip_probability[key]:
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			as_to_ip_probability[key][ip][index] = Decimal(weight)/Decimal(total_weight)
			ip_to_as_probability[ip][key][index] = Decimal(weight)/Decimal(total_weight)
as_to_as_probability = {}
for key in as_to_ip_probability:
	as_to_as_probability[key] = dict()
	for ip in as_to_ip_probability[key]:
		for index,weight in enumerate(as_to_ip_probability[key][ip]):
			to_as = ips_to_as[ip]
			if to_as in as_to_as_probability[key]:
				as_to_as_probability[key][to_as]+= Decimal(as_to_ip_probability[key][ip][index])
			else:
				as_to_as_probability[key][to_as] = Decimal(as_to_ip_probability[key][ip][index])
actual_source_as ="5432"
s = [(k, as_to_as_probability[actual_source_as][k]) for k in sorted(as_to_as_probability[actual_source_as], key=as_to_as_probability[actual_source_as].get, reverse=True)]
probabilities = []
names = []
# create array of probabilities
total = 0 
for to_as,next_prob in s:
	if (len(probabilities) > 0 ):
		curent_prob = Decimal(probabilities[len(probabilities)-1])
		total+=Decimal(next_prob)
		probabilities.append(Decimal(curent_prob)+Decimal(next_prob))
		names.append(to_as)
	else:
		total+=next_prob
		probabilities.append(next_prob)
		names.append(to_as)
print(total)
#generate random number
average_entropy = Decimal(0)
lowest_av = 0
#100 Iterations through 
for j in range(0,1000):
	entropies =[]
	as_probabilities = dict()
	for key in as_to_ip_probability:
		as_probabilities[key] = Decimal(1)
	# 100 Guard Selections
	for i in range(0,50):
		#generate random number
		import random
		guard_pick= Decimal(random.randrange(100000000000000000000000000000000000000000000))/100000000000000000000000000000000000000000000
		# Pick the guard 
		name = ""
		index = 0 
		while probabilities[index] < guard_pick:
			index+=1
		name = names[index]
		# Get probability that each AS chose that relay 
		for source_as in as_probabilities:
			as_probabilities[source_as] = Decimal(as_probabilities[source_as])*Decimal(as_to_as_probability[source_as][name])
		entropy =Decimal(0)
		shannon_probabilities = dict()
		total_probability = Decimal(0)
		for source_as in as_probabilities:
			total_probability += Decimal(as_probabilities[source_as])
		for source_as in as_probabilities:
			shannon_probabilities[source_as] =  Decimal(as_probabilities[source_as])/Decimal(total_probability)
		max_probability = 0 
		s = [(k, shannon_probabilities[k]) for k in sorted(shannon_probabilities, key=shannon_probabilities.get, reverse=True)]
		for source_as in shannon_probabilities:
			if shannon_probabilities[source_as] >  max_probability:
				max_probability = shannon_probabilities[source_as]
			ctx = Context(prec=40)
		two = Decimal(2)
		entropy = -ctx.divide(Decimal(max_probability).ln(ctx), two.ln(ctx))
		entropies.append(entropy)
	shannon_decrease.write("as5432rc"+str(j)+"=")
	shannon_decrease.write("[")
	for g in range(0,len(entropies)):
		shannon_decrease.write(str(float(entropies[g]))+",")
	shannon_decrease.write("]")
	shannon_decrease.write("\n")
