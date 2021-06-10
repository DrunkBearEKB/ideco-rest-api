import json
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from api import check_ip_validity, check_ports_validity, scan_ports


def parametrize(*parameters):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for params in parameters:
                func(*args, *params)
        return wrapper
    return decorator


async def get_response_json(response):
    response_json = await response.__dict__['content'].read()
    return json.loads(response_json.decode())


class MyTestAioHTTPTest(AioHTTPTestCase):

    async def get_application(self):
        async def handle_request(request: web.Request) -> web.Response:
            try:
                ip = request.match_info.get('ip')
                begin_port = int(request.match_info.get('begin_port'))
                end_port = int(request.match_info.get('end_port'))

                if not check_ip_validity(ip):
                    return web.HTTPBadRequest(
                        text='400: Bad Request\n'
                             'Invalid ip address!'
                    )
                if not check_ports_validity(begin_port, end_port):
                    return web.HTTPBadRequest(
                        text='400: Bad RequestInvalid ports!'
                    )

            except ValueError:
                return web.HTTPBadRequest()

            scan_results = scan_ports(ip, begin_port, end_port)

            return web.Response(
                text=json.dumps(scan_results)
            )

        app = web.Application()
        app.router.add_routes(
            [web.get('/scan/{ip}/{begin_port}/{end_port}', handle_request)
             ])

        return app

    @parametrize(
        [10, 20],
        [68, 90]
    )
    @unittest_run_loop
    async def test_response_format(self, begin_port, end_port):
        response = await self.client.request(
            'GET', f'/scan/127.0.0.1/{begin_port}/{end_port}')
        response_json = await get_response_json(response)

        self.assertIsInstance(response_json, list)
        self.assertEqual(end_port - begin_port + 1, len(response_json))

        for res in response_json:
            self.assertIsInstance(res, dict)
            self.assertIn('port', res)
            self.assertIsInstance(res['port'], int)
            self.assertIn('state', res)
            self.assertIsInstance(res['state'], str)

    @parametrize(
        [10, 20],
        [68, 90]
    )
    @unittest_run_loop
    async def test_response_after_time(self, begin_port, end_port):
        response_1 = await self.client.request(
            'GET', f'/scan/127.0.0.1/{begin_port}/{end_port}')
        response_json_1 = await get_response_json(response_1)

        response_2 = await self.client.request(
            'GET', f'/scan/127.0.0.1/{begin_port}/{end_port}')
        response_json_2 = await get_response_json(response_2)

        self.assertEqual(response_json_1, response_json_2)

    @parametrize(
        ['sdfg', 20],
        [90, 68])
    @unittest_run_loop
    async def test_response_for_incorrect_request(self, begin_port, end_port):
        response = await self.client.request(
            'GET', f'/scan/127.0.0.1/{begin_port}/{end_port}')

        self.assertEqual(400, response.status)