import sqlite3
import logging
from time import time
from functools import wraps
from telegram.parsemode import ParseMode
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, callbackqueryhandler
import config as config

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.master_id:
            print("Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text('Unauthorized Access Denied')
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi {},\nWelcome to the official feature request bot for the project [{}]({}). To request any feature, either reply the request with /request or just type /request followed by your request. If you want to know what else I can do, hit /help".format(update.effective_user.first_name, config.PROJECT_NAME, config.PROJECT_URL), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def myinfo(update, context):
    user_id = update.message.from_user.id
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()
    d.execute('SELECT * FROM requests WHERE userid LIKE {}'.format(user_id))
    data = d.fetchall()
    conn.commit()
    conn.close()
    
    if update.message.from_user.username != None:
        update.message.reply_text('Name: {} {}\nUsername: @{}\nUser ID: {}\nTotal Requests: {}'.format(update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username, user_id, len(data)))
    else:
        update.message.reply_text('Name: {} {}\nUser ID: {}\nTotal Requests: {}'.format(update.message.from_user.first_name, update.message.from_user.last_name, user_id, len(data)))

def check_request(update, context):
    pass

def status(update, contex):
    update.message.reply_text("Ya, I'm here :)")

@restricted
def kick(update, context):
    try:
        if (update.message.reply_to_message != None):
            update.effective_chat.kick_member(update.message.reply_to_message.from_user.id)
            update.message.reply_text('User Kicked')
        else:
            update.message.reply_text('Failed to find any user to kick')
    except Exception as e:
        update.message.reply_text("{}".format(e))

@restricted
def mute(update, context):
    try:
        if (update.message.reply_to_message != None):
            update.effective_chat.restrict_member(update.message.chat.id, update.message.reply_to_message.from_user.id, until_date=time()+3600)
            update.message.reply_text('User Muted for 1hr')
        else:
            update.message.reply_text('Failed to find any user to kick')
    except Exception as e:
        update.message.reply_text("{}".format(e))

def show_faqs(update, context):
    update.message.reply_text('You can have a look at the FAQs here: {}'.format(config.FAQ_URL), disable_web_page_preview=True)

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I will help you to request any feature or report issue regarding the project {}\nThese commands may help you:\n/request - Make your Request!\n/myinfo - Shows your info\n/myrequests - Shows your requests\n/allrequests - Shows all requests (Admin Only)\n/pendingrequests - Shows no of pending requests\n\nIf you have any trouble contact admin: @{}".format(config.PROJECT_NAME, config.master_username))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Made with ♥ by Ankit Sangwan")

## join group

def show_requests_count(update, context):
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()
    d.execute('SELECT * FROM requests')
    data = d.fetchall()
    conn.commit()
    conn.close()
    if len(data) == 0:
        update.message.reply_text(text='No Requests Pending :)')
    else:
        update.message.reply_text(text='There are {} pending requests'.format(len(data)))


@restricted
def show_requests(update, context):
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()
    d.execute('SELECT * FROM requests')
    data = d.fetchall()
    conn.commit()
    conn.close()
    if len(data) == 0:
        update.message.reply_text(text='No Pending Requests :)')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='List of Requests:')
            
        list_of_commands = ['Delete Request']
        buttons_list = []
        for i in list_of_commands:
            buttons_list.append(InlineKeyboardButton(text=i, callback_data = i))
        reply_markup = InlineKeyboardMarkup([buttons_list])
        for res in data:
            context.bot.send_message(chat_id=update.effective_chat.id, text=res, reply_markup=reply_markup)

def check_admin_pass(update, context):
    pass

def show_my_requests(update, context):
    user_id = update.message.from_user.id
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()
    d.execute('SELECT * FROM requests WHERE userid LIKE {}'.format(user_id))
    data = d.fetchall()
    conn.commit()
    conn.close()
    if len(data) == 0:
        update.message.reply_text(text="No Requests Found")
    else:
        update.message.reply_text(text="Here's a list of your requests:")
        for res in data:
            temp = res[17]
            status = ''
            if temp == 1:
                status = '🟡 Pending'
            if temp == 2:
                status = '🟢 Accepted'
            if temp == 3:
                status = '🔴 Rejected'
            if temp == 4:
                status = '🔵 On Progress'
            if temp == 5:
                status = '🟢 Completed'
            if temp == 0:
                status = '🔴 Deleted'
            context.bot.send_message(chat_id=update.effective_chat.id, text='{}: "{}"\nStatus: {}'.format(res[0].split(' ')[0], res[14], status))

def add_request(update, context):
    try:
        if (update.message.reply_to_message != None):
            date = update.message.reply_to_message.date

            userid = update.message.reply_to_message.from_user.id
            replyuserid = update.message.from_user.id

            first_name = update.message.reply_to_message.from_user.first_name
            last_name = update.message.reply_to_message.from_user.last_name
            replyfirst_name = update.message.from_user.first_name
            replylast_name = update.message.from_user.last_name

            username = update.message.reply_to_message.from_user.username
            replyusername = update.message.from_user.username

            chatid = update.message.chat.id
            chatName = update.message.chat.title
            chattype = update.message.chat.type

            msgid = update.message.reply_to_message.message_id
            replymsgid = update.message.message_id
            isreply = 1

            votes = 0
            stage = 1

            requesttype = 'feature'
            
            replymessage = update.message.text.replace('/request@{}'.format(config.BOT_USERNAME), '', 1).replace('/request', '', 1).strip()
            if update.message.reply_to_message.caption != None:
                request = update.message.reply_to_message.caption.replace('/request@{}'.format(config.BOT_USERNAME), '', 1).replace('/request', '', 1).strip()
            else:
                request = update.message.reply_to_message.text.replace('/request@{}'.format(config.BOT_USERNAME), '', 1).replace('/request', '', 1).strip()
            
            if (last_name != None and last_name.strip() != ''):
                name = first_name + ' ' + last_name
            else:
                name = first_name
            
            if (replylast_name != None and replylast_name.strip() != ''):
                replyname = replyfirst_name + ' ' + replylast_name
            else:
                replyname = replyfirst_name

        else:
            date = update.message.date

            userid = update.message.from_user.id
            replyuserid = None

            first_name = update.message.from_user.first_name
            last_name = update.message.from_user.last_name
            replyfirst_name = None
            replylast_name = None
            replyname = None

            username = update.message.from_user.username
            replyusername = None

            chatid = update.message.chat.id
            chatName = update.message.chat.title
            chattype = update.message.chat.type

            msgid = update.message.message_id
            replymsgid = None

            isreply = 0
            votes = 0
            stage = 1

            requesttype = 'feature'
            
            replymessage = None
            request = update.message.text.replace('/request@{}'.format(config.BOT_USERNAME), '', 1).replace('/request', '', 1).strip()
            if (last_name != None and last_name.strip() != ''):
                name = first_name + ' ' + last_name
            else:
                name = first_name
                
        if request.strip() != '':
            list_of_commands = ['Accept', 'Reject']
            buttons_list = []
            for i in list_of_commands:
                buttons_list.append(InlineKeyboardButton(text=i, callback_data = i))
            reply_markup = InlineKeyboardMarkup([buttons_list])
            context.bot.send_message(chat_id=config.master_id[0], text="New request added: {}".format(request), reply_markup=reply_markup)
            conn = sqlite3.connect('requests_db.db')
            d = conn.cursor()
            d.execute("INSERT INTO requests (date, userid, name, username, chatid, chatName, chattype, msgid, isreply, replyuserid, replyname, replyusername, replymsgid, replymessage, request, requesttype, votes, stage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,1)", (date, userid, name, username, chatid, chatName, chattype, msgid, isreply, replyuserid, replyname, replyusername, replymsgid, replymessage, request, requesttype))
            # d.execute("INSERT INTO requests (date, name, userid, username, request, stage, type) VALUES (?,?,?,?,?,0,?)", (date, name, chatid, username, request, chattype))
            conn.commit()
            conn.close()
            update.message.reply_text('Request Added Successfully')

        else:
            update.message.reply_text('Please enter a valid request.')    

    except Exception as e:
        update.message.reply_text('Failed to add request. Please try again later.')
        print(update.message)
        context.bot.send_message(chat_id=config.master_id[0], text="Error: {}".format(e))
    # dont forget to star the repo

# def add_bug(update, context):
    # update.message.reply_text('Bug Added Successfully')

def ask_query(update, context):
    pass

def reply_user(update, context):
    pass

def request_status(update, context):
    pass

def info(update, context):
    pass

def callback_query_handler(update, context):
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()

    query = update.callback_query
    query.answer()
    query_param = query.data
    # print(query)

    
    if query_param == 'Accept':
        # d.execute('SELECT * FROM requests WHERE request LIKE {}'.format(query.message.text))
        query.message.edit_text(text=query.message.text+'\nStatus: 🟢',parse_mode=ParseMode.MARKDOWN,)
        d.execute('UPDATE requests SET stage = 2 WHERE request = "{}"'.format(query.message.text.replace("New request added: ","")))
        
        # context.bot.send_message(chat_id=update.effective_chat.id,text='Your request has been ACCEPTED')
    if query_param == 'Reject':
        query.message.edit_text(text=query.message.text+'\nStatus: 🔴',parse_mode=ParseMode.MARKDOWN,)
        d.execute('DELETE FROM requests WHERE request = "{}"'.format(query.message.text.replace("New request added: ","")))
        # context.bot.send_message(chat_id=update.effective_chat.id,text='Your request has been REJECTED')
    if query_param == 'Delete Request':
        if (update.effective_chat.id == config.master_id[0]):
            query.message.delete()
            d.execute('DELETE FROM requests WHERE date = "{}"'.format(query.message.text.split(",")[0].replace("[", "").replace('"', "")))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,text='Access Denied')
        
    
    conn.commit()
    conn.close()

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def main():
    conn = sqlite3.connect('requests_db.db')
    d = conn.cursor()
    # stage=0(ready to do a request) stage=1(just typed /request) stage=2(gave the name of the apk) stage=3(he have to confirm all) stage=4(examinating) stage=5(voting) stage=6(approved) stage=7(soddisfacted and to delete) stage=13(BANNED)
    d.execute("CREATE TABLE IF NOT EXISTS requests (date VARCHAR, userid INTEGER, name TEXT, username TEXT, chatid INTEGER, chatName TEXT, chattype TEXT, msgid INTEGER, isreply BIT, replyuserid INTEGER, replyname TEXT, replyusername TEXT, replymsgid INTEGER, replymessage TEXT, request TEXT, requesttype TEXT, votes INTEGER DEFAULT 0, stage INTEGER DEFAULT 1)")
    conn.commit()
    conn.close()

    updater = Updater(token=config.TOKEN)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    dispatcher.add_handler(CommandHandler('request', add_request, pass_user_data=True))
    dispatcher.add_handler(CommandHandler('myinfo', myinfo))
    dispatcher.add_handler(CommandHandler('allrequests', show_requests))
    dispatcher.add_handler(CommandHandler('myrequests', show_my_requests))
    dispatcher.add_handler(CommandHandler('pendingrequests', show_requests_count))
    dispatcher.add_handler(CommandHandler('notes', show_faqs))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
