import sys, getopt
from subprocess import Popen, PIPE
import shlex

from dpkt.ip import IP
import dpkt, socket

from statistics import mean_confidence_interval

TARGET_IPV4 = ("127.1.1.1", 0)

# To send signal of resetting flows
sock4 = socket.socket(socket.AF_INET, socket.SOCK_RAW, dpkt.ip.IP_PROTO_ICMP)


class Route:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __eq__(self, other):
        return self.source == other.source and self.destination == other.destination


def parseRoutes(topologyFile):
    routes = []
    with open(topologyFile) as topology:
        for route in topology:
            addresses = route.split(" ")
            if len(addresses) == 2:
                # Remove the backslash n from the destination
                addresses[1] = addresses[1].replace("\n", "")
                routes.append(Route(addresses[0], addresses[1]))
    return routes


def compareRoutes(parsedRoutes, foundRoutes):
    for route in parsedRoutes:
        if route not in foundRoutes:
            return False
    if len(parsedRoutes) != len(foundRoutes):
        return False
    return True


def startParisTraceroute(parisTracerouteCmd):
    args = shlex.split(parisTracerouteCmd)
    p = Popen(args, stdout=PIPE, bufsize=1)
    startedLattice = False
    foundRoutes = []
    with p.stdout:
        for line in iter(p.stdout.readline, b''):
            if startedLattice:
                tokens = line.split("-> [")
                # If there is only one token, means that we have reached our destination
                if len(tokens) == 1:
                    continue
                # If it is None, deduce it as source localhost
                if tokens[0] == "None ":
                    tokens[0] = "127.0.0.1"
                # Remove space from source too
                source = tokens[0].replace(" ", "")
                # Check if there are more than 1 destination
                destinations = tokens[1].split(", ")
                # Remove the ] from the last destination address
                destinations[len(destinations) - 1] = destinations[len(destinations) - 1].replace("]", "")
                for destination in destinations:
                    destination = destination.replace(" ", "")
                    destination = destination.replace("\n", "")
                    foundRoutes.append(Route(source, destination))

            if line.startswith("Lattice:"):
                startedLattice = True
        return foundRoutes
    p.wait()


def main(argv):
    topologyFile = ''
    outputfile = ''
    parisTracerouteCmd = ""
    confidenceIntervalPercent = 0.95
    runNumber = 1000
    try:
        opts, args = getopt.getopt(argv, "ht:p:o:n:c:", ["topology=", "ofile=", "paris-traceroute="])
    except getopt.GetoptError:
        print 'main.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-t", "--topology"):
            topologyFile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--paris-traceroute"):
            parisTracerouteCmd = arg
        elif opt in ("-n", "--run-number"):
            runNumber = int(arg)
        elif opt in ("-c", "--confidence-interval"):
            confidenceIntervalPercent = float(arg)

    print 'Topology file is "', topologyFile
    print "Will execute this paris-traceroute command: ", parisTracerouteCmd
    print 'Output file is "', outputfile
    parsedRoutes = parseRoutes(topologyFile)

    ipPacket = IP(
        src="127.0.0.1",
        dst="127.1.1.1",
        p=dpkt.ip.IP_PROTO_UDP,
        ttl=128
    )
    sampleNumber = 50
    samples = []
    for k in range(0, sampleNumber):
        failure = 0
        success = 0
        if k % 10 == 0:
            print "Iteration number : ", k
        for x in range(0, runNumber):
            foundRoutes = startParisTraceroute(parisTracerouteCmd)
            sock4.sendto(str(ipPacket), TARGET_IPV4)
            if compareRoutes(parsedRoutes, foundRoutes):
                success += 1
            else:
                failure += 1
        samples.append(failure / float((failure + success)))

    print "sample number: ", sampleNumber
    print "run number by sample : ", runNumber
    m, interval = mean_confidence_interval(samples,confidenceIntervalPercent)

    print "mean estimated: ", m
    print "interval :", interval
    confidenceInterval = "interval of confidence with "+str(confidenceIntervalPercent)+": " + "[" + str(m - interval) + ", " + str(m + interval) + "]"
    print confidenceInterval
    if outputfile == "":
        outputfile = topologyFile + "_output"

    with open(outputfile, "w") as output:
        output.write("sample number: " + str(sampleNumber) + "\n")
        output.write("run number by sample: " + str(runNumber) + "\n")
        output.write("mean estimated of failure: " + str(m) + "\n")
        output.write("interval :" +  str(interval) + "\n")
        output.write("confidenceInterval: " + confidenceInterval + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
