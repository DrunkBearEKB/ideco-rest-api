import os
import sys
from aiohttp import web
import json
import socket
import configparser
import threading
import multiprocessing
import logging.handlers
import datetime

FILE_CONFIG = f'{os.path.dirname(__file__)}/' + 'config.ini'
DEFAULT_CONFIG = \
    '''[Settings]
port = 9090
timeout = 1
amount_threads_for_user = 5
'''


def parse_config() -> configparser.ConfigParser:
    """
    Parses the configuration file from the FILE_CONFIG variable
    :return: parsed config
    :rtype: configparser.ConfigParser
    """
    _config = configparser.ConfigParser()

    if not os.path.exists(FILE_CONFIG):
        create_default_config()
    _config.read(FILE_CONFIG)

    return _config


def create_default_config() -> None:
    """
    Creates a default configuration file with data from the
    DEFAULT_CONFIG variable
    :rtype: None
    """
    with open(FILE_CONFIG, mode='w') as file:
        file.write(DEFAULT_CONFIG)


def check_ip_validity(ip: str) -> bool:
    """
    Checks the validity of the ip address
    :param ip: host ip address to check for validity
    :type ip: str
    :return: validity of the ip address
    :rtype: bool
    """
    return all(map(lambda num: 0 <= int(num) <= 255, ip.split('.')))


def check_ports_validity(begin_port: int, end_port: int = None) -> bool:
    """
    Checks the validity of the port/ports
    :param begin_port: begin of the port check interval
    :type begin_port: int
    :param end_port: end of the port check interval [None is default]
    :type end_port: int
    :return: validity of port/ports
    :rtype: bool
    """
    if end_port is not None:
        return 0 <= begin_port <= end_port <= 65535
    return 0 <= begin_port <= 65535


def scan_ports(ip: str, begin_port: int, end_port: int) -> list[dict]:
    """
    Scans ports from begin_port to end_port for this ip address
    :param ip: host ip address to check
    :type ip: str
    :param begin_port: begin of the port check interval
    :type begin_port: int
    :param end_port: end of the port check interval
    :type end_port: int
    :return: results of scanning ports of ip address
    :rtype: list[dict]
    """
    scan_results = multiprocessing.Queue()
    threads = []

    for i in range((end_port + 1 - begin_port) // AMOUNT_THREADS_FOR_USER + 1):
        _begin = begin_port + i * AMOUNT_THREADS_FOR_USER
        _end = min(_begin + AMOUNT_THREADS_FOR_USER, end_port + 1)

        for port in range(_begin, _end):
            thread = threading.Thread(
                target=__scan_port,
                args=(ip, port, scan_results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    results = []
    while not scan_results.empty():
        results.append(scan_results.get())
    results.sort(key=lambda res: res['port'])

    return results


def __scan_port(ip: str, port: int, out: multiprocessing.Queue) -> None:
    """
    Scans port for this ip address
    :param ip: host ip address to check
    :type ip: str
    :param port: port to check
    :type port: int
    :param out: the queue that the result of the function is added to
    :type out: multiprocessing.Queue
    :return: result of scanning port of ip address
    :rtype: list[dict]
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_tcp:
        socket_tcp.settimeout(TIMEOUT)
        connected = socket_tcp.connect_ex((ip, port))
        out.put({
            'port': port,
            'state': 'open' if connected == 0 else 'close'
        })


async def handle_request(request: web.Request) -> web.Response:
    """
    Handles incoming request
    :param request: request sent by the user
    :type request: web.Request
    :return: Response for request
    :rtype: web.Response
    """
    logger.info(f'Request from [{request.remote}] was accepted.')

    try:
        ip = request.match_info.get('ip')
        begin_port = int(request.match_info.get('begin_port'))
        end_port = int(request.match_info.get('end_port'))

        if not check_ip_validity(ip):
            logger.info('Invalid ip address!')
            return web.HTTPBadRequest(
                text='400: Bad Request\n'
                     'Invalid ip address!'
            )
        if not check_ports_validity(begin_port, end_port):
            logger.info('Invalid ports!')
            return web.HTTPBadRequest(
                text='400: Bad RequestInvalid ports!'
            )

    except ValueError:
        logger.info('Can not parse request!')
        return web.HTTPBadRequest()

    scan_results = scan_ports(ip, begin_port, end_port)

    logger.info(f'Sent response for {request.remote}.')
    return web.Response(
        text=json.dumps(scan_results)
    )

logger = logging.getLogger('api')
logger.setLevel(logging.INFO)

handler = logging.handlers.SysLogHandler(
    address=('localhost', 8080)
)
# handler = logging.FileHandler(
#     datetime.datetime.now().strftime('logs/logfile_%Y-%m-%d_%H-%M.log')
# )
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt='[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler.setFormatter(formatter)
logger.addHandler(handler)

# creating global variables (PORT, AMOUNT_THREADS_FOR_USER and TIMEOUT)
# from the config file and checks their validity
try:
    config = parse_config()

    PORT = int(config['Settings']['port'])
    AMOUNT_THREADS_FOR_USER = int(
        config['Settings']['amount_threads_for_user'])
    TIMEOUT = float(config['Settings']['timeout'])

    if not check_ports_validity(PORT) or AMOUNT_THREADS_FOR_USER < 1 or \
            TIMEOUT < 0:
        logger.error('Invalid parameters in the configuration file!')
        print('Invalid parameters in the configuration file!')
        sys.exit()

except (ValueError, KeyError):
    logger.error('Can not parse config file!')
    print('Can not parse config file!')
    sys.exit()


def main() -> None:
    """
    The main function of the program
    :rtype: None
    """
    # defines the main app and routes for this app
    app = web.Application()
    app.router.add_routes(
        [web.get('/scan/{ip}/{begin_port}/{end_port}', handle_request)
         ])

    # checks whether the program can be run on PORT
    socket_server_temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server_temp.bind(('', PORT))
    try:
        socket_server_temp.listen()
    except OSError:
        socket_server_temp.close()
        logger.error(f'Sever can not be started on port equal to "{PORT}"!')
        print(f'Sever can not be started on port equal to "{PORT}"!')
        sys.exit()
    del socket_server_temp

    logger.info('Sever started!')
    web.run_app(app, port=PORT)


if __name__ == '__main__':
    main()
