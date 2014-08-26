#! /bin/bash

# usage:
# config_network --ip[=]<value> --mask[=]<value> --gateway[=]<value> --dns[=]<value>

#set -vx
# A string with command options
options=$@

# An array with all the arguments
arguments=($options)

# Loop index
index=0

declare -A longoptspec
longoptspec=( [ip]=1 [mask]=1 [gateway]=1 [dns]=1 ) #use associative array to declare how many arguments a long option expects, in this case we declare that loglevel expects/has one argument, long options that aren't listed i n this way will have zero arguments by default
optspec=":h-:"
while getopts "$optspec" opt; do
while true; do
    case "${opt}" in
        -) #OPTARG is name-of-long-option or name-of-long-option=value
            if [[ "${OPTARG}" =~ .*=.* ]] #with this --key=value format only one argument is possible
            then
                opt=${OPTARG/=*/}
                OPTARG=${OPTARG#*=}
                ((OPTIND--))    
            else #with this --key value1 value2 format multiple arguments are possible
                opt="$OPTARG"
                OPTARG=(${@:OPTIND:$((longoptspec[$opt]))})
            fi
            ((OPTIND+=longoptspec[$opt]))
            continue #now that opt/OPTARG are set we can process them as if getopts would've given us long options
            ;;
        ip)
          IP=$OPTARG
            ;;
        mask)
          MASK=$OPTARG
            ;;
        gateway)
          GATEWAY=$OPTARG
            ;;
        dns)
          DNS=$OPTARG
            ;;
        h|help)
            echo "usage: $0 --ip[=]<value> --mask[=]<value> --gateway[=]<value> --dns[=]<value>" >&2
            exit 2
            ;;
    esac
break; done
done

ifconfig  eth0 $IP netmask $MASK
ifconfig lo 127.0.0.1
route add default gw $GATEWAY
echo "nameserver $DNS" >> /etc/resolv.conf