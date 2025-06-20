import requests

from tqdm import tqdm
from function import *

path_file_txt = 'link.txt'
path_file_xlsx = 'list.xlsx'
path_to_account = 'accounts.json'
path_to_names = 'names.json'
path_to_nonames = 'nonames.txt'
path_to_settings = 'settings.json'


payload_authorization = {}
payload_text = {}
audit_page = []
man_link_list=[]


# URL для входу на сайт
logining_url = 'https://www.natashaclub.com/member.php'
base_url = 'https://www.natashaclub.com/'
send_message_url = 'https://www.natashaclub.com/compose.php?ID='
start_search = 'https://www.natashaclub.com/search_result.php?p_per_page=10&online_only=on&Sex=female&LookingFor=male&DateOfBirth_start=35&DateOfBirth_end=75&Region[]=3&Region[]=4&Region[]=7&CityST=0&City=&TrustLevel=0&Registered=0&LastOnline=0&LanguageSkills1=0&&page='
com_url = 'https://www.natashaclub.com/cc.php'
outbox_url_base = 'https://www.natashaclub.com/outbox.php'
ajax_url = 'https://www.natashaclub.com/ajax.action.php'
profile_url = 'https://www.natashaclub.com/profile.php?ID='


search_payload = {
    'DateOfBirth_start': ['35'],
    'DateOfBirth_end': ['85'],
    'Region[]': ['2', '3', '4', '5', '6', '7', '8'],  # Вибір декількох регіонів
    'online_only': 'on',  # Замість checkbox_name використовуйте відповідне значення
    # додаткові поля форми, якщо потрібно
}
cookies = {
    'Language': 'English',
    'memberT': 'yYL5Ayj4dIFRYOMuTjMkvsTv2ad50rvoMLtsAM3W4HSITOuh',
}

headers = {
    'accept': 'text/html, */*; q=0.01',
    'accept-language': 'uk,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': 'Language=English; memberT=yYL5Ayj4dIFRYOMuTjMkvsTv2ad50rvoMLtsAM3W4HSITOuh',
    'origin': 'https://www.natashaclub.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.natashaclub.com/cc.php',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'x-requested-with': 'XMLHttpRequest',
}
data = {
    'ajaxaction': 'cc.ShowHide',
    'what': 'ShowWasPPPed',
}

text_like_response = ['Sorry, a virtual smile has not been sent.You already sent a smile to this person',
             'Virtual smile has been successfully sent.', 'Sorry, but you\'ve reached your limit for today.']
text_message_response = ['Sorry, but you\'ve reached your limit for today.', 'You can write only 1 first letter',
                'You can contact anyone. Send a message to:']
text_request = {
    'text': '',  # Текст повідомлення
    'SEND_MESSAGE': 'YES',
    'sendto': 'both'
    # Параметр, який позначає, що потрібно надіслати повідомлення
}

ignore_list = [
    '/1000037247.html'
]
start_words = ['Dear','Honey','Darling']
ban_test_list = ['master', 'system administrator',' test']
text_blck_list = 'Внимание! ID в черном списке агентства'

# Завантаження БД імен
names = load_name(path_to_names)


def send_like(name):
    try:
        with requests.Session() as session:
            if authorization_on_account(name,session):
                colored_log(logging.INFO,f'Авторизовано на аккаунт ___{name}___')
                num_page = 1
                num_page_limit = count_pages(session)
                start = True
                # Ініціалізуємо прогрес-бар з tqdm
                with tqdm(range(100), desc="Processing", unit="item") as pbar:
                    for i in data:
                        while start and num_page<=num_page_limit:
                            response_page_search = session.post(f'{start_search}{num_page}')
                            soup_page_search = BeautifulSoup(response_page_search.text,'lxml')

                            href_a_with_likes = soup_page_search.find_all('a', href = True)
                            likes_url = [like['href'] for like in href_a_with_likes if like['href'].startswith('vkiss.php?sendto=')]
                            for like_url in likes_url:
                                if write_me(session,like_url[like_url.index('=')+1:]):
                                    # Блок для користувача в чорному списку агенства
                                    profile_url_for_send_message = f'{profile_url}{like_url[like_url.index('=')+1:]}'
                                    response_page_profile_sending_message = session.post(profile_url_for_send_message)
                                    soup_page_profile_sending_message = BeautifulSoup(
                                        response_page_profile_sending_message.text, 'lxml')
                                    div_header = soup_page_profile_sending_message.find('div', id='ContentDiv').text
                                    if text_blck_list in div_header:
                                        # print(f'{text_blck_list} === {profile_url_for_send_message}')
                                        continue
                                    response_send_like = session.post(f'{base_url}{like_url}')
                                    soup_send_like = BeautifulSoup(response_send_like.text, 'lxml')
                                    status_send_like = soup_send_like.find('div', id = 'ContentDiv').text
                                    # limit
                                    if text_like_response[2] in status_send_like:
                                        colored_log(logging.DEBUG, f'Лайки на {name} відправлені')
                                        start = False
                                        break
                                    # sent twice
                                    elif text_like_response[0] in status_send_like:
                                        continue
                                    # sent successful
                                    elif text_like_response[1] in status_send_like:
                                        pbar.update(1)
                                        continue
                                else:
                                    continue
                            else:
                                num_page+=1

            else:
                colored_log(logging.WARNING, f'Неправильний логін або пароль для ___{name}___')
    except Exception as e:
        colored_log(logging.ERROR, e=e)

def send_mutual_like(name):
    try:
        with requests.Session() as session:
            if authorization_on_account(name, session):
                colored_log(logging.INFO, f'Авторизовано на аккаунт ___{name}___')
                cookies = session.cookies.get_dict()
                response_mutual = requests.post(ajax_url, cookies=cookies,headers=headers, data=data)
                soup = BeautifulSoup(response_mutual.text, 'lxml')
                link_like_all = soup.find_all('a', string='grant access')
                for link in link_like_all:
                    res = session.post(url=base_url + link['href'])
                    if res.status_code == 200:
                        print('Grant Access')
                else:
                    colored_log(logging.DEBUG, f'Взаємні лайки на {name} відправлені')
            else:
                colored_log(logging.WARNING, f'Неправильний логін або пароль для ___{name}___')
    except Exception as e:
        colored_log(logging.ERROR, e=e)


def send_message_standart(name, limit = None):
    while True:
        try:
            if settings['is_limit'] and not limit:
                count_messages_limit = settings['limit_message']
                print(count_messages_limit)
                break
            else:
                count_messages_limit = int(input(f'Write limit for _{name}_\n'))
                break
        except:
            colored_log(logging.WARNING, f'NUMBER, NOT STRING')
    try:
        count_messages = 0
        with requests.Session() as session:
            start = True if count_messages_limit >= 1 else False

            if start:
                if authorization_on_account(name, session):
                    colored_log(logging.INFO, f'Авторизовано на аккаунт ___{name}___')
                    num_page = 1
                    num_page_limit = count_pages(session)
                    start = True if count_messages_limit>=1 else False
                    while start and num_page <= num_page_limit and count_messages<=count_messages_limit:
                        response_page_search = session.post(f'{start_search}{num_page}')
                        soup_page_search = BeautifulSoup(response_page_search.text, 'lxml')
                        mans_space = soup_page_search.find('div', class_ ='DataDiv').find_all('table', class_ = 'SearchRowTable')
                        part_link_mans = [i.find('a')['href'] for i in mans_space]
                        for part_link_man in part_link_mans:
                            try:
                                if count_messages >= count_messages_limit:
                                    start = False
                                    colored_log(logging.INFO, f'{count_messages} повідомлень відправлено на {name}')
                                    break
                                username_man = part_link_man[1:len(part_link_man)-5]
                                if write_me(session,username_man):
                                    # Блок для користувача в чорному списку агенства
                                    profile_url_for_send_message = f'{profile_url}{username_man}'
                                    response_page_profile_sending_message = session.post(profile_url_for_send_message)
                                    soup_page_profile_sending_message = BeautifulSoup(
                                        response_page_profile_sending_message.text, 'lxml')
                                    div_header = soup_page_profile_sending_message.find('div', id='ContentDiv').text
                                    if text_blck_list in div_header:
                                        # print(f'{text_blck_list} === {profile_url_for_send_message}')
                                        continue
                                    url_for_send_message = f'{send_message_url}{username_man}'
                                    response_page_sending_message = session.post(url_for_send_message)
                                    soup_page_sending_message = BeautifulSoup(response_page_sending_message.text,'lxml')
                                    status_send_message = soup_page_sending_message.find('td', class_='text').text
                                    if text_message_response[0] in status_send_message:
                                        colored_log(logging.WARNING, f'Ліміт повідомлень на {name}')
                                        start = False
                                        break
                                    elif text_message_response[1] in status_send_message:
                                        continue
                                    elif text_message_response[2] in status_send_message:
                                        response_get_man_info = session.post(base_url + username_man)
                                        soup_get_man_info = BeautifulSoup(response_get_man_info.text, 'lxml')
                                        header_man = soup_get_man_info.find(class_='ContentHeaders').find('span').text
                                        try:

                                            colored_log(logging.WARN,'---------------------------------------------------------------------------')
                                            if ': To be added...' in header_man.strip():
                                                start_message = random.choice(start_words)
                                                text_request['text'] = get_text(start_message,payload_text[name])
                                                action = session.post(url_for_send_message, data=text_request)
                                                count_messages += 1
                                                colored_log(logging.INFO, f'{count_messages}-e повідомлення відправлене, status - {action.status_code}')
                                            else:
                                                print(header_man)
                                                start_message = get_start_message(header_man,names, settings['skip_send'])
                                                if start_message == 'skip':
                                                    with open(path_to_nonames, 'a+', encoding='utf-8') as f:
                                                        f.write(f'{header_man[:header_man.index(':')].strip().lower()}||| {header_man}')
                                                    # print(f'{header_man}\n')
                                                else:
                                                    # print(start_message)
                                                    text_request['text'] = get_text(start_message,payload_text[name])
                                                    print(text_request['text'][:20])
                                                    action = session.post(url_for_send_message, data=text_request)
                                                    count_messages+=1
                                                    colored_log(logging.INFO, f'{count_messages}-e повідомлення відправлене, status - {action.status_code}')
                                        except Exception as e:
                                            colored_log(logging.ERROR, e=e)
                            except Exception as e:
                                colored_log(logging.ERROR, e=e)
                        if count_messages >= count_messages_limit and start:
                            start = False
                        num_page+=1
                        new_names = load_name(path_to_names)
                        if names != new_names:
                            write_name(path_to_names, names)
                    else:
                        colored_log(logging.WARNING, f'Закінчилися сторінки з аккаунтами - {num_page_limit}')
                else:
                    colored_log(logging.WARNING, f'Неправильний логін або пароль для ___{name}___')
        colored_log(logging.INFO, f'{count_messages} повідомлень відправлено на {name}')

    except Exception as e:
        colored_log(logging.ERROR, e=e)

def send_message_on_link_xlsx(name,limit = None):
    global man_link_list
    while True:
        try:
            if settings['is_limit'] and not limit:
                count_messages_limit = settings['limit_message']
                print(count_messages_limit)
                break
            else:
                count_messages_limit = int(input(f'Write limit for _{name}_\n'))
                break
        except:
            colored_log(logging.WARNING, f'NUMBER, NOT STRING')
    try:
        with requests.Session() as session:
            count_messages = 0
            start = True if count_messages_limit >= 1 else False
            if authorization_on_account(name, session):
                colored_log(logging.INFO, f'Авторизовано на аккаунт ___{name}___')
                for man_link in man_link_list:
                    if count_messages >= count_messages_limit:
                        start = False
                        colored_log(logging.INFO, f'{count_messages} повідомлень відправлено на {name}')
                        break
                    man_id = man_link.replace('https://www.natashaclub.com/profile.php?ID=','')
                    if write_me(session, man_id):
                        # Блок для користувача в чорному списку агенства
                        profile_url_for_send_message = f'{profile_url}{man_id}'
                        response_page_profile_sending_message = session.post(profile_url_for_send_message)
                        soup_page_profile_sending_message = BeautifulSoup(
                            response_page_profile_sending_message.text, 'lxml')
                        div_header = soup_page_profile_sending_message.find('div', id='ContentDiv').text
                        if text_blck_list in div_header:
                            # print(f'{text_blck_list} === {profile_url_for_send_message}')
                            continue
                        response_get_man_info = session.post(man_link)
                        soup_get_man_info = BeautifulSoup(response_get_man_info.text, 'lxml')
                        header_man = soup_get_man_info.find(class_='ContentHeaders').find('span').text
                        for part in ban_test_list:
                            if part in header_man:
                                colored_log(logging.INFO,
                                            f'Сторінка адміністратора сйту{response_get_man_info}')
                                continue

                        try:
                            colored_log(logging.WARN,'---------------------------------------------------------------------------')
                            if ': To be added...' in header_man.strip():
                                start_message = random.choice(start_words)
                                text_request['text'] = get_text(start_message, payload_text[name])
                                action = session.post(f'{send_message_url}{man_id}', data=text_request)
                                # print(text_request['text'][:40])
                                count_messages += 1
                                colored_log(logging.INFO,f'{count_messages}-e повідомлення відправлене, status - {action.status_code}')
                            else:
                                print(header_man)
                                start_message = get_start_message(header_man, names, settings['skip_send'])

                                if start_message == 'skip':
                                    with open(path_to_nonames, 'a+', encoding='utf-8') as f:
                                        f.write(f'{header_man[:header_man.index(':')].strip().lower()}||| {header_man}')
                                    # print(f'{header_man}\n')
                                else:
                                    # print(start_message)
                                    text_request['text'] = get_text(start_message, payload_text[name])
                                    print(text_request['text'][:20])
                                    action = session.post(f'{send_message_url}{man_id}', data=text_request)
                                    # print(text_request['text'][:40])
                                    count_messages += 1
                                    colored_log(logging.INFO,f'{count_messages}-e повідомлення відправлене, status - {action.status_code}')
                            s = BeautifulSoup(action.text,'lxml')
                            # write_html(s)
                            # print('man_id',man_id)
                            # print(f'{send_message_url}{man_id}')
                        except Exception as e:
                            colored_log(logging.ERROR, e=e)
            else:
                colored_log(logging.WARNING, f'Неправильний логін або пароль для ___{name}___')
            if count_messages >= count_messages_limit and start:
                colored_log(logging.INFO, f'{count_messages} повідомлень відправлено на {name}')
                start = False
            new_names = load_name(path_to_names)
            if names != new_names:
                write_name(path_to_names, names)

    except Exception as e:
            colored_log(logging.ERROR, e=e)



def main():
    global payload_authorization,payload_text,settings,man_link_list
    payload_authorization,payload_text = get_payload_account(path_to_account)
    settings = load_settings(path_to_settings)
    s = True
    while s:
        colored_log(logging.WARN, '---------------------------------------------------------------------------')
        command= input('Write __l__ for LIKE or __mm__ for MESSAGE or __xx__ MESSAGE on LIST/TABLE or __mix__ MESSAGE on ONE ACCAUNT\n>>>').strip().lower()
        # command= 'xx'
        if command =='l':
            for name in payload_authorization:
                send_like(name)
                send_mutual_like(name)
        elif command =='mm':
            for name in payload_authorization:
                send_message_standart(name)

        elif command == 'xx':
            man_link_list = load_man_link(path_file_xlsx)
            for name in payload_authorization:
                send_message_on_link_xlsx(name)
        elif command == 'mix':
            num = 0
            num_name_list = {}
            for name in payload_authorization:
                print(f'{num} - {name}')
                num_name_list[num] = name
                num+=1
            accaunt = int(input('Виберіть акаунт'))
            msg = input(f'__mm__ for MESSAGE or __xx__ MESSAGE on LIST/TABLE')
            if msg =='mm':
                send_message_standart(num_name_list[accaunt],True)
            elif msg == 'xx':
                man_link_list = load_man_link(path_file_xlsx)
                send_message_on_link_xlsx(num_name_list[accaunt],True)
        else:
            break



if __name__ == '__main__':
    main()
