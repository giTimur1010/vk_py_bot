import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from toks import main_bot_token, main_user_token, DEV_ID
import datetime


# возвращает список студентов в группе
def students_init():
    students = ["students"]

    return students


#Авторизация
vk_user_session = vk_api.VkApi(token=main_user_token)
vk_bot_session = vk_api.VkApi(token=main_bot_token)
longpoll = VkLongPoll(vk_bot_session)


# дает имя человека по идентификатору
def get_name(user_ids):
    user = vk_user_session.method("users.get", {
        "user_ids": user_ids
    })

    return f"{user[0]['first_name']} {user[0]['last_name']}"

# дает людей проголосовавших в опросе по id создателя и опроса
def get_voters(owner_id, poll_id):
    poll = vk_user_session.method("polls.getById", {
        "owner_id": owner_id,
        "poll_id": poll_id
    })
    answer_ids = ''
    for answer in poll['answers']:
        answer_ids += str(answer["id"]) + ', '

    answer_ids = answer_ids[:len(answer_ids) - 1]

    voters = vk_user_session.method("polls.getVoters", {
        "owner_id": owner_id,
        "poll_id": poll_id,
        "answer_ids": answer_ids
    })

    return voters

# дает рандомное распределение людей в списке
def get_random_string(list, counter):
    random_string = ''
    while list:
        student = random.choice(list)
        list.remove(student)
        if student == "Timur Imanov":
            student += " :)"

        random_string += f"{counter}: {student}\n"
        counter += 1
    return random_string

# дает распределение на лабораторную работу по опросу с помощью id создателя и опроса
def get_laba_list(owner_id, poll_id):
    voters = get_voters(owner_id, poll_id)
    students = students_init()
    laba_list = ''
    counter = 1
    for i in range(len(voters)):
        list = []
        for voter in voters[i]['users']['items']:
            name_voter = get_name(voter)
            list.append(name_voter)
            students.remove(name_voter)


        group_count = len(list)
        laba_list += get_random_string(list, counter)
        counter += group_count
    laba_list += get_random_string(students, counter)

    return laba_list

# генерирует рандомное распределение на лабораторную работу
def get_random_list():
    students = students_init()
    str = ''
    i = 1
    while students:
        student = random.choice(students)
        str += f"{i}: {student}\n"
        students.remove(student)
        i += 1
    return str

#отправляет сообщение от бота по id
def sender(id, text):
    vk_bot_session.method("messages.send", {'user_id': id, 'message': text, 'random_id': 0})



# работа бота
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            user_id = event.user_id


            if "опрос" in msg:
                owner_id, poll_id = msg[msg.find("poll") + len("poll"):].split("_")
                sender(user_id, get_laba_list(owner_id, poll_id))
                sender(DEV_ID, str(datetime.datetime.now())[:-7] + " get_random: https://vk.com/id" + str(user_id))
            elif msg == "рандом":
                sender(user_id, get_random_list())
                sender(DEV_ID, str(datetime.datetime.now())[:-7] + " get_random: https://vk.com/id" + str(user_id) + " " + get_name(user_id))
            else:
                sender(user_id, "Некорректная Команда")
