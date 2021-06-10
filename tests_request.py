import unittest
import requests


def parametrize(*parameters):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for params in parameters:
                func(*args, *params)
        return wrapper
    return decorator


def _send_request(begin_port, end_port):
    return requests.get(f'http://localhost:9090/scan/127.0.0.1/'
                        f'{begin_port}/{end_port}')


class PortScannerAPITestCase(unittest.TestCase):
    @parametrize(
        [10, 20],
        [68, 90],
        [100, 150]
    )
    def test_response_format(self, begin_port, end_port):
        response_json = _send_request(begin_port, end_port).json()

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
        [68, 90],
        [100, 150]
    )
    def test_response_after_time(self, begin_port, end_port):
        response_json_1 = _send_request(begin_port, end_port).json()
        response_json_2 = _send_request(begin_port, end_port).json()

        self.assertEqual(response_json_1, response_json_2)

    @parametrize(
        ['sdfg', 20],
        [90, 68])
    def test_response_for_incorrect_request(self, begin_port, end_port):
        response = _send_request(begin_port, end_port)

        self.assertEqual(400, response.status_code)


if __name__ == '__main__':
    unittest.main()
