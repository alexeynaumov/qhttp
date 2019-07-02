# coding=utf8

import os
from qhttp.gui.widgets.webview.WebView import BaseView

DEFAULT_PORT = 8888
DEFAULT_STATIC_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static/"
DEBUG = True


class WebView(BaseView):
    def __init__(self, port=DEFAULT_PORT, static_path=DEFAULT_STATIC_PATH, parent=None):
        BaseView.__init__(self, port=port, static_path=static_path, parent=parent)

        def get(transaction):
            transaction.render("./static/index.html")

            # process_transaction(transaction)

        def post(transaction):
            centralWidget = self.parent()
            mainWindow = centralWidget.parent()

            transaction.view = mainWindow  # let op!
            # process_transaction(transaction)

        self.httpServer.doGet = get
        self.httpServer.doPost = post


if "__main__" == __name__:
    import sys
    from PyQt5.QtWidgets import QApplication

    application = QApplication(sys.argv)

    graph = WebView()
    graph.httpServer.port = DEFAULT_PORT
    graph.httpServer.static_path = DEFAULT_STATIC_PATH
    graph.show()

    sys.exit(application.exec_())