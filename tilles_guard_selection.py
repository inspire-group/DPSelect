import json
import math
from copy import deepcopy
import plotly.offline as py
import plotly.graph_objs as go

ases_to_ips = {}
asIP_to_resilience = {}
ips_to_bandwidthN= {}
ips_to_bandwidth= {}
ipResilience = {}
file1_bandwidth_normalized = open('guard_ips_with_bandwidth_yixin.txt', 'r')
file1_bandwidth= open('guard_ips_with_bandwidth.txt', 'r')
file2_as= open('list02','r')
file_ouput = open('shannonOverTime.txt','w+')

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
	current_k = g*N
	print(current_k)
	new_ip_resilience = {}
	current_reslience_set = ip_to_resilience.keys()
	for ip in ip_to_resilience:
		ip_resilience = current_k*ip_to_resilience[ip]
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
		for ip in ip_to_resilience:
			ip_resilience = current_k*ip_to_resilience[ip]
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
	#for ip in new_ip_resilience:
		#new_ip_resilience[ip] = new_ip_resilience[ip]/(g*N)
	return new_ip_resilience
alpha =.5
with open("tille_resiliences_yixin.json") as data_file: 
	data = json.load(data_file)
	weights = {}
	for key, values in data.items():
		client_as_weights = {}
		ipResilience[key] = dict()
		while values:
			to_ip, resilience = values.popitem()
			raptor_weight = 0
			if ips_to_bandwidthN[to_ip] != 0:
				#raptor_weight = resilience*alpha + (1-alpha)*ips_to_bandwidthN[to_ip]
				#raptor_weight = math.exp(raptor_weight*450*2)
				raptor_weight = alpha*resilience+ alpha*ips_to_bandwidthN[to_ip]
				if to_ip in client_as_weights:
					client_as_weights[to_ip].append(raptor_weight)
					ipResilience[key][to_ip].append(reslience)
				else:
					client_as_weights[to_ip] = [raptor_weight]
					ipResilience[key][to_ip] = [resilience]
		weights[key] = deepcopy(client_as_weights)
data_file.close()
'''
ip_weights = {}
ip_probabilities = {}
ip_epsilons = {}
ovh_data = []
num_values = 0
num_key_values =0
while weights:
	key, values = weights.popitem()
	while values:
		num_values +=1
		ip, weight = values.popitem()
		if ip not in ip_weights:
			ip_weights[ip] = [weight[0]]
			for wei in weight[1:]:
				ip_weights[ip].append(wei)
		else:
			for wei in weight[0:]:
				ip_weights[ip].append(wei)
		if float(key) == 3:
			if len(ovh_data) > 0:
				ovh_data.append([ip,weight])
			else:
				ovh_data = [[ip,weight]]
for ip in ip_weights:
	max_ip_weight = 0
	min_ip_weight = 3
	total_ip_weight = 0
	ip_weight_list = ip_weights[ip]
	for weight in ip_weight_list:
		total_ip_weight += weight
		if weight > max_ip_weight:
			max_ip_weight = weight
		if weight < min_ip_weight:
			min_ip_weight = weight
	if total_ip_weight != 0:
		min_ip_weight = min_ip_weight/total_ip_weight
		max_ip_weight = max_ip_weight/total_ip_weight
	num_ases = 0
	for index, weight in enumerate(ip_weights[ip]):
		if total_ip_weight != 0:
			ip_weights[ip][index] = weight/total_ip_weight
			num_ases +=1
		#print(ip_weights[ip][index])
	if min_ip_weight != 0  and max_ip_weight!= 0:
		ip_epsilon = math.log(max_ip_weight/min_ip_weight)
	elif min_ip_weight == 0 and max_ip_weight == 0:
		ip_epsilon = 0
	elif max_ip_weight != 0 and min_ip_weight == 0:
		#print(ip)
		ip_epsilon = 10000000000
	ip_epsilons[ip] = ip_epsilon
print("Graph of OVH")
total_epsilon_per_choice = 0
total_ip_weight = 0
graph_pairs = {}
num_weights = 0
for pair in ovh_data:
	ip = pair[0]
	weights = pair[1]
	for weight in weights:
		if ip_epsilons[ip] *weight != 0:
			graph_pairs[ip] = ip_epsilons[ip]
			#print(graph_pairs[ip])
			# Still need the particular probability that this as picks this guard
			total_ip_weight += weight
			total_epsilon_per_choice += (ip_epsilons[ip] *weight)
total_epsilon_per_choice = total_epsilon_per_choice/total_ip_weight
print(total_epsilon_per_choice)

## Graph of epsilon values versus Ip Addresses for Given AS
graph_ips = graph_pairs.keys()
graph_epsilons = []
graph_ips = sorted(graph_ips)
for key in graph_ips:
	graph_epsilons.append(graph_pairs[key])

graph_data = [go.Bar(x=graph_ips,y=graph_epsilons)]
py.plot(graph_data,filename='basic-bar.html')
'''
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
			as_to_ip_probability[key][ip][index] = weight/total_weight
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
