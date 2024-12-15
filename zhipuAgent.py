from zhipuai import ZhipuAI
import logging
import re

import os

from config import config


class ZhipuAgent:

    def __init__(self, role_number, experiment_name='1', count=1):
        # 调用智谱接口
        self.client = ZhipuAI(
            api_key="ca64e5d70ba7e6da43462f211b45d75b.sE0oIZwtjbBTnz1U")
        # 初始化上下文
        self.context = []
        self.order = role_number
        self.spy_suspect = 0

        # 设置日志级别
        logging.basicConfig(level=logging.DEBUG)
        # 创建一个日志器
        self.logger = logging.getLogger(str(self.order))

        # 创建结果文件夹
        result_dir = f"./result/{experiment_name}/{count}/"
        os.makedirs(result_dir, exist_ok=True)

        # 设置日志文件路径
        log_file_path = os.path.join(result_dir, f"{str(self.order)}.log")
        self.file_handler = logging.FileHandler(log_file_path, "w")
        self.file_handler.setLevel(logging.DEBUG)

        # 创建一个格式器，用于定义日志输出的格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # 将处理器添加到日志器
        self.logger.addHandler(self.file_handler)
        self.history = []

    def start_game(self):
        # 开始游戏

        # 打开文件，并读取其内容
        with open('./prompt/init_prompt.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        self.ask_zhipu(content)

    def set_config(self, config):
        # 设置配置
        self.keyword = config["keyword"]

    def describe(self, former_utterance):
        if former_utterance == "":
            descripe_prompt = ""
        else:
            descripe_prompt = former_utterance

        descripe_prompt += "你是第" + str(self.order) + "号玩家。"
        descripe_prompt += "你分配到的关键词是：<" + self.keyword + ">。"
        descripe_prompt += "请开始描述。只输出描述，不要输出别的信息。"
        descripe_prompt += "注意，你的回答中绝对不能包含你的关键词<" + self.keyword + ">。"

        ans = self.ask_zhipu(descripe_prompt)
        # match = re.findall(r"\([^()]*\)", ans)

        return ans

    def describe_cot(self, former_utterance, round, classfication):
        ans = ""
        if round == 0:
            content = f"|| 你是第{self.order}号玩家，你的关键词是<{self.keyword}>。你的回答中绝对不能包含你的关键词<{self.keyword}>。这是第一轮描述，不需要分析||之前别的玩家的描述，请你描述关键词基本特征，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类，描述包括以下两点，1.他的基本特征是什么2.他在该类（{classfication}）中最突出不同的特征是什么，尽量简短"
            ans = self.ask_zhipu(former_utterance + content)

        if round == 1:
            content = f"你是第{self.order}号玩家，你的关键词是<{self.keyword}>。你的回答中绝对不能包含你的关键词<{self.keyword}>。这是第二轮描述，你之前的描述是{self.history[0]}，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类，请你补充关于关键词的描述，注意，你的描述应该比起之前的描述更加贴近关键词，作为之前的补充"
            ans = self.ask_zhipu(former_utterance + content)


        if round == 2:
            content = f"你是第{self.order}号玩家，你的关键词是<{self.keyword}>。你的回答中绝对不能包含你的关键词<{self.keyword}>。这是第三轮描述，你之前的描述是{self.history[0]}和{self.history[1]}，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类，请你补充关于关键词的描述，注意，你的描述应该比起之前的描述更加贴近关键词，作为之前的补充"
            ans = self.ask_zhipu(former_utterance + content)

        self.history.append(ans)
        return ans

    def cot_judge(self, former_utterance, classfication, r):
        content = f"||在这个游戏中，我们需要通过分析每位玩家的描述来找出卧底。通常，平民的描述会围绕相同的词语展开，而卧底的描述可能会因为词语的不同而显得不太一致。我们需要仔细比较每个描述之间的相似性和差异性，以找出可能的卧底，注意，卧底并不会隐藏自己，他会直接描述他的词语，现在，逐一分析每个玩家的描述，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类。"
        if(r!=0):
            content += f"||之前是第{r+1}轮描述和之前轮数描述的合集。你之前认为的卧底是玩家{self.spy_suspect}。"
        else:
            content += "这是第一轮描述。"
        ans = self.ask_zhipu(former_utterance + content)
        content = f"你刚刚的分析是{ans}|| `请根据上述分析，比较描述以找出不一致之处，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类。"
        ans = self.ask_zhipu(content)
        content = f"你刚刚的分析是{ans}|| 请通过你分析的不一致之处，推断卧底身份，注意，这局游戏的词语分类为<{classfication}>，卧底词和平民词都属于该类。"
        ans = self.ask_zhipu(content)
        content = f"你刚刚的推断是{ans}|| 基于你刚刚的推断得出你的最终结论，请输出你认为的卧底，在这种情况下只需要输出编号，是1-4中的某个数字，不要输出其他信息。在这个过程不要进行任何推理，只对||以前的部分进行信息提取"
        while True:
            ans = self.ask_zhipu(content)
            # 检查 ans 是否是 1-4 的纯数字字符串
            if ans.isdigit() and 1 <= int(ans) <= 4:
                break
            else:
                self.logger.warning(f"Invalid vote: {ans}. Asking again.")

        return int(ans)

    def vote(self, former_utterance, classfication):

        if config["judge_cot"]:
            self.spy_suspect = self.cot_judge(former_utterance, classfication, 2)

        else:
            vote_prompt = "请投票，输入你认为是卧底的玩家编号，是1-4中的某个数字，不要输出其他信息。"
            self.spy_suspect = int(self.ask_zhipu(vote_prompt))


        if self.spy_suspect == self.order:
            vote_prompt = f"你认为卧底是你自己。你现在需要随便选一个人投票。请输出一个数字，是1-4中的某个数字，但这个数字不能是{self.order}，不要输出其他信息。"

            while True:
                self.spy_suspect = self.ask_zhipu(vote_prompt)
                # 检查 ans 是否是 1-4 的纯数字字符串
                if self.spy_suspect.isdigit() and 1 <= int(
                        self.spy_suspect) <= 4:
                    break
                else:
                    self.logger.warning(
                        f"Invalid vote: {self.spy_suspect}. Asking again.")

        self.logger.removeHandler(self.file_handler)
        return int(self.spy_suspect)

    def ask_zhipu(self, user_message):

        self.logger.info("**********JUDGER" + "**********\n" + user_message)
        # 更新上下文
        self.context.append({"role": "user", "content": user_message})

        try:
            # 创建对话消息列表，包括系统消息、上下文消息和用户最新消息
            # 使用+操作符将上下文添加到消息列表中
            messages = [{
                "role": "system",
                "content": "你现在不是ai助手，你是参与谁是卧底游戏的一个玩家，请输出符合玩家身份的内容"
            }] + self.context

            response = self.client.chat.completions.create(
                model="GLM-4-flash",
                messages=messages,
                top_p=0.7,
                temperature=0.95,
                max_tokens=10000,
                tools=[{
                    "type": "web_search",
                    "web_search": {
                        "search_result": True
                    }
                }],
                stream=True)

            ans = ""
            for trunk in response:
                ans += trunk.choices[0].delta.content

            # 将AI的回复也添加到上下文中
            self.context.append({"role": "assistant", "content": ans})
            self.logger.info("**********PLAYER" + str(self.order) +
                             "**********\n" + ans)

            return ans

        except Exception as e:
            self.logger.warning("发生错误：", e)
            return None


# 使用ZhipuAgent
if __name__ == '__main__':
    zhipuAgent = ZhipuAgent(2)
    with open('./prompt/cot_test.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    zhipuAgent.vote(content)
