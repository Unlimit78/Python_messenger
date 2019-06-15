from twisted.internet import stdio, reactor
from twisted.internet.protocol import ClientFactory, Protocol


class DataWrapper(Protocol):
    output = None

    def dataReceived(self, data: bytes):
        """
        Вывод через канал клиента
        :param data:
        :return:
        """
        if data.decode() == 'exit\n':
            reactor.callFromThread(reactor.stop)

        if self.output:
            self.output.write(data)


class UserProtocol(DataWrapper):
    def wrap_input(self):
        """
        Передача управления ввода
        :return:
        """
        input_forwarder = DataWrapper()
        input_forwarder.output = self.transport

        stdio_wrapper = stdio.StandardIO(input_forwarder)
        self.output = stdio_wrapper

    def connectionMade(self):
        """
        Обработчик успешного соединения
        :return:
        """
        print("Connected [OK]")
        self.transport.write(f"login:{self.factory.login}".encode())
        self.wrap_input()


class UserFactory(ClientFactory):
    protocol = UserProtocol
    login: str

    def __init__(self, user_login: str):
        """
        Инициализация клиента
        :param user_login:
        """
        self.login = user_login

    def startedConnecting(self, connector):
        """
        Установка соединения
        :param connector:
        :return:
        """
        print("Connecting to the server...")

    def clientConnectionLost(self, connector, reason):
        """
        Обработчик отключения сервера
        :param connector:
        :param reason:
        :return:
        """
        print("Disconnected")
        reactor.callFromThread(reactor.stop)

    def clientConnectionFailed(self, connector, reason):
        """
        Обработчик неудачного соединения
        :param connector:
        :param reason:
        :return:
        """
        print("Connection failed")
        reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    reactor.connectTCP(
        "localhost",
        7410,
        UserFactory(input("Your login >>> "))
    )
    reactor.run()