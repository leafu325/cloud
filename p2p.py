import os
import hashlib
import socket
import threading

volume_locate = "./BChain/" # �~M~@�~J�~O~H�~D��~X�~^

port = 8001 #�~\��~@�~^�~Z~Dport 
peers = [('172.17.0.7', 8001), ('172.17.0.5', 8001)]  #�~_�~O��~V�~L�~@~KIP:8001 �~@�~^�~@~Z信

def check_last_hsh(block):

    with open(volume_locate+block,'r') as f:

        hsh_code = f.readline().split(':')[1].strip()
        print(f"hsh_code:{hsh_code}")

    return hsh_code


class P2PNode:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('172.17.0.6', self.port)) #�~@~Y�~X��~\��~@�~^�~Z~D IP

    def start(self):
        threading.Thread(target=self._listen).start()

    def send_messages(self, transaction_info):
        message = transaction_info
        for peer in self.peers:
            self.sock.sendto(message.encode('utf-8'), peer)

    def _listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            info = data.decode('utf-8')
            if info == 'checkAllChains':

                print("===============")
                content = self.get_file_content('/BChain/0.txt')
                block = content.strip().split(':')[1]
                hsh_code = check_last_hsh(block)
                self.send_messages(hsh_code)
                print("===============")

            elif len(info.split(","))==3:

                print("===============")
                print(f"Received {info=} from {addr}")
                local_transaction(info)
                print("===============")

            else:
                print(f"Hash code {info} from {addr}")
    
    def send_command(self, command):
        message = command
        for peer in self.peers:
            self.sock.sendto(message.encode('utf-8'), peer)

    def send_hsh_code(self, hsh_code):
        message = hsh_code
        for peer in self.peers:
            self.sock.sendto(message.encode('utf-8'), peer)

    def get_file_content(self, filename):
        with open(filename,'r') as f:
            content = f.read()
        return content
    
def transaction(communicator, new_information):
    local_transaction(new_information)
    communicator.send_messages(new_information)

def create_block(new_information):

    file = '0.txt' # super block

    # read super block
    with open(volume_locate + file, mode='r') as super_block:
        # last block file
        last_block = super_block.readline().split(':')[1].strip()
        # new block file
        new_block = str(int(last_block.split('.')[0]) + 1) + ".txt"

    # update super block
    with open(volume_locate + file, mode='w') as super_block:
        super_block.write("block:" + new_block)

    # read last block content
    with open(volume_locate + last_block, mode='r') as f:
        text = f.readlines()

    # write last block's next block
    with open(volume_locate + last_block, mode='w') as f:
        text[1] = text[1][:12] + f"{new_block}\n"
        f.writelines(text)

    # create and write new block
    with open(volume_locate + new_block, mode='w') as f:
        encode = hashlib.sha3_256()
        encode.update( ''.join(text[:]).encode(encoding='utf-8'))
        new_content = ["Shashlib256 of previous block:" + f" {encode.hexdigest()}\n", "Next block: x\n"]
        f.write(''.join(new_content[:]))
        f.write(new_information)


def local_transaction(new_information):

    file = '0.txt'

    try:
        # read super block for finding last block
        last_block = open(volume_locate + file, mode='r').readline().split(':')[1].strip()

        # read last block
        with open(volume_locate + last_block, 'r') as f:
            last_block_content = f.readlines()

        class E(Exception):
            def __str__(self):
                return "0.txt record block that not last block"

        # For check 0.txt record is last block
        if last_block_content[1][12] != 'x':
            raise E

        # write information
        if len(last_block_content) >= 7 :
            # if hashlibve five transaction , create new block
            create_block(new_information)
        else:
            # append information
            open(volume_locate + last_block, 'a').write(new_information)

        sender, reciver, money = new_information.strip().split(',')
        print(f"{sender}�~I帳�~G�{reciver}: ${money}")
    except Exception as ex:
        print(ex)


def calculate_balance(user):
    balance = 0  # �~H~]�~K�~L~V�~X�~M 

    # 循�~R��~A~M歷�~I~@�~\~I�~M~@�~J
    current_dir= '1.txt' # 起�~K�~^
    i = 1
    while(1):

        with open(volume_locate + current_dir, 'r') as file:
            lines = file.readlines()

        # 跳�~A~N�| ��~E��~L�~H�~I~M�~@�~M~@�~J�~Z~D�~S~H�~L�~@��~R~L�~K�~@�~@~K�~M~@�~J�~Z~D�~L~G�~P~Q�~I
        for line in lines[2:]:
            transaction = line.strip().split(',')
            sender, reciver, money = transaction

            # �| ��~S~Z交�~X~S�~[��~V��~X�~M
            if reciver == user:
                balance += int(money)
            if sender == user:
                balance -= int(money)

        # 移�~K~U�~H��~K�~@�~@~K�~M~@�~J�~L�~B�~^~\�~R�~\~I�~K�~@�~@~K�~M~@�~J�~L�~P�~]~_循�~R�
        current_dir = lines[1].split(':')[1].strip()

        if(current_dir == "x"):
            break

        i -= 1

    return balance

def checkMoney(user):
    print(f"{user}�~Z~D帳�~H��~X�~M�~X�: ${calculate_balance(user)}")

def checkChain(user):
    #setting
    file = "0.txt"
    check = 1

    # read super block for finding last block

    last_block = open(volume_locate + file, mode='r').readline().split(':')[1].strip()
    block_number = int(last_block.split('.')[0])

    #checkChashlibin
    while block_number != 1:

        recent_block = f"{block_number}"
        last_block = f"{block_number-1}"

        recent_block_file = os.path.join(recent_block+".txt")
        test_block_file = os.path.join(last_block+".txt")

        with open(volume_locate + recent_block_file,"r") as f:
            with open(volume_locate + test_block_file,"r") as f2:

                text2 = f2.read()
                test_hsh_code = hashlib.sha3_256(text2.encode()).hexdigest()

                text = f.read().split('\n')
                hsh = text[0].split(': ')[1].strip()

                if(test_hsh_code != hsh):

                    print("block"+last_block+" -> error")
                    print("block"+recent_block+"'s hashlibsh code : "+str(hsh))
                    print("block"+last_block+": "+str(test_hsh_code))
                    check = 0

                else:
                    print("block"+last_block+" -> ok")

        block_number-=1

    if(check == 1):
        print("OK")

        sender = "angel"
        reciver = user
        money = "10"
        transaction(node,f"{sender},{reciver},{money}\n")

def checkLog(user):
    current_dir= "1.txt" # 起�~K�~^

    while(1):

        with open(volume_locate + current_dir, 'r') as file:
            lines = file.readlines()

        # 跳�~A~N�| ��~E��~L�~H�~I~M�~@�~M~@�~J�~Z~D�~S~H�~L�~@��~R~L�~K�~@�~@~K�~M~@�~J�~Z~D�~L~G�~P~Q�~I
        for line in lines[2:]:
            transaction = line.strip().split(',')
            sender, reciver, money = transaction

            if reciver == user or sender == user:
                information = f"{sender},{reciver},{money}\n"
                print(information,end='')


        # 移�~K~U�~H��~K�~@�~@~K�~M~@�~J�~L�~B�~^~\�~R�~\~I�~K�~@�~@~K�~M~@�~J�~L�~P�~]~_循�~R�
        current_dir = lines[1].split(':')[1].strip()

        if(current_dir == "x"):
            break
def checkAllChain(communicator, command):
    communicator.send_command(command)


if __name__ == "__main__":

    node = P2PNode(port, peers)
    node.start()

    while True:
        print("===============")
        command = input("Enter a command {transaction,  checkChain, checkLog, checkMoney, checkAllChains, exit} : \n")
        commands = command.strip('\n').split()

        print("===============")
        if commands[0] == "transaction":
            new_information = f"{commands[1]},{commands[2]},{commands[3]}\n"
            transaction(node, new_information)

        elif commands[0] == "checkChain":
            checkChain(commands[1])

        elif commands[0] == "checkLog":
            checkLog(commands[1])

        elif commands[0] == "checkMoney":
            checkMoney(commands[1])

        elif commands[0] == "checkAllChains":
            checkAllChain(node,command[0])

        elif commands[0] == "exit":
            break

        else:
            print(f"Command Error : {command}")
            print(f"                {'^' * len(command)}")