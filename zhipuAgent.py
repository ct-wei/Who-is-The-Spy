from zhipuai import ZhipuAI
import logging
import re

class ZhipuAgent:
    def __init__(self,role_number):
        # 调用智谱接口
        self.client = ZhipuAI(api_key="ca64e5d70ba7e6da43462f211b45d75b.sE0oIZwtjbBTnz1U")
        # 初始化上下文
        self.context = []
        self.order = role_number
        
        # 设置日志级别
        logging.basicConfig(level=logging.DEBUG)
        # 创建一个日志器
        self.logger = logging.getLogger(str(self.order))
        
        
        self.file_handler = logging.FileHandler(str(self.order)+'.log',"w")
        self.file_handler.setLevel(logging.DEBUG)

        # 创建一个格式器，用于定义日志输出的格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # 将处理器添加到日志器
        self.logger.addHandler(self.file_handler)

        
    def start_game(self):
        # 开始游戏
        
        # 打开文件，并读取其内容
        with open('/Users/teddy/Desktop/大学/博士/AML高级机器学习/Whoisspy/init_prompt.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        self.ask_zhipu(content)

    
    def set_config(self, config):
        # 设置配置
        self.keyword=config["keyword"]
    
    
    
    def describe(self,former_utterance):
        if former_utterance == "":
            descripe_prompt=""
        else:
            descripe_prompt=former_utterance
            
        descripe_prompt+="你是第"+str(self.order)+"号玩家。"
        descripe_prompt+= "你分配到的关键词是：<"+self.keyword+">。"
        descripe_prompt+="请开始描述。"
        
        ans=self.ask_zhipu(descripe_prompt)
        # match = re.findall(r"\([^()]*\)", ans)

        return ans
    
    
    def vote(self, former_utterance):
        
        vote_prompt="请投票,只输出数字。"
        final_prompt=former_utterance+vote_prompt
        ans=self.ask_zhipu(final_prompt)
        return ans
    
    
    def ask_zhipu(self, user_message):
        
        self.logger.info("**********JUDGER"+"**********\n"+user_message)
        # 更新上下文
        self.context.append({"role": "user", "content": user_message})

        try:
            # 创建对话消息列表，包括系统消息、上下文消息和用户最新消息
            # 使用+操作符将上下文添加到消息列表中
            messages = [{"role": "system", "content": "让我们来玩一个叫做<谁是卧底>的推理游戏。基本规则：<人数>：4人。<角色分配>：每位玩家随机抽取一个词语，3名玩家拿到的词语是相同的（平民词），1名玩家拿到与之相近但不同的词语（卧底词）。<游戏流程>：1、玩家轮流描述自己的词语，但<不能>直接说出词语本身。2、描述完毕后，投票选出最像卧底的玩家。3、每轮结束后，被投票选出的玩家出局，不能再进行描述或投票。4、每轮投票结束后，如果卧底被成功找出，平民方获胜；如果卧底未被找出且卧底人数等于或超过平民人数，则卧底方获胜。你将扮演一个<玩家>，请等待你被分配到的关键词。"}] + self.context 
            
            response = self.client.chat.completions.create(
                model="GLM-4-flash",
                messages=messages,
                top_p=0.7,
                temperature=0.95,
                max_tokens=100,
                tools=[{"type":"web_search","web_search":{"search_result":True}}],
                stream=True
            )

            ans = ""
            for trunk in response:
                ans += trunk.choices[0].delta.content

            # 将AI的回复也添加到上下文中
            self.context.append({"role": "assistant", "content": ans})
            self.logger.info("**********PLAYER"+str(self.order)+"**********\n"+ans)
            
            return ans
            
        except Exception as e:
            self.logger.warning("发生错误：", e)
            return None

# 使用ZhipuAgent
if __name__ == '__main__':
    zhipuAgent = ZhipuAgent(1)
    zhipuAgent.start_game()
    
    # 模拟用户提问
    user_message = "我上句话说了什么"
    a = zhipuAgent.ask_zhipu(user_message)
    print(a)
    
#    import re

#     # 假设我们有一个包含引号的字符串
# string = '你好"发"红包'

# # 使用正则表达式匹配双引号和单引号中间的内容
# match = re.findall(r"(?<=\"|').*?(?=\"|')", string)

# # 输出匹配结果
# for content in match:
#     print(match)