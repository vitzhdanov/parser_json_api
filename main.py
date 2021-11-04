import os

import requests

from datetime import datetime


def get_users_tasks():
    try:
        get_tasks = requests.get('https://json.medrating.org/todos').json()
        get_users = requests.get('https://json.medrating.org/users').json()
        # Создаём директорию, если не создана
        if not os.path.exists('tasks'):
            os.mkdir('tasks')
        # Получаем id всех пользователей
        users_id = [x['id'] for x in get_users]
        # Создаём лист словарей пользователей и прикрепленных к нему задач
        users_tasks = []
        for num in users_id:
            users_tasks.append(
                {
                    'user': get_users[num-1],
                    'tasks': []
                }
            )
        for i in get_tasks:
            try:
                for o in users_id:
                    if i['userId'] == o:
                        users_tasks[o-1]['tasks'].append(i)
            except KeyError:
                pass
        # Вызываем функцию для проверки устаревших отчетов
        return check_path(users_tasks)
    except Exception as ex:
        print(f"[INFO] {ex}")


def check_path(users_tasks):
    t = []
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    for user in users_tasks:
        # Если файл с именем пользователя существует, переименовываем его и вызываем функцию для записи
        if os.path.exists(f"tasks/{user['user']['username']}.txt"):
            os.renames(f"tasks/{user['user']['username']}.txt", f"tasks/old_{user['user']['username']}_{now}.txt")
            t.append(result(user))
        else:
            # В проивном случае вызываем функцию для записи
            t.append(result(user))


def result(user):
    # Создаём файл с именем пользовател и записываем необходимые данные
    with open(f"tasks/{user['user']['username']}.txt", "w") as file:
        try:
            file.write(
                f"Отчет для {user['user']['name']}.\n"
                f"{user['user']['username']} <{user['user']['email']}> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"Всего задач: {len(user['tasks'])}\n\n"
            )
            # Создаём списки завершенных и оставшихся задач
            false_tasks = []
            true_tasks = []

            # Если список задач пуст, ничего не делаем
            if len(user['tasks']) == 0:
                pass
            # Сортируем задачи
            for t in user['tasks']:
                if not t['completed']:
                    false_tasks.append(t)
                else:
                    true_tasks.append(t)
            # Записываем завершенные и оставшиеся задачи
            file.write(f"Завершенные задачи ({len(true_tasks)}):\n")
            for t in true_tasks:
                file.write(f"{t['title'][0:48]}\n")
            file.write(f"\nОставшиеся задачи ({len(false_tasks)}):\n")
            for f in false_tasks:
                file.write(f"{f['title'][0:48]}\n")
            file.flush()
        except Exception as ex:
            file.close()
            print(f"[INFO] {ex}")


if __name__ == '__main__':
    get_users_tasks()
