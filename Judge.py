from RoleIterator import RoleIterator
from config import config
from zhipuAgent import ZhipuAgent


class Judge:

    def __init__(self):
        self.true_spy = 0
        self.roles = []
        pass

    def judge(self, text):
        pass

    def start_game(self, config, time, count=1):
        self.players = []
        role_iterator = RoleIterator(config['data'])
        self.true_spy = role_iterator.true_spy
        self.roles = role_iterator.roles
        self.classfication = role_iterator.classfication

        for role_number, role_name in role_iterator:
            agent = ZhipuAgent(role_number, f"{config['name']}-{time}", count)
            agent.start_game()
            player_config = {"player_num": role_number, "keyword": role_name}
            agent.set_config(player_config)
            self.players.append(agent)
        return self.players

    def play_role(self):
        content_history = [[],[],[],[]]
        for r in range(config['round']):
            for player in self.players:
                ans = ""
                # make utterance
                former_utterance = make_former_utterance(content_history)

                if config['describe_cot']:
                    ans = player.describe_cot(
                        former_utterance, r,
                        self.classfication)  # read the content and describe
                    while (self.check_violation(ans, player)):
                        ans = player.describe_cot(former_utterance, r, self.classfication)

                else:
                    ans = player.describe(former_utterance)

                    # check violation
                    while (self.check_violation(ans, player)):
                        ans = player.ask_zhipu(
                            "不能直接说出词语本身，请重新描述。只输出自己的描述，不要输出别的信息。")

                content_history[player.order - 1].append(ans)
            if(r != 2):
                for player in self.players:
                    player.spy_suspect = player.cot_judge(
                        former_utterance, self.classfication, r)


        votes = []
        incorrect_count = 0
        for index, player in enumerate(self.players):
            former_utterance = make_former_utterance(content_history)
            ans = player.vote(former_utterance, classfication=self.classfication)
            votes.append(ans)
            if player.order != self.true_spy and int(ans) != self.true_spy:
                incorrect_count += 1

        res, all_players = self.count_votes(votes)
        if res == 0:
            print("卧底被成功投出")
        if res == 1:
            print("没有投出任何人")
        if res == 2:
            print("投出非卧底")
        print("非卧底错误投票数：" + str(incorrect_count))

        return self.roles, self.true_spy, res, all_players, incorrect_count

    def check_violation(self, ans, player):

        if player.keyword in ans:
            return True
        else:
            return False

    def count_votes(self, votes):
        all_players = dict()
        for player in self.players:
            all_players[player.order] = 0

        print("votes")
        for vote in votes:
            for player in all_players:
                if player == vote:
                    all_players[player] += 1

        # 检查是否平票
        max_votes = max(all_players.values())
        candidates = [
            player for player, count in all_players.items()
            if count == max_votes
        ]

        out_index = candidates[0]
        print(all_players)

        if len(candidates) > 1:
            # 平票情况
            return 1, all_players,

        # 判断投票结果
        if out_index == self.true_spy:
            # 卧底成功被投出
            return 0, all_players
        else:
            # 普通人被错误投出
            return 2, all_players


def make_former_utterance(content_history):
    former_utterance = ""
    for order, player in enumerate(content_history):
        former_utterance += "玩家" + str(order+ 1) + "说："
        for content in player:
            former_utterance += content
    return former_utterance


if __name__ == '__main__':
    Judge().start_game(config=config)
