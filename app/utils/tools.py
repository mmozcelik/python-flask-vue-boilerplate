import logging
from app.utils.frequests import Frequests


def check_domain_mx(domain_name):
    response = None
    try:
        response = Frequests.get('http://mxapi.myapp.com', params={
            'domain': domain_name,
            'token': '12432'
        }, timeout=3)

        return response.json().get('success')
    except:
        pass

    return True


def port_check(host, port):
    import socket
    from contextlib import closing

    logging.info("port_check(1): Checking port on host: {0}:{1}".format(host, port))
    result = False
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)
        if sock.connect_ex((host, port)) == 0:
            result = True

        logging.info("port_check(2): Checked port on host: {0}:{1} with result {2}".format(host, port, result))

    logging.info("port_check(3): Returning result on host: {0}:{1} with result {2}".format(host, port, result))
    return result
