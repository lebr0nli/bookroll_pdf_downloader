import requests
import time
import os
from bs4 import BeautifulSoup

DEBUG = False

'''start, login into brpt'''


def login_brpt(my_session):  # return already login session,login state
    print('login start......')
    user_name = input('yours 學號: ')
    user_passwd = input('yours 密碼: ')
    brpt_login_url = 'https://brpt.bookroll.org.tw/login/index.php'  # 登入頁面
    login_token_html = my_session.get(brpt_login_url)
    soup = BeautifulSoup(login_token_html.text, "html.parser")
    login_token = soup.find('input', {'name': 'logintoken'}).get('value')  # 拿login token

    my_session.post(brpt_login_url, data={'achor': '',
                                          'logintoken': login_token,
                                          'username': user_name + '@cc.ncu.edu.tw',
                                          'password': user_passwd})  # 登入brpt bookroll
    identify_name_url = 'https://brpt.bookroll.org.tw/my/'
    identify_name_html = BeautifulSoup(my_session.get(identify_name_url).text, 'html.parser')
    try:
        identify_name = identify_name_html.find('span', {'class': 'usertext mr-1'}).get_text()
        print(identify_name.replace(' ', ''), ' 你好')
        print('login successful!!')
        return my_session, True
    except AttributeError:
        print('login failure QQ')
        return my_session, False  # login False


'''go into bookroll.org and return raw_html with resource'''


def get_resource_page(my_session):  # return bookroll.org session , raw_html
    print('redirect to bookroll.org......')
    print('input your course id')
    print('e.g. https://brpt.bookroll.org.tw/course/view.php?id=407 -> course id = 407')
    course_id = input('Your course id:')
    brpt_course_url = f'https://brpt.bookroll.org.tw/course/view.php?id={course_id}'  # 課程預覽頁面
    course_initial_html = BeautifulSoup(my_session.get(brpt_course_url).text, "html.parser")
    course_name_str = course_initial_html.find('span', {'class': 'media-body font-weight-bold'}).get_text()
    if DEBUG:
        course_name_str = course_name_str + ' test'
    try:
        os.mkdir(course_name_str)  # 建立課程資料夾
        print(course_name_str + ' 檔案夾已建立')
    except FileExistsError:
        pass
    os.chdir(course_name_str)  # change working directory
    class_all_entry_html = course_initial_html.find_all('div', {'class': 'activityinstance'})

    # 取得頁面的第二個連結（教材資源），並更新連結，其實直接改為launch，跳過中間過程
    course_initial_source_url = class_all_entry_html[1].select_one('a').get('href').replace('view', 'launch')
    course_initial_source_html = BeautifulSoup(my_session.get(course_initial_source_url).text, "html.parser")
    # 製作下一步post所需的data
    resource_post_parameter_list = course_initial_source_html.find_all('input')
    resource_post_parameter_name_list = [x.get('name') for x in resource_post_parameter_list]
    resource_post_parameter_value_list = [x.get('value') for x in resource_post_parameter_list]
    resource_post_parameter_list_dict = dict(zip(resource_post_parameter_name_list, resource_post_parameter_value_list))
    # 製作結束
    main_resource_302url = course_initial_source_html.find('form').get('action')  # 獲取連結
    main_resource_response = my_session.post(main_resource_302url, resource_post_parameter_list_dict)  # get good_url
    main_resource_url = main_resource_response.history[-1].url.replace('&secondId=', '!').split('!')[0]  # get good_url
    main_resource_response = my_session.post(main_resource_url, resource_post_parameter_list_dict)  # 獲取上課資源
    main_resource_html = main_resource_response.text
    main_resource_html = BeautifulSoup(main_resource_html, "html.parser")
    xcsrf_token = main_resource_html.find('meta', {'id': '_csrf'}).get('content')  # prepared xcsrf to down pdf
    if DEBUG:
        print('xcsrf_token: ', xcsrf_token)
    my_session.headers.update({'X-CSRF-TOKEN': xcsrf_token})
    print('redirect complete......')
    return my_session, main_resource_html


'''get what to download'''


def get_pdf_url(my_session, process_html):  # return update session, download dict
    print('now parsing directory of resource..........')
    all_resource_directory_url = [x.get('href') for x in process_html.find_all('a', {'class': 'directory_close'})]
    all_resource_directory_name = [x.get_text() for x in process_html.find_all('a', {'class': 'directory_close'})]
    all_resource_directory_dict = dict(zip(all_resource_directory_name, all_resource_directory_url))
    bookroll_home_page = 'https://bookroll.org.tw'
    download_target = {}
    for download_directory_name in all_resource_directory_name:
        open_directory_html = BeautifulSoup(
            my_session.get(bookroll_home_page + all_resource_directory_dict[download_directory_name]).text,
            'html.parser')
        content_resource_html = open_directory_html.find_all('a', {'class': 'directory_open'})[1].find_parent('li')
        content_resource_dict_html = content_resource_html.find_all('li', {'class': 'contents'})  # 尚未處理
        content_resource_name = [x.find('a').get_text() for x in content_resource_dict_html]
        content_resource_url = [x.find('a').get('href').split('=')[1] for x in content_resource_dict_html]
        content_resource_dict = dict(zip(content_resource_name, content_resource_url))
        download_target.update({download_directory_name: content_resource_dict})
    print('parsing done!!!')
    return my_session, download_target


'''Choose Download Target'''


def choose_download(my_session, all_download_queue):  # start your download
    print()
    print('可下載目錄：')
    for choose_number, choose_name in enumerate(all_download_queue.keys()):
        print(choose_number, choose_name)
    print()
    print('輸入想要下載的目錄編號，或是輸入不想下載的目錄編號加上負號，以空格分隔，全部下載請輸入all')
    print('sample input: 0 5 6')
    print('sample input: -0 -5 -6')
    print('sample input: all')
    user_prefer = input('Your input: ')
    if user_prefer == 'all':
        print('download all pdf......')
        for target_directory_name, target_content_list in all_download_queue.items():
            print('download directory: ' + target_directory_name)
            for target_content_name, target_content_url in target_content_list.items():
                if DEBUG:
                    print('target_content_url: ', target_content_url)
                print('download file: ' + target_content_name)
                down_pdf(my_session, target_directory_name, target_content_name, target_content_url)
    else:
        if '-' in user_prefer:
            user_choose_list = user_prefer.replace('-', '').split()
            user_choose_list = [abs(int(x)) for x in user_choose_list]
            all_download_queue_directory = list(all_download_queue.keys())
            for del_index in sorted(user_choose_list, reverse=True):
                del all_download_queue_directory[del_index]  # 移除不想下載的目錄
        else:
            user_choose_list = user_prefer.split()
            user_choose_list = [int(x) for x in user_choose_list]
            all_download_queue_directory = [list(all_download_queue.keys())[x] for x in user_choose_list]
        for target_directory_name in all_download_queue_directory:  # download by directory and file_name
            print('download directory: ' + target_directory_name)
            target_content_list = all_download_queue[target_directory_name]
            for target_content_name, target_content_url in target_content_list.items():
                if DEBUG:
                    print('target_content_url: ', target_content_url)
                print('download file: ' + target_content_name)
                down_pdf(my_session, target_directory_name, target_content_name, target_content_url)


'''Download pdf'''


def down_pdf(my_session, file_path, file_name, file_url):  # download method
    get_pdf_url_list = ['https://bookroll.org.tw/book/pdfoutput', 'https://bookroll.org.tw/book/pdfoutputdata']
    temp_file = my_session.post(get_pdf_url_list[0], data={'viewerUrl': file_url}).text[5:-2]
    if DEBUG:
        print('temp_file: ', temp_file)
    pdf_create_success = False
    while not pdf_create_success:
        pdf_file = my_session.post(get_pdf_url_list[1], data={'tmpFile': temp_file}).content
        if len(pdf_file) == 0:
            print('loading...')
            time.sleep(2)
        else:
            print('download success')
            try:
                os.mkdir(file_path)
                print(file_path + '檔案夾已建立')
            except FileExistsError:
                pass
            with open(file_path + '/' + file_name + '.pdf', 'wb') as f:
                f.write(pdf_file)
                f.close()
            pdf_create_success = True


def main():
    main_session = requests.session()
    main_session, login_complete = login_brpt(main_session)  # update session and login
    if login_complete:
        main_session, raw_html = get_resource_page(main_session)  # update session and get raw html with resource
        main_session, all_download_queue = get_pdf_url(main_session,
                                                       raw_html)  # update session and get what to download
        choose_download(main_session, all_download_queue)  # start download
        os.chdir('..')  # back to default('/微積分/..')


if __name__ == '__main__':
    main()
