# coding=utf8

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from qhttp.core.web import HttpSever


def verify(function):
    """
    Decorator. Verifies if the transaction is from the widgets. Returns 401 response otherwise.
    :param function:
    :return: None
    """

    def wrapped(transaction):
        reference = "JAM_{}/{}".format(None, None)
        agent = transaction.request.headers.get("User-Agent", "")

        if reference in agent:
            function(transaction)
            return

        else:
            transaction.send_error(status_code=401)
            return

    return wrapped


class BaseView(QWebEngineView):
    def __init__(self, port, static_path, parent=None):
        QWebEngineView.__init__(self, parent)

        self.httpServer = HttpSever()
        self.httpServer.port = port
        self.httpServer.static_path = static_path
        self.httpServer.listen()

        self.load(QUrl("http://127.0.0.1:{}".format(self.httpServer.port)))
