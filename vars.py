"""
variables for carrier_bot.py
"""
START_COMMAND = '/start'
ABOUT_COMMAND = '/about'
HELP_COMMAND = '/help'
DUMMY_DATE = '1900-01-01'

GREETING_TEXT = ("Привет, Беларус\ка Испании!\n\n"
                 "Если ты готов\а помочь в передаче мелких вещей или документов во время своей поездки домой, "
                 "или же ищешь кого-то, кто может помочь тебе - этот бот готов быть твоим инструментом.\n\n"
                 "Ты можешь сохранить приблизительные даты своей поездки и информацию о том,"
                " что ты готов\а взять с собой. Или же поискать, есть ли кто-то, кто"
                " готов взять с собой вещи\документы и едет в интересующий тебя период. \n\n"
                "Бот написан с помощью AI и продолжает находиться в разработке, "
                "список хотелок и\или жалоб можно прислать мне в телеграм: https://t.me/Fideloin\n\n"
                "ВАЖНО! Чтобы другие пользователи могли вам написать, "
                "для бота должна быть разрешена пересылка ваших сообщений. "
                "Подробности, а также информацию о приватности, "
                "исходном коде бота и хранимых данных мы можете найти использовав команду /about")
GREETING_INLINE_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "Mои поездки", "callback_data": "/getmytrips"}
            ],
            [
                {"text": "Хочу передать вещь", "callback_data": "/searchtrips"},
                {"text": "Планирую поездку", "callback_data": "/savetrip"}
            ]
        ]
}
ABOUT_TEXT = ("Бот был написал в чтобы занять руки и для помощи беларусам Малаги и окрестностей."
              "Пока что целевая аудитория - беларусы в Испании, но если будет потребность, "
              "завезу ещё и поддержку других стран.\n\n"
              "Исходный код бота можно найти по ссылке - https://github.com/Fideloin/carrier-bot . "
              "Автор приветствует комментарии\предложения и PR'ы. \n\n"
              "ВАЖНО! Ни бот, ни ищущий не имеют доступа к вашему телефону/имени/контактам/личным данным. "
              "Ваш контакт будет выдан в формате ссылки \"<a href=\"tg://user?id=123456789\">Username</a>\".\n"
              "В этом формате человеку можно написать, но никакой информации об аккаунте, кроме общедоступной, "
              "получить не получится.\n\n"
              "ВАЖНО! Чтобы ссылка выше работала, человек оставивший контакт должен "
              "разрешить пересылку своих сообщений. По дефолту эта опция включена, "
              "но если вы её меняли и забыли, то проверить можно в настройках Телеграм: "
              "\"Настройки/Конфиденциальность/Пересылка сообщений\". Там можно разрешить всем, "
              "своим контактам или никому. Удостоверьтесь, что у вас разрешена пересылка всем, "
              "либо добавьте контакт бота в список исключений. "
              "Доступа ни к каким сообщениям бот не имеет, функция нужна "
              "лишь для того, чтобы ссылка на ваше имя была кликабельной для человека, "
              "который нашёл вашу сохранённую поездку.\n\n"
              "При удалении всех поездок, удаляется также и вся хранимая информация\n\n"
              "Кратко об инфраструктуре - бот работает на AWS Lambda, база данных - AWS DynamoDB. "
              "Физический регион ресурсов - N.Virginia, US. Хранимая информация в базе - телеграм user_id, никнейм,"
              "информация о планируемой поездке (даты и примечание). Логи работы бота удаляются автоматически по "
              "прошествии 3-х дней.")
ABOUT_SECOND_MSG_TEXT = "Нажмите /start чтобы начать работу с ботом"
HELP_TEXT = ("Используйте /start чтобы начать работу с ботом\n\n"
            "Используйте /help чтобы увидеть это сообщение\n\n"
            "Используйте /about чтобы увидеть информацию об исходном боте, конфиденциальности и сохраняемых данных")
GETMYTRIPS_INLINE_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "В начало", "callback_data": f"{START_COMMAND}"}
            ]
        ]
}
SAVETRIP_STEP1_TEXT = ("Пожалуйста введите предполагаемую дату вашей поездки в Беларусь\n\n"
                      "Используйте формат DD-MM-YYYY (например: 17-03-2024)\n\n"
                      "Если поездка только из Беларуси, всё равно отправьте \"-\","
                       " чтобы ваша поездка сохранилась в базе")
SAVETRIP_STEP2_TEXT = ("И предполагаемую дату вашей поездки в Испанию\n\n"
                      "Используйте формат DD-MM-YYYY (например: 20-04-2024) \n\n"
                      "Если поездка только в Беларусь, всё равно отправьте \"-\", "
                       "чтобы ваша поездка сохранилась в базе")
SAVETRIP_STEP3_TEXT = ("Какие-нибудь заметки о том, по поводу того, с чем к вам можно обратиться? "
                      "Что вы можете взять с собой?\n\n"
                      "Например: \"Еду налегке, поэтому готов помочь с передачей любых мелких вещей\"; "
                      "\"Много вещей и напряжённый график. Могу взять только какие-нибудь документы\"\n\n"
                      "Если писать нечего, пожалуйста, всё равно отправьте \"-\", "
                       "чтобы ваша поездка сохранилась в базе")
SAVE_SUCCESS_TEXT = ("Поездка сохранена\n\n"
                    "Вы можете посмотреть свои предстоящие поездки нажав кнопку снизу")
SAVE_SUCCESS_INLINE_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "Mои поездки", "callback_data": "/getmytrips"},
                {"text": "В начало", "callback_data": f"{START_COMMAND}"}
            ]
        ]
}
INCORRECT_DATE_TEXT = ("Невалидный формат даты. Пожалуйста, "
                       "вводите дату в формате DD-MM-YYYY (например, 28-05-2024)")
INCORRECT_DATE_INLINE_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "Попробовать снова", "callback_data": "/savetrip"},
            ],
            [
                {"text": "Mои поездки", "callback_data": "/getmytrips"},
                {"text": "В начало", "callback_data": f"{START_COMMAND}"}
            ]
        ]
}

SEARCH_INTRO_TEXT = ("Давайте поищем, кто может отвезти ваши вещи. \n\n"
                    "Хотите передать вещи в Беларусь или в Испанию?")
SEARCH_INTRO_INLINE_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "В Беларусь", "callback_data": "/searchbelarusdate"},
                {"text": "В Испанию", "callback_data": "/searchspaindate"}
            ]
        ]
}
SEARCH_BELARUS_TIME_TEXT = ("Введите интересующий вас месяц для передачи "
                            "в Беларусь в формате MM-YYYY (например, 03-2024)")
SEARCH_SPAIN_TIME_TEXT = ("Введите интересующий вас месяц для передачи "
                          "в Испанию в формате MM-YYYY (например, 03-2024)")
INCORRECT_SEARCH_DATE_TEXT = ("Невалидный формат даты. Пожалуйста, "
                              "вводите дату в формате MM-YYYY (например, 03-2024)")
SEARCH_END_KEYBOARD = {
    "inline_keyboard":
        [
            [
                {"text": "Попробовать снова", "callback_data": "/searchtrips"},
                {"text": "В начало", "callback_data": f"{START_COMMAND}"}
            ]
        ]
}
GENERIC_ERROR_TEXT = ("Невозможно обработать сообщение.\n\n"
                     "К сожалению, я не ChatGPT, и не понимаю, "
                     "что именно вы имеете в виду. Пожалуйста следуйте инструкциям бота, "
                     "чтобы достичь интересующего результата.\n\n"
                     "Если не получается решить проблему - пожалуйста напишите мне в ТГ, "
                     "или откройте issue в github.\n\n"
                     "Нажмите /start чтобы начать заново")
