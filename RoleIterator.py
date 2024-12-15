import csv
import random

class RoleIterator:

    def __init__(self, file):
        # 读取 CSV 文件中的数据
        with open(file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # 将所有行读取到列表中
            data = list(reader)

        # 从数据中随机选择一行
        random_row = random.choice(data)

        # 将随机行的前四列作为角色关键词
        self.roles = random_row[:4]
        # 将第五列（卧底位置）作为 true_spy
        self.true_spy = int(random_row[4])  # 转换为索引，减1表示从0开始
        self.classfication = random_row[5]

        # 初始化索引
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.roles):
            role_info = (self.index + 1, self.roles[self.index])
            self.index += 1
            return role_info
        else:
            raise StopIteration

if __name__ == '__main__':

    role_iterator = RoleIterator("./data/4player.csv")

    for role_number, role_name in role_iterator:
        print(f'角色序号：{role_number}, 角色名：{role_name}')
