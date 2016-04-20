#!/bin/bash
INTERFACES="/etc/network/interfaces"
. /etc/lsb-release

change_if_name () {
    MAC=$1
    NAME=$2
    if grep $MAC /sys/class/net/*/address; then
        if [ "$DISTRIB_RELEASE" == "14.04" ]; then
            RULES="/etc/udev/rules.d/70-persistent-net.rules"
            touch $RULES
            interface=`awk -F\" '/'"$MAC"'/ { print $(NF-1) }' $RULES`
            sed -i 's/'"$interface"'/'"$NAME"'/' $RULES
        elif [ "$DISTRIB_RELEASE" == "16.04" ] || [ "$DISTRIB_RELEASE" == "15.10" ]; then
            RULES="/etc/udev/rules.d/10-rename-network.rules"
            touch $RULES
            echo 'SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="'"$MAC"'", NAME="'"$NAME"'"' >> $RULES
        fi
        echo >> $INTERFACES
        echo 'auto '"$NAME"'' >> $INTERFACES
        echo 'iface '"$NAME"' inet static' >> $INTERFACES
        echo '        address '"$3"'' >> $INTERFACES
        echo '        netmask '"$4"'' >> $INTERFACES
        echo '        network '"$5"'' >> $INTERFACES
        echo '        broadcast '"$6"'' >> $INTERFACES
        if ! [[ -z $7 ]]; then echo '        gateway '"$7"'' >> $INTERFACES; fi
        if ! [[ -z $8 ]]; then echo '        dns-nameservers '"$8"'' >> $INTERFACES; fi
        if ! [[ -z $9 ]]; then echo '        dns-search '"$9"'' >> $INTERFACES; fi
        # Prioritize eth10 nameservers over all other eth* interfaces
        if [ "$NAME" == "eth10" ]; then sed -i 's/eth\*/eth10\*\neth\*/' /etc/resolvconf/interface-order; fi
    fi
}

#              mac name address netmask network broadcast |{optional->} gateway dns-nameservers dns-search
# ppkvm003
change_if_name "98:be:94:59:e4:00" "eth10" "9.3.89.26" "255.255.255.0" "9.3.89.0" "9.3.89.255" "9.3.89.1" "9.3.1.200 9.0.128.50" "aus.stglabs.ibm.com"
change_if_name "98:be:94:59:e4:01" "eth11" "172.16.255.2" "255.255.255.0" "172.16.255.0" "172.16.255.255"
# ppkvm004
change_if_name "98:be:94:0d:f1:20" "eth10" "9.3.89.27" "255.255.255.0" "9.3.89.0" "9.3.89.255" "9.3.89.1" "9.3.1.200 9.0.128.50" "aus.stglabs.ibm.com"
# sm5
change_if_name "68:05:ca:39:8c:c0" "eth10" "9.3.89.114" "255.255.255.0" "9.3.89.0" "9.3.89.255" "9.3.89.1" "9.3.1.200 9.0.128.50" "aus.stglabs.ibm.com"
# sm6
change_if_name "68:05:ca:39:8c:94" "eth10" "9.3.89.115" "255.255.255.0" "9.3.89.0" "9.3.89.255" "9.3.89.1" "9.3.1.200 9.0.128.50" "aus.stglabs.ibm.com"
# sm7
change_if_name "68:05:ca:39:8c:c4" "eth10" "9.3.89.116" "255.255.255.0" "9.3.89.0" "9.3.89.255" "9.3.89.1" "9.3.1.200 9.0.128.50" "aus.stglabs.ibm.com"

