
from function import *
from main import path_to_names
path_to_nonames = 'nonames.txt'
names = load_name(path_to_names)


def sorted_names(names):
    new_names = dict(sorted(names.items()))
    write_name( path_to_names, new_names)


def added_names(path_to_input):
    with open(path_to_input, 'r', encoding='utf-8') as file:
        content = file.read().splitlines()  # Уникаємо зайвих символів переносу
        unique_names = set()
        new_names = names
        for line in content:
            # Розділяємо рядок на слова і додаємо їх у множину
            unique_names.update(line.split())

        for word in unique_names:
            if word in new_names:
                continue
            else:
                value = input(f'>>>{{ {word} }} >>> ').strip()
                new_names[word] = value
        else:
            write_name( path_to_names, new_names)


if __name__ == '__main__':
    while True:
        action = input('>>> What do you want to do?\nWrite 1 for << sort >>\nWrite 2 for << added nonames >>\nELSE for << exit >>\n')
        if action == '1':
            try:
                sorted_names(names)
                colored_log(logging.INFO,'Successful sorted names!!!')
            except Exception as e:
                colored_log(logging.ERROR, e=e)
        elif action == '2':
            added_names(path_to_nonames)
            colored_log(logging.INFO, 'Names added!!!')
        else:
            break



