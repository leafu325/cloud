import socket
import threading
from ollama import Client
from wiki import search_information_from_wiki

port = 8001

class P2PNode:
    def __init__(self):
        self.client = Client(host='http://localhost:11434')
        self.port = 8001
        self.peers = [('172.17.0.3', port)]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('172.17.0.2', self.port)) 

    def start(self):
        threading.Thread(target=self._say).start()

    def _say(self):
        while True:
            content = input("Say something: ")
            self.inference(content)

    def send_messages(self, message):
        for peer in self.peers:
            self.sock.sendto(message.encode('utf-8'), peer)

    def inference(self, content):

        keyword = self.client.chat(model='llama3', messages = [
            {
            'role': 'user',
            'content':content,
                },
            {
            'role': 'user',
            'content': 'Please only return key word or main topic of this content for me',
                },
            ])

        data_string = search_information_from_wiki(keyword['message']['content'])

        response = self.client.chat(model='llama3', messages=[
            {
            'role': 'user',
            'content': content,
            },
            {
            'role': 'assistant',
            'content': f"Please use following infomation tell user about {keyword['message']['content']}:\n {data_string}",
            }
            ,
        ])

        message = f"{response['message']['content']}"
        self.send_messages(message)



if __name__ == "__main__":
    node = P2PNode()
    node.start()
