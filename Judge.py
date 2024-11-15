
from RoleIterator import RoleIterator
from config import config
from zhipuAgent import ZhipuAgent

class Judge:
    def __init__(self):
        pass

    def judge(self, text):
        pass
    
    def start_game(self,config):
        self.players=[]
        role_iterator = RoleIterator()

        for role_number, role_name in role_iterator:
            agent = ZhipuAgent(role_number)
            agent.start_game()
            player_config={
                "player_num":role_number,
                "keyword":role_name
            }
            agent.set_config(player_config)
            self.players.append(agent)
        return self.players

    
    def play_role(self):
        content_history = []
        for player in self.players:
            # make utterance
            former_utterance=make_former_utterance(content_history)
            
            # read the content and describe
            ans=player.describe(former_utterance)
            
            # check violation
            while(self.check_violation(ans,player)):
                ans=player.ask_zhipu("不能直接说出词语本身，请重新描述。")
                
            content_history.append([player.order,ans])
        
        votes=[]
        for player in self.players:
            former_utterance=make_former_utterance(content_history)
            ans=player.vote(former_utterance)
            votes.append(ans)
        
        out_index=self.count_votes(votes)
        print("玩家"+str(out_index)+"淘汰")

    def check_violation(self,ans,player):
        
        if player.keyword in ans:
            return True
        else:
            return False
    
    
    def count_votes(self,votes):
        all_players=dict()
        for play in self.players:
            all_players[play.order]=0
        
        print("vots")
        for vote in votes:
            for player in all_players:
                if str(player) in vote:
                    all_players[player]+=1
                    
        out_index=max(all_players,key=all_players.get)
        print(all_players)
        return out_index
        
    

def make_former_utterance(content_history):
    former_utterance = ""
    for order,ans in content_history:
        former_utterance += "玩家"+str(order)+"说："+ans
    return former_utterance

if __name__ == '__main__':
    Judge().start_game(config=config)

