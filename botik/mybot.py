
import logging #imports logging for logs in json

from telegram import (    #whole library import in order to create telegram bot
    Update,  #class Update
    ReplyKeyboardMarkup, #for keyboard
)
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
# filters — filtering messages (text, photos, etc.)
# MessageHandler — processing regular messages
# ApplicationBuilder — initialization of an asynchronous Telegram bot
# CommandHandler — processing commands (e.g., /start)
# ContextTypes — context typing (access to bot, user_data, etc.)
# CallbackQueryHandler — processing clicks on inline buttons


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',       #logging
    level=logging.INFO
)



class Task:                                                            # Creating a class named Task
    def __init__(self, value=None, date=None, user_input=None):        # Constructor method with parameters that creates class objects. And any time we call the class Task, we give values for its parameters
        self.value = value                                             # Says that object value in Task gets its value from constructor parameter
        self.date = date                                               # Says that object date in Task gets its value from constructor parameter
        self.user_input = user_input                                   # Says that object user_input in Task gets its value from constructor parameter

    def __str__(self):                                                 # Special method that defines how object is converted to string (e.g., when printed)
        return f"📌 {self.value}\n📅 Untill: {self.date}\n💬 Comment: {self.user_input}" # Nicely formats the task as readable text

buttons1 = [                                                           #Here, we are creating a variable that is going to contain LIST and will be used as text for buttons
    ["Set task", "Delete task"],                                 #The buttons themselves; upper block
    ['Show tasks', 'Feature<3']                               #The buttons themselves; lower block

]                                                                      #End of the LIST
firstmenu = ReplyKeyboardMarkup(buttons1, resize_keyboard=True)        #Initializes a keyboard from buttons1; resize_keyboard=True makes buttons fit the screen


buttons2 = [                                                           #The same buttons var, but it will be shown only for returning to the main menu
    ["Main menu"]                                                   #The button itself
]
onlymainmenu = ReplyKeyboardMarkup(buttons2, resize_keyboard=True)     #Initializes a keyboard from buttons2; resize_keyboard=True makes buttons fit the screen



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):   #asynced func that will be reacting on command /start
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="img.png") #Sends an image using the bot's send_photo() method
                                                                                    #await pauses execution until the image is fully sent
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Hello, Master! I am Chungusik-chan! I am glad to serve you! I can write down your task so that you do not forget anything! And I can do not only that <3", reply_markup=firstmenu)
                                                                                     #Line above makes bot send a message
async def tasking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    step = context.user_data.get('task_step')
    if user_input == "Main menu":
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo="img.png")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Hello, Master! I am Chungusik-chan! I am glad to serve you! I can write down your task so that you do not forget anything! And I can do not only that <3",
                                       reply_markup=firstmenu)
    if user_input == "Feature<3":
        await update.message.reply_text("I love you, Master<3", reply_markup=onlymainmenu)



    if user_input == "Delete task":
        tasks = context.user_data.get('tasks', [])
        if not tasks:
            await update.message.reply_text("У вас пока нет задач, Господин.", reply_markup=firstmenu)
        else:
            task_list = "\n\n".join(f"{i + 1}. {t}" for i, t in enumerate(tasks))
            await update.message.reply_text(
                f"Your tasks:\n\n{task_list}\n\nEnter task's number that you want to delete:")
            context.user_data['task_step'] = 'delete'
        return

    if step == 'delete':
        try:
            index = int(user_input) - 1
            tasks = context.user_data.get('tasks', [])

            if 0 <= index < len(tasks):
                removed = tasks.pop(index)
                await update.message.reply_text(f"✅ Taskdeleted:\n{removed}", reply_markup=firstmenu)
            else:
                await update.message.reply_text("❌ Invalid task number, Master. Please try again.")
        except ValueError:
            await update.message.reply_text("❌ Please enter the number, Master.")

        context.user_data['task_step'] = None  # draw
        return

    if user_input == "Show tasks":
        tasks = context.user_data.get('tasks', [])
        if not tasks:
            await update.message.reply_text("You've got no tasks, Master 🫡", reply_markup=firstmenu)
        else:
            msg = "\n\n".join(f"{i + 1}. {t}" for i, t in enumerate(tasks))
            await update.message.reply_text(f"Your tasks:\n\n{msg}", reply_markup=firstmenu)
        return

    # 🟢 Step 1 — the beginning: user pressed the button
    if user_input == "Set task":
        await update.message.reply_text("Describe the task, Master!")
        context.user_data['task_step'] = 'value'
        return

    # 🟠 Step 2 - User enters description
    if step == 'value':
        context.user_data['task_value'] = user_input
        context.user_data['task_step'] = 'date'
        await update.message.reply_text("Enter the deadline for the task completion (e.g, 2025-07-15):")
        return

    # 🟡 Step 3 - User enters the date
    if step == 'date':
        context.user_data['task_date'] = user_input
        context.user_data['task_step'] = 'comment'
        await update.message.reply_text("Enter your comment or an additional description:")
        return

    # 🔵 Step 4 - Comment + task creation
    if step == 'comment':
        context.user_data['task_comment'] = user_input
        context.user_data['task_step'] = None  # Draw the state

        task = Task(
            value=context.user_data['task_value'],
            date=context.user_data['task_date'],
            user_input=context.user_data['task_comment']
        )

        # Saving task to te LIST
        if 'tasks' not in context.user_data:
            context.user_data['tasks'] = []
        context.user_data['tasks'].append(task)

        await update.message.reply_text(
            f"✅ Task created, Master!:\n\n{task}",
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

