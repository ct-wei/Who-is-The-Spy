

from zhipuAgent import ZhipuAgent
from config import config
import logging
from Judge import Judge





if __name__ == '__main__':
    
    # 设置日志级别
    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    judge=Judge()
    players=judge.start_game(config=config)
    judge.play_role()

    
        
    
    
    