import time
import logging
import threading
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc


class Client:
    def __init__(self, stub, user):
        self.stub = stub
        self.user = user
        self.loggedin = False

    def login(self):
        request = chat.Post(user=self.user, message='')
        self.loggedin = True
        _ = self.stub.Login(request)

    def logout(self):
        request = chat.Post(user=self.user, message='')
        self.loggedin = False
        _ = self.stub.Logout(request)

    def send(self, msg):
        request = chat.Post(user=self.user, message=msg)
        _ = self.stub.Send(request)

    def stream(self):
        for post in self.stub.Stream(chat.Empty()):  # esta linha irá aguardar novas mensagens do servidor!
            if not self.loggedin:
                break

            if self.user == post.user:
                continue

            print("[{}]: {}".format(post.user, post.message))


def main():
    logging.info("Cliente iniciou às {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))
    try:
        ipservidor = input("Digite o IP do Servidor: ")
        channel = grpc.insecure_channel(ipservidor+":50051")
#        channel = grpc.insecure_channel("localhost:50051")
        stub = rpc.ChatStub(channel)
        logging.info("Criado canal às {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))

        user = input("\nEntre com usuário: ")

        client = Client(stub, user)
        client.login()

        thread = threading.Thread(target=client.stream, daemon=True)
        thread.start()

        while True:
            msg = input()

            if msg == "q":
                client.logout()
                break

            client.send(msg)

    except KeyboardInterrupt:
        pass
    finally:
        channel.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
