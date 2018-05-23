# TestParisTraceroute

This tool has been developped in order to statistically test the MultiPathsDetection algorithm implemented in [Paris Traceroute](https://). 

## Getting Started
First you need to create your topology:

At the moment, a topology is just a file describing nodes and edges. 

An example is given below : 
```
127.0.0.1 10.0.0.1

10.0.0.1 10.1.2.3
10.0.0.1 2.3.3.3

10.1.2.3 127.1.1.6
2.3.3.3 127.1.1.6
```
The file is composed of lines that are composed of pairs of addresses.

Note that the localhost address (127.0.0.1) is mandatory at first line.

It saves this topology so it can be tested that this expected topology is the one you have or have not discovered via Paris Traceroute.

Then it launches a certain number of samples of Paris Traceroute that you specify.
It then gives you the measured failure rate and the confidence interval at a certain value that you can specify.
### Prerequisites
You will need the following libraries of python:

```
dpkt
scipy
numpy
shlex
```
You also need paris-traceroute to be installed.


### Installing

You don't need any tools to install TestParisTraceroute 

###Usage
In folder where paris-traceroute executable is:
```
python /path/to/TestParisTraceroute/main.py -t <topology_file>  -p <paris-traceroute_command>
```
### Break down into end to end tests
You can test this tool in combination with [fakerouteC++](https://)

In a terminal, tap:
```
./fakerouteC__ resources/2-pathsLoadBalancer 127.1.1.6
```
In another terminal in paris-traceroute folder:
```
python /path/to/TestParisTraceroute/main.py -t resources/2-pathsLoadBalancer  -p "paris-traceroute -amda -B95,1,128 127.1.1.6"
```
See paris-traceroute for options meanings.

You should see on standard output:
```
Topology file is " resources/2-pathsLoadBalancer
Will execute this paris-traceroute command:  paris-traceroute -amda -B95,1,128 127.1.1.6
Output file is " 
Iteration number :  0
Iteration number :  10
Iteration number :  20
Iteration number :  30
Iteration number :  40
sample number:  50
run number by sample :  1000
mean estimated:  0.03206
interval : 0.00156437713451
interval of confidence with 0.95: [0.0304956228655, 0.0336243771345]
```

The iteration number tells you the state of your experiment.
By default, it writes the results in the topologyFile_output in the working directory.