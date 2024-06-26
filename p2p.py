import os
import hashlib
import socket
import threading

volume_locate = "./BChain/"

local_addr = '172.17.0.11'
port = 8001
peers = [('172.17.0.10', 8001), ('172.17.0.5', 8001)]
test_list = []

class P2PNode:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((local_addr, self.port))

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

            if info.split(',')[0] == 'other_chekcAllChains' and info.split(',')[1] != local_addr:
                other_chekcAllChains(self,info.split(',')[1],info.split(',')[2])
    
            if info.split(',')[0] == "transaction":

                print("===============")
                print(f"Received {info.split(',',1)[1]} from {addr}")
                local_transaction(info)
                print("===============")

            elif info.split(',')[0] == 'check1' and info.split(',')[2] == local_addr:

                with open(volume_locate+'0.txt', mode = 'r') as super_block:
                    last_block = super_block.readline().split(':')[1].strip()

                with open(volume_locate+last_block,'r') as f:

                    text = f.read()
                    hsh_code = hashlib.sha3_256(text.encode()).hexdigest()

                test_list.append([info.split(',')[1],addr])

                if hsh_code != info.split(',')[1]:
                    print(f"({local_addr}, 8001) or {addr} -> NO")
                else:
                    print(f"({local_addr}, 8001) or {addr} -> Yes")

                if  len(test_list) == 2:
                    if test_list[0][0] != test_list[1][0]:
                        print(f"{test_list[0][1]} or {test_list[1][1]} -> NO")
                    else:
                        print(f"{test_list[0][1]} or {test_list[1][1]} -> Yes")

                    check_consensus(test_list,[hsh_code,(local_addr,port)])
                    
                    file = "0.txt"

                    last_block = open(volume_locate + file, mode='r').readline().split(':')[1].strip()
                    block_number = int(last_block.split('.')[0])

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
                                else:
                                    print("block"+last_block+" -> ok")

                        block_number-=1

                    new_information = f"transaction,angel,{info.split(',')[3]},100\n"
                    transaction(self, new_information)
                    test_list.clear()

                    
            elif info.split(',')[0] == 'to_override_node':
                to_override_node(info.split(',',1)[1])

            elif info.split(',')[0] == 'for_ovreride_node':
                for_ovreride_node(info)
            
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
        new_information = new_information.split(',',1)[1]
        if len(last_block_content) >= 7 :
            # if hashlibve five transaction , create new block
            create_block(new_information)
        else:
            # append information
            open(volume_locate + last_block, 'a').write(new_information)

        sender, reciver, money = new_information.strip().split(',')
        print(f"{sender} TRANSFER TO {reciver}: ${money}")
    except Exception as ex:
        print(ex)

def calculate_balance(user):

    balance = 0

    current_dir= '1.txt'
    i = 1
    while True:

        with open(volume_locate + current_dir, 'r') as file:
            lines = file.readlines()

        for line in lines[2:]:
            transaction = line.strip().split(',')
            sender, reciver, money = transaction

            if reciver == user:
                balance += int(money)
            if sender == user:
                balance -= int(money)

        current_dir = lines[1].split(':')[1].strip()

        if(current_dir == "x"):
            break

        i -= 1

    return balance

def checkMoney(user):
    print(f"{user} 'S MONEY : ${calculate_balance(user)}")

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
                else:
                    print("block"+last_block+" -> ok")

        block_number-=1

    if(check == 1):
        print("OK")

        sender = "angel"
        reciver = user
        money = "10"
        transaction(node,f"transaction,{sender},{reciver},{money}\n")

def checkLog(user):
    current_dir= "1.txt" # 起�~K�~^

    while True :

        with open(volume_locate + current_dir, 'r') as file:
            lines = file.readlines()

        for line in lines[2:]:
            transaction = line.strip().split(',')
            sender, reciver, money = transaction

            if reciver == user or sender == user:
                information = f"{sender},{reciver},{money}\n"
                print(information,end='')

        current_dir = lines[1].split(':')[1].strip()

        if(current_dir == "x"):
            break

def other_chekcAllChains(self,start_addr,user):
    
    with open(volume_locate+'0.txt', mode = 'r') as super_block:
        last_block = super_block.readline().split(':')[1].strip()

    with open(volume_locate+last_block,'r') as f:

        text = f.read()
        hsh_code = hashlib.sha3_256(text.encode()).hexdigest()

        message = f"check1,{hsh_code},{start_addr},{user}"

        for peer in self.peers:
            self.sock.sendto(message.encode('utf-8'), peer)
    
    file = "0.txt"
    last_block = open(volume_locate + file, mode='r').readline().split(':')[1].strip()
    block_number = int(last_block.split('.')[0])

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
                else:
                    print("block"+last_block+" -> ok")

        block_number-=1

def check_consensus(test_list,local_list):

    num_different = len({test_list[0][0], test_list[1][0], local_list[0]})

    if num_different == 1:
        print("Nothing")
    elif num_different == 2:
        target = None
        override_from = None
        if test_list[0][0] != test_list[1][0]:

            if test_list[0][0] == local_list[0]:
                target = test_list[1][1]
                override_from = local_list[1]

            elif test_list[1][0] == local_list[0]:
                target = test_list[0][1]
                override_from = local_list[1]

        elif test_list[0][0] != local_list[0]:
            target = local_list[1]
            override_from = test_list[0][1]

        message = f"to_override_node,{target}"
        node.sock.sendto(message.encode('utf-8'), override_from)

    elif num_different == 3:
        print("系統廢了")
    
def to_override_node(target_addr):
    
    current_dir= "1.txt"

    while True :

        if(current_dir == "x"):
            print(f"{target_addr} overriding has finished.")
            break

        with open(volume_locate + current_dir, 'r') as file:
            lines = file.read()

        message = f"for_ovreride_node,{current_dir},{lines},{local_addr}"
        addr_port_parts = target_addr.strip('()').split(',')
        tuple_addr = addr_port_parts[0].strip('\'\'')  
        tuple_addr = (tuple_addr, port)

        node.sock.sendto(message.encode('utf-8'), tuple_addr)
        
        current_dir = lines.split('\n')[1].split(':')[1].strip()


def for_ovreride_node(info):

    current_dir = info.split(',')[1]
    with open(volume_locate + current_dir, 'w') as file:
        content = info.split(',',2)[2]
        content = content.rsplit(',',1)[0]
        file.write(content)


if __name__ == "__main__":

    node = P2PNode(port, peers)
    node.start()

    while True:
        print("===============")
        command = input("Enter a command {transaction,  checkChain, checkLog, checkMoney, checkAllChains, exit} : \n")
        commands = command.strip('\n').split()

        print("===============")
        if commands[0] == "transaction":
            new_information = f"transaction,{commands[1]},{commands[2]},{commands[3]}\n"
            transaction(node, new_information)

        elif commands[0] == "checkChain":
            checkChain(commands[1])

        elif commands[0] == "checkLog":
            checkLog(commands[1])

        elif commands[0] == "checkMoney":
            checkMoney(commands[1])

        elif commands[0] == "checkAllChains":

            command = f"other_chekcAllChains,{local_addr},{commands[1]}"
            for peer in node.peers:
                node.sock.sendto(command.encode('utf-8'), peer)


        elif commands[0] == "exit":
            break
