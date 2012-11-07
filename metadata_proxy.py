#! -*- coding: utf-8 -*-
import sys
from twisted.web import http, proxy
from twisted.internet import reactor
from twisted.python import log

log.startLogging(sys.stdout)

metadata_ip = None
tenant_id = None

class MetaProxyRequest(proxy.ProxyRequest):
    def process(self):
        # modify destination to metadata ip
        self.uri = 'http://%s:8775' % metadata_ip + self.uri

        # and add x-forwarded-for header
        peer = self.transport.getPeer().host
        self.requestHeaders.addRawHeader('X-Forwarded-For', peer)
        self.requestHeaders.addRawHeader('X-OS-TENANT-ID', tenant_id)

        return proxy.ProxyRequest.process(self)

class MetaProxy(proxy.Proxy):
    requestFactory = MetaProxyRequest

class ProxyFactory(http.HTTPFactory):
    protocol = MetaProxy

def main():
    if len(sys.argv) != 3:
        print 'Usage: proxy.py metadata_ip tenant_id'
        return

    global metadata_ip, tenant_id
    metadata_ip= sys.argv[1]
    tenant_id = sys.argv[2]

    reactor.listenTCP(80, ProxyFactory(), interface='169.254.169.254')
    reactor.run()

main()

# vim: ai nu ts=4 sw=4 et
