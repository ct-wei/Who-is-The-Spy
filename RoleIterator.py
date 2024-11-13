class RoleIterator:
    def __init__(self):
        self.roles = ['班主任', '班主任', '辅导员', '班主任']
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

    role_iterator = RoleIterator()

    for role_number, role_name in role_iterator:
        print(f'角色序号：{role_number}, 角色名：{role_name}')
