from function import *
import requests

path_to_account = 'accounts.json'
text_blck_list = 'Внимание! ID в черном списке агентства'

# URL для входу на сайт
logining_url = 'https://www.natashaclub.com/member.php'
base_url = 'https://www.natashaclub.com/'
send_message_url = 'https://www.natashaclub.com/compose.php?ID='
profile_url = 'https://www.natashaclub.com/profile.php?ID='
start_search = 'https://www.natashaclub.com/search_result.php?p_per_page=10&online_only=on&Sex=female&LookingFor=male&DateOfBirth_start=35&DateOfBirth_end=75&Region[]=3&Region[]=4&Region[]=7&CityST=0&City=&TrustLevel=0&Registered=0&LastOnline=0&LanguageSkills1=0&&page='
com_url = 'https://www.natashaclub.com/cc.php'
outbox_url_base = 'https://www.natashaclub.com/outbox.php'
ajax_url = 'https://www.natashaclub.com/ajax.action.php'

global payload_authorization,payload_text,settings,man_link_list
payload_authorization,payload_text = get_payload_account(path_to_account)

def cycle_man(name, limit = 10):
    count_messages_limit = 5
    count_messages = 0
    with requests.Session() as session:
        if authorization_on_account(name, session):
            colored_log(logging.INFO, f'Авторизовано на аккаунт ___{name}___')
            num_page = 1
            num_page_limit = count_pages(session)
            start = True if count_messages_limit >= 1 else False
            while start and num_page <= num_page_limit and count_messages <= count_messages_limit:
                response_page_search = session.post(f'{start_search}{num_page}')
                soup_page_search = BeautifulSoup(response_page_search.text, 'lxml')
                mans_space = soup_page_search.find('div', class_='DataDiv').find_all('table', class_='SearchRowTable')
                part_link_mans = [i.find('a')['href'] for i in mans_space]
                for part_link_man in part_link_mans:
                    try:
                        if count_messages >= count_messages_limit:
                            start = False
                            colored_log(logging.INFO, f'{count_messages} повідомлень відправлено на {name}')
                            break

                        username_man = part_link_man[1:len(part_link_man) - 5]
                        username_man = 1000274294
                        # Блок для користувача в чорному списку агенства
                        profile_url_for_send_message = f'{profile_url}{username_man}'
                        print(profile_url_for_send_message)
                        response_page_profile_sending_message = session.post(profile_url_for_send_message)
                        soup_page_profile_sending_message = BeautifulSoup(response_page_profile_sending_message.text, 'lxml')
                        div_header = soup_page_profile_sending_message.find('div', id = 'ContentDiv').text
                        if text_blck_list in div_header:
                            print(div_header)
                    except Exception as e:
                        colored_log(logging.ERROR, e=e)
                if count_messages >= count_messages_limit and start:
                    start = False
                num_page += 1

            else:
                colored_log(logging.WARNING, f'Закінчилися сторінки з аккаунтами - {num_page_limit}')
        else:
            colored_log(logging.WARNING, f'Неправильний логін або пароль для ___{name}___')

if __name__ == '__main__':
    for name in payload_authorization:
        cycle_man(name)