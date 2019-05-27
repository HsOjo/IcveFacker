import os

import requests


class IcveEdu:
    URL_V_CODE = 'https://www.icve.com.cn/portal/VerifyCode/index'
    URL_LOGIN = 'https://www.icve.com.cn/portal/Register/Login_New'
    URL_INFO = 'https://www.icve.com.cn/common/common/getJcInfo'
    URL_STU_LIST = 'https://www.icve.com.cn/studycenter/MyCourse/studingCourse'
    URL_COURSE_LIST = 'https://www.icve.com.cn/study/Directory/directoryList'
    URL_CELL_LIST = 'https://www.icve.com.cn/study/Directory/getCells'
    URL_UPDATE_STATUS = 'https://www.icve.com.cn/study/directory/updateStatus'
    URL_VIEW = 'https://www.icve.com.cn/study/directory/view'

    def __init__(self):
        self._session = requests.session()
        self._info = None  # type: dict
        self._stu_list = None  # type: dict

    def login(self, username, password):
        data = {
            'loginType': '',
            'username': username,
            'pwd': password,
            'verifycode': self.verify_code,
        }

        resp = self._session.post(IcveEdu.URL_LOGIN, data)
        return resp.status_code == 200 and self.info['IsAuth']

    @property
    def verify_code(self):
        p_img = 'vcode.jpg'

        resp = self._session.get(IcveEdu.URL_V_CODE)
        with open(p_img, 'bw') as io:
            io.write(resp.content)

        os.system('open "%s"&' % p_img)

        v_code = input('VerifyCode:')
        return v_code

    @property
    def info(self):
        if self._info is None:
            resp = self._session.post(IcveEdu.URL_INFO)
            self._info = resp.json(encoding='utf8')

        return self._info

    @property
    def stu_list(self):
        if self._stu_list is None:
            data = {
                'userid': self._info['userInfo']['Id']
            }

            resp = self._session.post(IcveEdu.URL_STU_LIST, data)
            self._stu_list = resp.json(encoding='utf8')  # type: dict
        return self._stu_list

    def get_course_list(self, course_id):
        data = {
            'courseId': course_id
        }

        resp = self._session.get(IcveEdu.URL_COURSE_LIST, params=data)
        result = resp.json(encoding='utf8')
        return result

    def get_cell_list(self, course_id):
        data = {
            'courseId': course_id
        }

        resp = self._session.get(IcveEdu.URL_CELL_LIST, params=data)
        result = resp.json(encoding='utf8')
        return result

    def update_status(self, cell_id, learn_time=0, status=1):
        data = {
            'cellId': cell_id,
            'learntime': learn_time,
            'status': status,
        }

        resp = self._session.post(IcveEdu.URL_UPDATE_STATUS, data)
        return resp.status_code == 200

    def view(self, cell_id):
        data = {
            'cellId': cell_id,
        }

        resp = self._session.post(IcveEdu.URL_VIEW, data)
        result = resp.json(encoding='utf8')
        return result


ie = IcveEdu()
if ie.login(input('username:'), input('password:')):
    print(ie.info)
    print(ie.stu_list)

    for i in ie.stu_list['list']:
        c_list = ie.get_course_list(i['id'])
        cells_info = ie.get_cell_list(i['id'])
        cells_info = {c['id']: c for c in cells_info['results']}

        for directory in c_list['directory']:
            for chapter in directory['chapter']:
                for cell in chapter['cell']:
                    if 'Id' in cell:
                        if cells_info[cell['Id']]['status'] != '1':
                            data = ie.view(cell['Id'])
                            if cell['CellType'] == 'video':
                                ie.update_status(cell['Id'], data['data']['videoLength'])
                            print(cell['Title'])
                print(chapter['chapter']['Title'])
