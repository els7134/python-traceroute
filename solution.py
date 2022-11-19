from socket import *
import os
import sys
import struct
import time
import select
import binascii
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    myChecksum = 0
    # Make the header in a similar way to the ping exercise.
    myID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    # Append checksum to the header.
    data = struct.pack("d", time.time())

    myChecksum = checksum(header + data)
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHb", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
    destAddr = gethostbyname(hostname)
    # print('destAddr: ' + destAddr)
    # print('hostname: ' + hostname)
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            # destAddr = gethostbyname(hostname)

            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #print (tries)
            #print (mySocket)
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    #Fill in start
                    #append response to your dataframe including hop #, try #, and "Timeout" responses as required by the acceptance criteria
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': 'timeout', 'Hostname': 'timeout', 'Response Code': 'timeout'}, ignore_index=True)
                    print ('in whatready')
                    #print (df)
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                #print(str(addr[0]))
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    #Fill in start
                    #append response to your dataframe including hop #, try #, and "Timeout" responses as required by the acceptance criteria
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': 'timeout', 'Hostname': 'timeout', 'Response Code': 'timeout'}, ignore_index=True)
                    print('in timeleft <= 0')
                    #print (df)
                    #Fill in end
            except Exception as e:
                print (e) # uncomment to view exceptions
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                request_type, types, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
                # print("here in else")
                print(types)
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    hname = gethostbyaddr(addr[0])[0]
                    print(hname)
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    hname = 'hostname not returnable'
                    #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +
                    bytes])[0]
                    #Fill in start
                    #You should update your dataframe with the required column field responses here
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': str(addr[0]), 'Hostname': hname, 'Response Code': str(types)}, ignore_index=True)
                    print("in 11")
                    print(df)
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should update your dataframe with the required column field responses here
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': str(addr[0]), 'Hostname': hname, 'Response Code': str(types)}, ignore_index=True)
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should update your dataframe with the required column field responses here
                    print('in 0')
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': str(addr[0]), 'Hostname': hname, 'Response Code': str(types)}, ignore_index=True)
                    print(df)
                    #Fill in end
                else:
                    # Fill in start
                    #If there is an exception/error to your if statements, you should append that to your df here
                    df = df.append({'Hop Count': str(ttl), 'Try': str(tries), 'IP': str(destAddr[0]), 'Hostname': hostname, 'Response Code': str(types)}, ignore_index=True)
                    #Fill in end
                break
    print(df)
    return df

if __name__ == '__main__':
    get_route("google.co.il")