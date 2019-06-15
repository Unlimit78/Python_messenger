from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)
        print(f"Client connected: {self.ip}")
        self.transport.write("Welcome to the chat v0.1\n".encode())
        file = open('base.txt','r')
        previous_messages = file.readlines()
        for message in previous_messages:
            message = message.replace('\n','')
            print(message)
            self.transport.write((message+'\n').encode())
        file.close()

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')
        file = open('base.txt','a')
        if self.login is not None:
            server_message = f"{self.login}: {message}"
            file.write(server_message+'\n')
            file.close()
            self.factory.notify_all_users(server_message)

            print(server_message)
        else:
            if message.startswith("login:"):
                self.login = message.replace("login:", "")
                if self.login not in self.factory.logins:
                    self.factory.logins.append(self.login)
                    notification = f"New user connected: {self.login}"
                    self.factory.notify_all_users(notification)
                    print(notification)
                else:
                    self.transport.write("Wrong Login ... \n".encode())
                    self.login = None
                    self.connectionLost()

            else:
                print("Error: Invalid client login")

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        self.logins = ['user']
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()