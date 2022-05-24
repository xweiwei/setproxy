#!/system/bin/sh

HOST=$1
APP_UID=$2

iptables -t nat -A OUTPUT -p tcp -d ${HOST} -j RETURN

iptables -t nat -m owner --uid-owner ${APP_UID} -A OUTPUT -p tcp --dport 80 -j REDIRECT --to 8123
iptables -t nat -m owner --uid-owner ${APP_UID} -A OUTPUT -p tcp --dport 443 -j REDIRECT --to 8124
iptables -t nat -m owner --uid-owner ${APP_UID} -A OUTPUT -p tcp --dport 5228 -j REDIRECT --to 8124

