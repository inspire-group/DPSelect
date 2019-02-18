# DPSelect: A Differential Privacy Based Guard Relay Selection Algorithm

This repository contains the DPSelect code for analyzing both the Counter-RAPTOR and DPSelect entry guard relay selection algorithm.
To Run this Code:
 1.  Download Updated Tor Consensus from https://collector.torproject.org/archive/relay-descriptors/consensuses/ for the month that you  
 wish to analyze.
 2.  Download Updated Network Topology from http://data.caida.org/datasets/as-relationships/serial-2/
 3.  Extract Guard Ips and Bandwidths using ```get_guards.py``` after changing the file name in script to point to the consensus that you 
 are running
 4.  Extract Guard Ips and Bandwidths using get_guards_tille.py
 5.  Run ``` usr/local/bin/netcat whois.cymru.com 43 < guard_ips.txt | sort -n > list ``` to get a list of ASes corresponding to the 
 guards 
 6. Run ``` get_as.py ``` to get a list of the gurard ASes.
 7. Run ```counter_raptor_resilience.py ``` with the appropriate network topology and AS list. 
 8. Run  ``` get_tille_resilience.py ``` to get a .json of the tille resiliences.
 9. Run ``` optimization.py``` to run a monte-carlo simulation to determine the quality function to be used in DPSelect.
 10. Run a corresponding attack file to analyze a given entropy type.
