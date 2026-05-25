import requests
import logging
from time import sleep
from bs4 import BeautifulSoup

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": "",
}

PAGES = range(10, 15) # 抓取题目的页码
PROBLEM_IDS = list(range(1201, 1427)) # 要抓取题目的编号
PROBLEM_NUM = len(PROBLEM_IDS) # 要抓取题目的数量
# 要抓取 AC 记录的用户
USER_UIDS = [653, 339, 474, 494, 488, 216, 465, 478, 
            482, 481, 338, 333, 479, 335, 486, 331, 
            329, 307, 340, 336, 208, 222, 487, 495, 
            214, 468, 470, 197, 167, 469, 282, 143, 177, 189]
problem_names = []
users = []

def get_problems(file):
    for page in PAGES:
        url = f"http://oi.bashu.cn/d/junior/p?page={page}"
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.text, 'html.parser')
        problems = soup.select("td.col--problem-name")
        for problem in problems:
            id = int(problem.select_one("b").get_text(strip=True))
            if id in PROBLEM_IDS:
                name = problem.select_one("a").contents[1].get_text(strip=True)
                logging.info(f"A problem has been crawled. id: {id}, name: {name}")
                problem_names.append(name)

        sleep(0.1)
    
    buf = ""
    for id in PROBLEM_IDS:
        buf += f"{id}\t"
    buf = buf.strip()
    buf += "\n114514\t114514\t114514\t" # 114514 占位用
    for name in problem_names:
        buf += f"{name}\t"
    buf = buf.strip()
    buf += "\n"
    file.write(buf)

def get_user_status(file):
    for uid in USER_UIDS:
        url = f"http://oi.bashu.cn/d/junior/user/{uid}#tab-1"
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.text, 'html.parser')
        username = soup.select_one("h1").get_text(strip=True).split("(")[0]
        if username == "登录":
            logging.warning("The website needs logging in.")
            continue
        status = [0] * PROBLEM_NUM
        AC_problem_ids = soup.select("a")
        for id in AC_problem_ids:
            if(len(id.contents) == 0):
                continue
            if len(str(id.contents[0]).split(">")) >= 2:
                AC_problem_id = str(id.contents[0]).strip("<b>").strip("</b>")
                if not AC_problem_id.isdigit():
                    continue
                AC_problem_id = int(AC_problem_id)
                if AC_problem_id in PROBLEM_IDS:
                    index = PROBLEM_IDS.index(AC_problem_id)
                    status[index] = 1
                    logging.info(f"User {username} has AC a problem. id: {AC_problem_id}")
        AC_problem_num = status.count(1)
        logging.info(f"User {username} has AC {AC_problem_num} problem(s).")
        global users
        user = [0, username, AC_problem_num] + status.copy()
        users.append(user)

        sleep(0.1)
    
    users = sorted(users, key=lambda x: -x[2])
    for rank in range(len(users)):
        users[rank][0] = rank + 1
    for user in users:
        buf = ""
        for element in user:
            buf += f"{element}\t"
        buf = buf.strip()
        buf += "\n"
        file.write(buf)

import os

def main():
    sid = os.environ.get('SID')
    sid_sig = os.environ.get('SID_SIG')
    if not sid or not sid_sig:
        logging.error("Missing SID or SID_SIG environment variables.")
        raise ValueError("Missing SID or SID_SIG environment variables.")
    header["Cookie"] = f"sid={sid}; sid.sig={sid_sig}"
    logging.basicConfig(level=logging.INFO)
    logging.info("Begin to crawl the problems and the users' statuses.")
    with open("data.tsv", "w", encoding="utf-8") as file:
        file.write("排名\t用户名\tAC 数量\t")
        get_problems(file)
        logging.info("All the problems have been crawled.")
        get_user_status(file)
        logging.info("All the users' statuses have been crawled.")

if __name__ == "__main__":
    main()