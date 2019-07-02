# coding=utf8

import os

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from qhttp.core.web import HttpSever

DEFAULT_PORT = 8888
DEBUG = True


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

    if DEBUG:
        return function

    return wrapped


class BaseView(QWebEngineView):
    def __init__(self, parent=None):
        QWebEngineView.__init__(self, parent)

        self.httpServer = HttpSever()
        self.httpServer.port = DEFAULT_PORT
        self.httpServer.static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
        self.httpServer.listen()

        self.load(QUrl("http://127.0.0.1:{}".format(DEFAULT_PORT)))


class WebView(BaseView):
    def __init__(self, parent=None):
        BaseView.__init__(self, parent)

        @verify
        def get(transaction):
            transaction.render("index.html")

            # process_transaction(transaction)

        @verify
        def post(transaction):
            centralWidget = self.parent()
            mainWindow = centralWidget.parent()

            transaction.view = mainWindow  # let op!
            # process_transaction(transaction)

        self.httpServer.doGet = get
        self.httpServer.doPost = post

        print()


if "__main__" == __name__:
    import sys
    from PyQt5.QtWidgets import QApplication

    application = QApplication(sys.argv)

    graph = WebView()
    graph.show()

    sys.exit(application.exec_())