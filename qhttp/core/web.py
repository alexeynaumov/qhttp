# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Alexey Naumov <rocketbuzzz@gmail.com>
#
# This file is part of qhttp.
#
# qhttp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import asyncio

import tornado.web
import tornado.gen
import tornado.ioloop
import tornado.platform.asyncio

from PyQt5.QtCore import QCoreApplication, QThread, QEvent, QObject
from PyQt5.QtWidgets import QApplication

CODE_GET = QEvent.User + 128
CODE_POST = QEvent.User + 129
CODE_PUT = QEvent.User + 130
CODE_PATCH = QEvent.User + 131
CODE_DELETE = QEvent.User + 132
CODE_HEAD = QEvent.User + 133
CODE_OPTIONS = QEvent.User + 134


def make_event(code):
    code = QEvent.Type(code)

    class Event(QEvent):
        def __init__(self, request):
            QEvent.__init__(self,  code)
            self.transaction = request  # request becomes transaction attribute of the event

    return Event


GetEvent = make_event(CODE_GET)
HeadEvent = make_event(CODE_HEAD)
PostEvent = make_event(CODE_POST)
PutEvent = make_event(CODE_PUT)
DeleteEvent = make_event(CODE_DELETE)
OptionsEvent = make_event(CODE_OPTIONS)
PatchEvent = make_event(CODE_PATCH)


class HttpSever(QThread):
    """
    Simple http server.

    Usage:
    import sys
    from PyQt5.QtCore import QCoreApplication

    application = QApplication(sys.argv)

    def onGet(transaction):
        transaction.write("Get")
        transaction.finish()

    server = HttpSever()
    server.port = 8888
    server.doGet = onGet
    server.listen()

    sys.exit(application.exec_())
    """

    def __init__(self, port=80, static_path=None, parent=None):
        QThread.__init__(self, parent)

        self.port = port
        self.static_path = static_path or os.path.dirname(__file__)

        self.__on_get = None
        self.__on_head = None
        self.__on_post = None
        self.__on_put = None
        self.__on_delete = None
        self.__on_options = None
        self.__on_patch = None

    def __doGet(self, callback):
        self.__on_get = callback

    def __doHead(self, callback):
        self.__on_head = callback

    def __doPost(self, callback):
        self.__on_post = callback

    def __doPut(self, callback):
        self.__on_put = callback

    def __doDelete(self, callback):
        self.__on_delete = callback

    def __doOptions(self, callback):
        self.__on_options = callback

    def __doPatch(self, callback):
        self.__on_patch = callback

    def listen(self, port=None):
        if port:
            self.port = port

        self.start()

    def customEvent(self, event):
        if CODE_GET == event.type():
            if self.__on_get:
                self.__on_get(event.transaction)
                return

        if CODE_HEAD == event.type():
            if self.__on_head:
                self.__on_head(event.transaction)
                return

        if CODE_POST == event.type():
            if self.__on_post:
                self.__on_post(event.transaction)
                return

        if CODE_PUT == event.type():
            if self.__on_put:
                self.__on_put(event.transaction)
                return

        if CODE_DELETE == event.type():
            if self.__on_delete:
                self.__on_delete(event.transaction)
                return

        if CODE_OPTIONS == event.type():
            if self.__on_options:
                self.__on_options(event.transaction)
                return

        if CODE_PATCH == event.type():
            if self.__on_patch:
                self.__on_patch(event.transaction)
                return

    def run(self):

        class MainHandler(tornado.web.RequestHandler):

            @tornado.gen.coroutine
            def get(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, GetEvent(request))

            @tornado.gen.coroutine
            def head(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, HeadEvent(request))

            @tornado.gen.coroutine
            def post(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, PostEvent(request))

            @tornado.gen.coroutine
            def put(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, PutEvent(request))

            @tornado.gen.coroutine
            def delete(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, DeleteEvent(request))

            @tornado.gen.coroutine
            def options(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, OptionsEvent(request))

            @tornado.gen.coroutine
            def patch(request, *args, **kwargs):
                QCoreApplication.sendEvent(self, PatchEvent(request))

        def make_application():
            return tornado.web.Application([
                (r"/", MainHandler),
                (r"/(.*)", tornado.web.StaticFileHandler, dict(path=self.static_path))
            ])

        asyncio.set_event_loop_policy(tornado.platform.asyncio.AnyThreadEventLoopPolicy())

        application = make_application()
        application.listen(self.port)

        tornado.ioloop.IOLoop.current().start()

    doGet = property(fset=__doGet)
    doHead = property(fset=__doHead)
    doPost = property(fset=__doPost)
    doPut = property(fset=__doPut)
    doDelete = property(fset=__doDelete)
    doOptions = property(fset=__doOptions)
    doPatch = property(fset=__doPatch)


if "__main__" == __name__:
    import sys

    application = QApplication(sys.argv)

    def onGet(transaction):
        transaction.write("Get")
        transaction.finish()

    def onHead(transaction):
        transaction.write("Head")
        transaction.finish()

    def onPost(transaction):
        transaction.write("Post")
        transaction.finish()

    def onPut(transaction):
        transaction.write("Put")
        transaction.finish()

    def onDelete(transaction):
        transaction.write("Delete")
        transaction.finish()

    def onOptions(transaction):
        transaction.write("Options")
        transaction.finish()


    def onPatch(transaction):
        transaction.write("Patch")
        transaction.finish()

    server = HttpSever()
    server.port = 8888

    server.doGet = onGet
    server.doHead = onHead
    server.doPost = onPost
    server.doPut = onPut
    server.doDelete = onDelete
    server.doOptions = onOptions
    server.doPatch = onPatch

    server.listen()

    sys.exit(application.exec_())
