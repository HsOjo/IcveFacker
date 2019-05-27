import json
import time
from urllib.parse import parse_qs

import requests

LOGIN_URL = 'https://zjy2.icve.com.cn/common/login/login'
KEEP_URL = 'https://zjy2.icve.com.cn/study/homework/keep'
ANSWER_URL = 'https://zjy2.icve.com.cn/study/homework/onlineHomeworkAnswer'
SAVE_URL = 'https://zjy2.icve.com.cn/study/homework/onlineHomeWorkSaveDraft'
STUDY_LIST_URL = 'https://zjy2.icve.com.cn/common/courseLoad/getStuStudyClassList'
PROCESS_LIST_URL = 'https://zjy2.icve.com.cn/study/process/getProcessList'
TOPIC_LIST_URL = 'https://zjy2.icve.com.cn/study/process/getTopicByModuleId'
CELL_LIST_URL = 'https://zjy2.icve.com.cn/study/process/getCellByTopicId'
LOG_URL = 'https://zjy2.icve.com.cn/common/Directory/stuProcessCellLog'
VIEW_URL = 'https://zjy2.icve.com.cn/common/Directory/viewDirectory'
ONLINE_URL = 'https://dm.icve.com.cn/ZjyLogsManage/zjyUserOnlineTimeRedis'
PREVIEW_URL = 'https://zjy2.icve.com.cn/study/onlineExam/preview'
EXAM_ANSWER_URL = 'https://zjy2.icve.com.cn/study/onlineExam/onlineExamAnswer'

LOGIN_DATA = input('login data:')

sess = requests.session()

data_login = parse_qs(LOGIN_DATA, True)
r_login = sess.post(LOGIN_URL, data=data_login)
r_login_str = r_login.content.decode()
r_login_data = json.loads(r_login_str)
print(r_login_data)


# sess.post('https://zjy2.icve.com.cn/portal/TeacherOnlineApply/isMergerUser', {'userId': r_login_data['userId']})
# print(sess.cookies.get_dict())

def keep_alive():
    data_online = {
        'userId': r_login_data['userId'],
        'userName': r_login_data['userName'],
        'userDisplayName': r_login_data['displayName'],
    }
    #     while True:
    #         time.sleep(1)
    sess.post(ONLINE_URL, data_online)


#
#
# Thread(target=keep_alive).start()


def homework():
    KEEP_DATA = input('keep data:')

    data_keep = parse_qs(KEEP_DATA, True)
    r_keep = sess.post(KEEP_URL, data=data_keep)
    r_keep_str = r_keep.content.decode()
    r_keep_data = json.loads(r_keep_str)

    for i in r_keep_data['questions']:
        data = {
            'online': '1',
            'studentWorkId': i['Id'],
            'answer': '',
        }

        answers = ','.join([str(i) for i in i['Answer']])
        if i['questionType'] == 1:  # single select
            data['answer'] = answers
        elif i['questionType'] == 3:  # judge
            data['answer'] = answers
        else:
            print('unknown question type: %s' % i['questionType'])
        answer_resp = sess.post(ANSWER_URL, data=data)
        answer_data = json.loads(answer_resp.content.decode())
        print(i['Title'], answer_data)
        time.sleep(0.5)

    so_data = [{'Id': v['Id'], 'SortOrder': i + 1} for i, v in enumerate(r_keep_data['questions'])]
    so_data_str = json.dumps(so_data)

    data = {
        'uniqueId': r_keep_data['uniqueId'],
        'homeWorkId': data_keep['homeWorkId'],
        'openClassId': data_keep['openClassId'],
        'homeworkTermTimeId': '',
        'paperStructUnique': '',
        'useTime': '2333',
        'sortOrder': so_data_str,
        'studentWorkId': data_keep['studentWorkId'],
    }
    sess.post(SAVE_URL, data)


def course():
    STUDY_DATA = input('study data:')

    data_study = parse_qs(STUDY_DATA, True)
    resp_study_list = sess.post(STUDY_LIST_URL, data_study)
    resp_study_list_str = resp_study_list.content.decode()
    resp_study_list_data = json.loads(resp_study_list_str)

    for i in resp_study_list_data['studyCourseList']:
        data_process = {'courseOpenId': i['courseOpenId'], 'openClassId': i['openClassId']}
        resp_process = sess.post(PROCESS_LIST_URL, data_process)
        resp_process_str = resp_process.content.decode()
        resp_process_data = json.loads(resp_process_str)

        for i_p in resp_process_data['progress']['moduleList']:
            data_topic = {'courseOpenId': i['courseOpenId'], 'moduleId': i_p['id']}
            resp_topic = sess.post(TOPIC_LIST_URL, data_topic)
            resp_topic_str = resp_topic.content.decode()
            resp_topic_data = json.loads(resp_topic_str)
            for i_t in resp_topic_data['topicList']:
                data_cell = {'courseOpenId': i['courseOpenId'], 'openClassId': i['openClassId'],
                             'topicId': i_t['id']}
                resp_cell = sess.post(CELL_LIST_URL, data_cell)
                resp_cell_str = resp_cell.content.decode()
                resp_cell_data = json.loads(resp_cell_str)
                for i_c in resp_cell_data['cellList']:
                    for i_c_c in i_c['childNodeList']:
                        if i_c_c['stuCellFourPercent'] < 100:
                            keep_alive()

                            data_view = {
                                'courseOpenId': i['courseOpenId'],
                                'openClassId': i['openClassId'],
                                'cellId': i_c_c['Id'],
                                'flag': 's',
                                'moduleId': i_p['id']
                            }
                            resp_view = sess.post(VIEW_URL, data_view)
                            resp_view_str = resp_view.content.decode()
                            resp_view_data = json.loads(resp_view_str)
                            # print(resp_view_data)
                            res_data = json.loads(resp_view_data['resUrl'])
                            # print(res_data)

                            data_log = {
                                'courseOpenId': i['courseOpenId'],
                                'openClassId': i['openClassId'],
                                'cellId': i_c_c['Id'],
                                'cellLogId': resp_view_data['cellLogId'],
                                'picNum': res_data['args'].get('PageCount', 0),
                                'studyNewlyTime': resp_view_data.get('audioVideoLong', 0),
                                'studyNewlyPicNum': res_data['args'].get('PageCount', 0),
                                'token': resp_view_data['guIdToken']
                            }
                            # print(data_log)

                            while True:
                                if '.mp4' in i_c_c['cellName'] or '.flv' in i_c_c['cellName']:
                                    sess.post(LOG_URL, data_log)
                                    # time.sleep(resp_view_data.get('audioVideoLong', 0))
                                resp_log = sess.post(LOG_URL, data_log)
                                resp_log_str = resp_log.content.decode()
                                resp_log_data = json.loads(resp_log_str)
                                print(i_c_c['cellName'], resp_log_data)
                                if resp_log_data['code'] == 1:
                                    break
                                else:
                                    time.sleep(6)
                            time.sleep(0.5)
                            # exit()


def exam():
    KEEP_DATA = input('keep data:')
    PREVIEW_DATA = input('preview data:')

    data_keep = parse_qs(KEEP_DATA, True)
    data_preview = parse_qs(PREVIEW_DATA, True)

    r_keep = sess.post(KEEP_URL, data=data_keep)
    r_keep_str = r_keep.content.decode()
    r_keep_data = json.loads(r_keep_str)

    k_answers = {}
    for i in r_keep_data['questions']:
        answers = ','.join([str(i) for i in i['Answer']])
        if i['questionType'] == 1:  # single select
            k_answers[i['questionId']] = answers
        elif i['questionType'] == 3:  # judge
            k_answers[i['questionId']] = answers
        else:
            print('unknown question type: %s' % i['questionType'])

    r_preview = sess.post(PREVIEW_URL, data=data_preview)
    r_preview_str = r_preview.content.decode()
    r_preview_data = json.loads(r_preview_str)

    for i in r_preview_data['questionData']['questions']:
        data = {
            'online': '1',
            'studentWorkId': i['Id'],
            'answer': '',
            'examId': data_preview['examId'],
            'courseOpenId': data_preview['courseOpenId'],
        }

        if k_answers.get(i['questionId']) is not None:
            data['answer'] = k_answers[i['questionId']]

        answer_resp = sess.post(EXAM_ANSWER_URL, data=data)
        answer_data = json.loads(answer_resp.content.decode())
        print(i['Title'], answer_data)
        time.sleep(0.5)


t = input('1.homework\n2.course\n3.exam\n')
if t == '1':
    homework()
elif t == '2':
    course()
elif t == '3':
    exam()
