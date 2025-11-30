from twisted.internet import reactor
from twisted.web import server, resource

class HelloResource(resource.Resource):
  isLeaf = True
  def render(self, request):
    request.setHeader(b'content-type', b'text/html')
    return b'hello twisted!'


def main():
  site = server.Site(HelloResource())
  reactor.listenTCP(8080, site)
  reactor.run()

if __name__ == '__main__':
  main()
