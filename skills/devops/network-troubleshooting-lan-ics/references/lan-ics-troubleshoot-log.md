# LAN‑ICS Troubleshooting Log (macOS side)

## Interface status
```
$ ifconfig en7
en7: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
    options=6464<VLAN_MTU,TSO4,TSO6,CHANNEL_IO,PARTIAL_CSUM,ZEROINVERT_CSUM>
    ether 98:fc:84:e0:4d:9c
    inet 192.168.137.2 netmask 0xffffff00 broadcast 192.168.137.255
    nd6 options=201<PERFORMNUD,DAD>
    media: autoselect (100baseTX <full-duplex>)
    status: active
```

## Routing before fix
```
$ netstat -rn | grep default
default            172.20.10.1        UGScg                 en0
```

## Ping to Windows host (always OK)
```
$ ping -c 3 192.168.137.1
PING 192.168.137.1 (192.168.137.1): 56 data bytes
64 bytes from 192.168.137.1: icmp_seq=0 ttl=128 time=1.802 ms
64 bytes from 192.168.137.1: icmp_seq=1 ttl=128 time=1.507 ms
64 bytes from 192.168.137.1: icmp_seq=2 ttl=128 time=1.666 ms
--- 192.168.137.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
```

## Change default gateway to Windows host
```
$ sudo route -n change default 192.168.137.1
change net default: gateway 192.168.137.1
```

## Routing after change
```
$ netstat -rn | grep default
default            192.168.137.1      UGSc                  en7
```

## Test external connectivity
```
$ ping -c 3 8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: icmp_seq=0 ttl=113 time=11.965 ms
64 bytes from 8.8.8.8: icmp_seq=1 ttl=113 time=11.943 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=113 time=12.308 ms
--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 11.943/12.072/12.308/0.167 ms
```

$ nslookup apple.com
Server:		fe80::904c:c5ff:fe50:2364%15
Address:	fe80::904c:c5ff:fe50:2364%15#53

Non-authoritative answer:
Name:	apple.com
Address: 17.253.144.10
```