import json

import aiohttp
from aiohttp import web as aw

from . import util as u


class NodesHandler(aw.View):

    async def get(self):
        pattern = self.request.query.get('pattern', None)
        if not pattern:
            return aw.Response(status=400)

        controller = self.request.app['controller']
        try:
            nodes = await controller.search(pattern)
        except u.InvalidPatternError:
            return aw.Response(status=400)
        except u.SearchFailedError:
            return aw.Response(status=503)

        nodes = [{'id': k, 'name': v} for k, v in nodes.items()]
        nodes = sorted(nodes, key=lambda _: _['name'])
        nodes = json.dumps(nodes)
        nodes = nodes + '\n'
        return aw.Response(text=nodes)

    async def delete(self):
        id_ = self.request.match_info['id']
        if id_ is None:
            return aw.Response(status=400)

        controller = self.request.app['controller']
        await controller.trash(id_)
        return aw.Response()


class CacheHandler(aw.View):

    async def get(self):
        nodes = self.request.query.getall('nodes[]', None)
        if not nodes:
            return aw.Response(status=400)

        controller = self.request.app['controller']
        result = await controller.compare(nodes)
        result = json.dumps(result)
        result = result + '\n'
        return aw.Response(text=result)

    async def post(self):
        controller = self.request.app['controller']

        kwargs = await self.request.post()
        paths = kwargs.getall('paths[]', None)
        if not paths:
            controller.sync_db()
            return aw.Response()

        controller.download_low(paths)
        return aw.Response()

    async def put(self):
        id_ = self.request.match_info['id']
        if id_ is None:
            return aw.Response(status=400)

        controller = self.request.app['controller']
        controller.download_high(id_)
        return aw.Response()


class LogHandler(aw.View):

    async def get(self):
        logs = self.request.app['logs']
        # iDontCare
        result = json.dumps(logs.get_recent())
        return aw.Response(text=result)


class LogSocketHandler(object):

    def __init__(self, app):
        self._counter = 0
        self._app = app
        self._app['ws'] = set()

    async def handle(self, request):
        ws = aw.WebSocketResponse()
        await ws.prepare(request)
        request.app['ws'].add(ws)

        id_ = self._counter
        self._counter += 1

        logs = request.app['logs']
        logs.add(id_, ws)

        try:
            async for message in ws:
                pass
        finally:
            logs.remove(id_)
            request.app['ws'].discard(ws)

        return ws

    async def close(self):
        wss = set(self._app['ws'])
        for ws in wss:
            await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY)
