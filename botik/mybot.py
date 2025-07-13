import asyncio #module import
import logging #imports logging for logs in json

from sqlalchemy import update #module import


from telegram import (    #whole library import in order to create telegram bot
    Update,  #class Update
    ReplyKeyboardMarkup, #for keyboard
    InlineKeyboardMarkup, #unused
    InlineKeyboardButton  #unused
)
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
# filters — фильтрация сообщений (текст, фото, и т.д.)
# MessageHandler — обработка обычных сообщений
# ApplicationBuilder — инициализация асинхронного Telegram-бота
# CommandHandler — обработка команд (например, /start)
# ContextTypes — типизация контекста (доступ к bot, user_data и др.)
# CallbackQueryHandler — обработка нажатий на inline-кнопки


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



class Task:                                                            # Creating a class named Task
    def __init__(self, value=None, date=None, user_input=None):        # Constructor method with parameters that creates class objects. And any time we call the class Task, we give values for its parameters
        self.value = value                                             # Says that object value in Task gets its value from constructor parameter
        self.date = date                                               # Says that object date in Task gets its value from constructor parameter
        self.user_input = user_input                                   # Says that object user_input in Task gets its value from constructor parameter

    def __str__(self):                                                 # Special method that defines how object is converted to string (e.g., when printed)
        return f"📌 {self.value}\n📅 До: {self.date}\n💬 Комментарий: {self.user_input}" # Nicely formats the task as readable text

buttons1 = [                                                           #Here, we are creating a variable that is going to contain LIST and will be used as text for buttons
    ["Дать задачу", "Удалить задачу"],                                 #The buttons themselves; upper block
    ['Просмотреть задачи', 'Прикольчик']                               #The buttons themselves; lower block

]                                                                      #End of the LIST
firstmenu = ReplyKeyboardMarkup(buttons1, resize_keyboard=True)        #Initializes a keyboard from buttons1; resize_keyboard=True makes buttons fit the screen


buttons2 = [                                                           #The same buttons var, but it will be shown only for returning to the main menu
    ["Главное меню"]                                                   #The button itself
]
onlymainmenu = ReplyKeyboardMarkup(buttons2, resize_keyboard=True)     #Initializes a keyboard from buttons2; resize_keyboard=True makes buttons fit the screen



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):   #asynced func that will be reacting on command /start
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="img.png") #Sends an image using the bot's send_photo() method
                                                                                    #await pauses execution until the image is fully sent
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Здравствуйте, Господин! Я - Чунгусик-тян! Рада вам служить! Пока что я могу только Вас кривлять, Господин. Напишите мне что угодно и я это скажу!", reply_markup=firstmenu)
                                                                                     #Line above makes bot send a message
async def tasking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    step = context.user_data.get('task_step')
    if user_input == "Главное меню":
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo="img.png")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Здравствуйте, Господин! Я - Чунгусик-тян! Рада вам служить! Я могу записывать ваши задачаи, что бы вы ничего не забыли! Да и не только это могу <3",
                                       reply_markup=firstmenu)
    if user_input == "Прикольчик":
        await update.message.reply_text("Я люблю вас, Господин", reply_markup=onlymainmenu)



    if user_input == "Удалить задачу":
        tasks = context.user_data.get('tasks', [])
        if not tasks:
            await update.message.reply_text("У вас пока нет задач, Господин.", reply_markup=firstmenu)
        else:
            task_list = "\n\n".join(f"{i + 1}. {t}" for i, t in enumerate(tasks))
            await update.message.reply_text(
                f"Ваши задачи:\n\n{task_list}\n\nВведите номер задачи, которую хотите удалить:")
            context.user_data['task_step'] = 'delete'
        return

    if step == 'delete':
        try:
            index = int(user_input) - 1
            tasks = context.user_data.get('tasks', [])

            if 0 <= index < len(tasks):
                removed = tasks.pop(index)
                await update.message.reply_text(f"✅ Удалена задача:\n{removed}", reply_markup=firstmenu)
            else:
                await update.message.reply_text("❌ Неверный номер задачи, Господин. Попробуйте снова.")
        except ValueError:
            await update.message.reply_text("❌ Введите, пожалуйста, номер — число, Господин.")

        context.user_data['task_step'] = None  # сброс
        return

    if user_input == "Просмотреть задачи":
        tasks = context.user_data.get('tasks', [])
        if not tasks:
            await update.message.reply_text("У вас пока нет задач, Господин 🫡", reply_markup=firstmenu)
        else:
            msg = "\n\n".join(f"{i + 1}. {t}" for i, t in enumerate(tasks))
            await update.message.reply_text(f"Ваши задачи:\n\n{msg}", reply_markup=firstmenu)
        return

    # 🟢 Шаг 1 — начало: пользователь нажал кнопку
    if user_input == "Дать задачу":
        await update.message.reply_text("Опишите задачку, Господин!")
        context.user_data['task_step'] = 'value'
        return

    # 🟠 Шаг 2 — пользователь вводит описание
    if step == 'value':
        context.user_data['task_value'] = user_input
        context.user_data['task_step'] = 'date'
        await update.message.reply_text("Введите срок выполнения задачи (например, 2025-07-15):")
        return

    # 🟡 Шаг 3 — пользователь вводит дату
    if step == 'date':
        context.user_data['task_date'] = user_input
        context.user_data['task_step'] = 'comment'
        await update.message.reply_text("Теперь введите комментарий или дополнительную информацию:")
        return

    # 🔵 Шаг 4 — комментарий + создание задачи
    if step == 'comment':
        context.user_data['task_comment'] = user_input
        context.user_data['task_step'] = None  # Сброс состояния

        task = Task(
            value=context.user_data['task_value'],
            date=context.user_data['task_date'],
            user_input=context.user_data['task_comment']
        )

        # Сохраняем задачу в список
        if 'tasks' not in context.user_data:
            context.user_data['tasks'] = []
        context.user_data['tasks'].append(task)

        await update.message.reply_text(
            f"✅ Задача создана, Господин:\n\n{task}",
            reply_markup=firstmenu
        )
        return


if __name__ == '__main__':
    application = ApplicationBuilder().token('8050992129:AAHavgyM320ilerfmo3LOkc2wkmNy3hBwTM').build()
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    tasking_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), tasking)
    application.add_handler(tasking_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    # application.add_handler(echo_handler)

    application.run_polling()

