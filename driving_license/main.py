import time
from datetime import datetime

import requests

# 预约时间 09:30 - 16:30
# 需要更新token， 其他地方重新登录获取之后会直接不可用；过期时间：未知， 大于24小时
Authorization = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzdHVkZW50Lm9yT09mNHM5NHNJWlRpU0E0LUM3Sllrd3R1OEUiLCJpYXQiOjE2MjU4Nzk1NDJ9.xtmraMR8LYpI5-wVm-KbzlxiQOArpP0oXeiRdG-h2xWwyB-tJm9UbAH7fSedSQQ14jHVPkVjxprnn8RuZ_DkaA"
StudentID = 224956
CoachID = 101
Subject = 2
BasePath = "https://api.wolun.club/weapp/student"
Headers = {
    "Authorization": Authorization,
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac",
    "Referer": "https://servicewechat.com/wxb2ed80dfa1c8b99f/81/page-frame.html",
    "Content-Type": "application/json",
    "Host": "api.wolun.club",
    "Connection": "keep-alive"
}


def get_lessons():
    params = {
        "subject": Subject,
        "coachId": CoachID,
    }
    resp = requests.get(BasePath + "/getAllFromLesson", params=params, headers=Headers)
    print("Get Lessons Resp: ", resp.text)
    lessons = resp.json().get("data").get("list")
    lessons.sort(key=lambda x: x.get("startDate"))
    return lessons


def appoint_lesson(lesson_id):
    data = {
        "lessonIds": lesson_id,
        "studentId": StudentID
    }
    Headers["Content-Type"] = "application/x-www-form-urlencoded"
    resp = requests.post(BasePath + "/reservationResults", data=data, headers=Headers)
    print("Appoint Lesson Resp: ", resp.text)
    if resp.json().get("success"):
        print("Appoint Lesson Success! \n")
        return True
    print("Appoint Lesson Failed! \n")
    return False


def job():
    print(f"Start time: {datetime.now()}\n")
    lessons = get_lessons()
    day_of_week = datetime.now().weekday()
    if day_of_week in [2, 3]:  # 预约 周六 周天
        target_lesson = lessons[-2]
    else:
        target_lesson = lessons[-1]
    # if target_lesson.get("isAppointment") == 0:
    #     print("Job: 目标课程不可预约！\n")
    #     return
    start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(target_lesson.get("startDate")) // 1000))
    end_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(target_lesson.get("endDate")) // 1000))
    print(f"Target Lesson Info：StartDate => {start_dt}, EndDate => {end_dt}")
    appoint_lesson(target_lesson.get("id"))
    print(f"Finish time: {datetime.now()}\n")


if __name__ == '__main__':
    print("Running...")
    # from apscheduler.schedulers.blocking import BlockingScheduler
    #
    # # BlockingScheduler
    # scheduler = BlockingScheduler()
    # scheduler.add_job(job, 'cron', day_of_week='0-6', hour=9, minute=30, second=00)
    # scheduler.start()
    job()