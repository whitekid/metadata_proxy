# Overview
in quantum, with with allow_overlapping_ip, nova-api can't find instance's metadata.
that's because instance ip address are duplicated to other tenant's. to response metadata request, metadata api server requires tenant_id.

To acomplish this idea.

In tenant's l3 routing namespace
- add 169.254.169.254/32 ip in lo device
- make http proxy in tenant's l3 router namespace, with listening 169.254.169.254
- remove DNAT iptable settings to point our proxy
- in proxy, it receive instance's metada request and pass to real metadata api server. with addng X-Forwarded-For, and X-OS-TENANT-ID
  X-Forwarded-For: real instance's ip address
  X-OS-TENANT-ID: namespace's owner

When real metadata api server receive the request
- server can find instance's ip address with X-Forwarded-For http header
- and tenant id with X-OS-TENANT-ID
- and response to proxy

# How to use
## nova-api
1. patch nova-api to 
   https://github.com/whitekid/nova/commit/de9b371a4667dd66f510093a1e207bc7f9e02c6d

2. in nova-api server set use_forwarded_for=true

3. restart nova-api

## l3-agent
1. install twisted-web
  $ apt-get install python-twisted-web

2. in tenant router namespace add metadata ip to lo device
   $ ip netns exec qrouter-XXXX ip addr add 169.254.169.254/32 device lo

3. remove DNAT rule for metadata-ip
   $ ip netns exec qrouter-XXXX
   $ iptables -t nat -L quantum-l3-agent-PREROUTING | grep 169.254.169.254 > /dev/null && iptables -t nat -D quantum-l3-agent-PREROUTING 1
   $ exit

4. simply run metadata-proxy in tenant's router namespace
  $ ip netns exec qrouter-XXX python metadata-proxy [real-metadata-api-server-ip] [tenant-id]
  eg) ip netns exec qrouter-XXX python proxy.py 10.100.1.6 f4fe7590238d444a8e4e52c6249581b3


# TODO
1. remove l3 agent's DNAT rule for metadata
