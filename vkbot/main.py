import os
import json
import time
import redis
import requests

from vk_api import vk_api
from vk_api.keyboard import VkKeyboard
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


def build_one_button(_entrance: str, _entrances: list) -> dict:
    return {
        "action": {
            "type": "callback",
            "label": _entrance,
            "payload": json.dumps({
                "entrance": _entrance,
                "ent_slice": _entrances
            })
        }
    }


def build_many_buttons(_entrances: list) -> list:
    _buttons = []
    ent_normalized = []
    rows = (len(_entrances) - 1) // 5 + 1
    for j in range(rows):
        ent_normalized.append(_entrances[j * 5: (j + 1) * 5])
    for i_row in range(len(ent_normalized)):
        btn_arr = []
        for j_ent in range(len(ent_normalized[i_row])):
            btn_arr.append(build_one_button(ent_normalized[i_row][j_ent], _entrances))
        _buttons.append(btn_arr)
    return _buttons


while True:
    try:
        vk_session = vk_api.VkApi(token=os.getenv('VK_GROUP_TOKEN'))
        long_poll = VkBotLongPoll(vk_session, os.getenv('VK_GROUP_ID'))
        vk = vk_session.get_api()

        r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0, decode_responses=True)

        keyboard = VkKeyboard()
        keyboard.add_location_button()

        for event in long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                if event.obj.message['text'].lower() == 'начать':
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        message=open('start_message.txt', 'r', encoding='utf8').read(),
                        keyboard=keyboard.get_keyboard()
                    )
                    continue
                elif not vk.groups.isMember(group_id=os.getenv('VK_GROUP_ID'), user_id=event.obj.message['from_id']):
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        message='Нет подписки на группу',
                        keyboard=keyboard.get_keyboard()
                    )
                    continue

                response = ''
                if 'geo' in event.obj.message:
                    lat, lon = event.obj.message['geo']['coordinates'].values()
                    response = requests.get(
                        f"http://{os.getenv('DOMOFOMKA_API_HOST')}:{os.getenv('DOMOFOMKA_API_PORT')}"
                        f"/codes_geo?lat={lat}&lon={lon}")
                else:
                    response = requests.get(
                        f"http://{os.getenv('DOMOFOMKA_API_HOST')}:{os.getenv('DOMOFOMKA_API_PORT')}"
                        f"/codes_msg?message={str(event.obj.message['text'])}")
                if response.status_code != 200:
                    continue
                result = response.json()

                if not result:
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        message='Нет результатов',
                    )
                    continue

                number_of_buttons = len(result['data'].values())
                entrances = [ent for ent in result['data'].keys()]
                number_of_messages = (len(entrances) - 1) // 10 + 1

                for i in range(number_of_messages):
                    ent_slice = entrances[i * 10: (i + 1) * 10]
                    buttons = build_many_buttons(ent_slice)
                    if not r.get(f"vk:user:{event.obj.message['from_id']}:action"):
                        msg_id = vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            message=result['address'],
                            keyboard=json.dumps({
                                "inline": True,
                                "buttons": buttons
                            })
                        )
                        conversation_message_id = vk.messages.getById(
                            message_ids=msg_id
                        )['items'][0]['conversation_message_id']
                        r.set(f"vk:user:{event.obj.message['from_id']}:message:{conversation_message_id}",
                              value=str(result).replace("\'", "\""), ex=os.getenv('CACHE_EXPIRE_TIME'))

            elif event.type == VkBotEventType.MESSAGE_EVENT:

                payload = event.obj['payload']
                buttons = build_many_buttons(payload['ent_slice'])

                if r.get(f"vk:user:{event.obj.user_id}:action"):
                    n = r.ttl(f"vk:user:{event.obj.user_id}:action") + 1
                    sec_str = 'секунд' + {n % 10 == 1 and n % 100 != 11: 'у',
                                          n % 10 in [2, 3, 4] and n not in range(10, 15): 'ы'}.setdefault(1, '')
                    vk.messages.sendMessageEventAnswer(
                        event_id=event.obj.event_id,
                        user_id=event.obj.user_id,
                        peer_id=event.obj.peer_id,
                        event_data=json.dumps({
                            'type': 'show_snackbar',
                            'text': f'Подождите {n} {sec_str}!'
                        })
                    )
                else:
                    response = r.get(f"vk:user:{str(event.obj.user_id)}:message:{event.obj['conversation_message_id']}")
                    if not response:
                        msg = vk.messages.getByConversationMessageId(
                            peer_id=event.obj.peer_id,
                            conversation_message_ids=event.obj['conversation_message_id'],
                        )
                        address = msg['items'][0]['text'].split('\n')[0]
                        response = requests.get(
                            f"http://{os.getenv('DOMOFOMKA_API_HOST')}:{os.getenv('DOMOFOMKA_API_PORT')}"
                            f"/codes_msg?message={address.replace(',', '').replace(' дом ', ' ')}"
                        )
                        result = response.json()
                    else:
                        result = json.loads(str(response))

                    possible_types = ['yaeda', 'delivery', 'oldcodes']
                    codes = result['data'][payload['entrance']]
                    codes.sort(key=lambda x: possible_types.index(x[1]))

                    answer = ''
                    for code, code_type in codes:
                        if code_type.upper() not in answer:
                            answer += f"\n{code_type.upper()}:\n"
                        answer += code + ' '

                    vk.messages.edit(
                        peer_id=event.obj.peer_id,
                        conversation_message_id=event.obj['conversation_message_id'],
                        message=f"{result['address']}\nПодъезд {payload['entrance']}\n{answer}",
                        keyboard=json.dumps({
                            "inline": True,
                            "buttons": buttons
                        })
                    )

                    r.set(f'vk:user:{event.obj.user_id}:action', 'button_tap', ex=os.getenv('ANTI_SPAM_TIME'))
                    r.set(f"vk:user:{str(event.obj.user_id)}:message:{event.obj['conversation_message_id']}",
                          value=str(result).replace("\'", "\""), ex=os.getenv('CACHE_EXPIRE_TIME'))

    except requests.exceptions.ReadTimeout:
        time.sleep(3)
