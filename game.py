from zhipuAgent import ZhipuAgent
from config import config
import logging
from Judge import Judge
from datetime import datetime

import csv
import os

if __name__ == '__main__':

    # 设置日志级别
    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    judge = Judge()
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    result_dir = f"./result/{config['name']}-{current_time}/"
    os.makedirs(result_dir, exist_ok=True)
    result_file = os.path.join(result_dir, "experiment_results.csv")

    with open(result_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入表头
        writer.writerow(["Roles", "Spy", "Result", "Votes", "Incorrect Votes"])

        total_wins = 0
        total_ties = 0
        total_errors = 0
        total_incorrect_votes = 0

        for i in range(config['exp_times']):
            players = judge.start_game(config=config,
                                       time=current_time,
                                       count=i)
            roles, spy, res, votes, incorrect_votes = judge.play_role()

            # 写入实验结果
            writer.writerow([roles, spy, res, votes, incorrect_votes])

            # 更新统计信息
            if res == 0:
                total_wins += 1
            elif res == 1:
                total_ties += 1
            elif res == 2:
                total_errors += 1

            total_incorrect_votes += incorrect_votes

        # 计算非卧底投票错率
        total_non_spy_votes = config['exp_times'] * (config['players_num'] - 1)
        incorrect_vote_rate = total_incorrect_votes / total_non_spy_votes if total_non_spy_votes > 0 else 0

        # 写入统计信息
        writer.writerow([])  # 空行分隔
        writer.writerow([
            "Total Wins", "Total Ties", "Total Errors", "Incorrect Vote Rate",
            "Total Non-Spy Votes"
        ])
        writer.writerow([
            total_wins, total_ties, total_errors, f"{incorrect_vote_rate:.2%}",
            total_non_spy_votes
        ])

    print(f"实验结果已保存至: {result_file}")
