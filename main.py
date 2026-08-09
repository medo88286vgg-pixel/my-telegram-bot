import time
import smtplib
import threading
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

# --- إعدادات البوت ---
bot_token = '8891457106:AAGb3u1cNeNCX3dktRy69Xkv8I2QQ8OE5bU'
bot = telebot.TeleBot(bot_token)

user_data = {}
allowed_users = ['7344994527', '2122029019']
admin_id = '2122029019'
subscription_data = {}

# --- لوحة التحكم الرئيسية ---
keyboard = types.InlineKeyboardMarkup(row_width=2)
btn_start_sending = types.InlineKeyboardButton('🚀 بدء الإرسال', callback_data='start_sending')
btn_explain = types.InlineKeyboardButton('📖 شرح البوت', url='https://t.me/mmakkkaaas/3')
btn_add_recipient = types.InlineKeyboardButton('📥 إضافة إيميل الشركة', callback_data='add_recipient')
btn_add_sender = types.InlineKeyboardButton('✉️ تعيين إيميل شد', callback_data='add_sender')
btn_set_subject_message = types.InlineKeyboardButton('📝 تعيين الموضوع والكليشة', callback_data='set_subject_message')
btn_set_interval_message_count = types.InlineKeyboardButton('⏱️ تعيين السليب وعدد الرسائل', callback_data='set_interval_message_count')
btn_show_all_info = types.InlineKeyboardButton('📊 عرض المعلومات', callback_data='show_all_info')
btn_clear_all_info = types.InlineKeyboardButton('🧹 مسح كل المعلومات', callback_data='clear_all_info')
btn_delete_email = types.InlineKeyboardButton('❌ مسح إيميل معين', callback_data='delete_email')
btn_show_accounts = types.InlineKeyboardButton('📁 إيميلاتي', callback_data='show_accounts')
btn_delete_klishes = types.InlineKeyboardButton('🗑️ حذف الكلايش والدعم', callback_data='delete_klishes')

keyboard.add(btn_start_sending, btn_explain)
keyboard.add(btn_add_recipient, btn_add_sender)
keyboard.add(btn_set_subject_message, btn_set_interval_message_count)
keyboard.add(btn_show_all_info, btn_clear_all_info)
keyboard.add(btn_delete_email, btn_show_accounts)
keyboard.add(btn_delete_klishes)

# --- لوحة الأدمن ---
admin_keyboard = types.InlineKeyboardMarkup(row_width=2)
btn_add_subscriber = types.InlineKeyboardButton('👤 إضافة مشترك', callback_data='add_subscriber')
btn_show_subscribers = types.InlineKeyboardButton('👥 عرض المشتركين', callback_data='show_subscribers')
btn_remove_subscriber = types.InlineKeyboardButton('❌ حذف مشترك', callback_data='remove_subscriber')
admin_keyboard.add(btn_add_subscriber, btn_show_subscribers, btn_remove_subscriber)

# --- لوحة تحديد مدة الاشتراك ---
duration_keyboard = types.InlineKeyboardMarkup(row_width=2)
btn_one_day = types.InlineKeyboardButton('1️⃣ يوم', callback_data='duration_1_day')
btn_one_week = types.InlineKeyboardButton('7️⃣ أسبوع', callback_data='duration_1_week')
btn_one_month = types.InlineKeyboardButton('🗓️ شهر', callback_data='duration_1_month')
btn_one_year = types.InlineKeyboardButton('📅 سنة', callback_data='duration_1_year')
duration_keyboard.add(btn_one_day, btn_one_week, btn_one_month, btn_one_year)

# --- الدوال المساعدة ---
def add_user_to_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'email_senders': [],
            'email_passwords': [],
            'recipients': [],
            'email_subjects': [],
            'email_messages': [],
            'interval_seconds': 0,
            'message_count': 0,
            'current_subject': '',
            'current_message': '',
            'stop_sending': False
        }

def safe_send_message(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except ApiTelegramException as e:
        if e.error_code == 429:
            retry_after = int(e.result_json.get('parameters', {}).get('retry_after', 5))
            time.sleep(retry_after)
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        return None

def safe_edit_message_text(chat_id, message_id, text, reply_markup=None):
    try:
        return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)
    except ApiTelegramException as e:
        if e.error_code == 429:
            retry_after = int(e.result_json.get('parameters', {}).get('retry_after', 5))
            time.sleep(retry_after)
            return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)
        return None

def send_email(sender_email, sender_password, recipient, subject, message):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    msg.add_header('User-Agent', 'iPhone Mail (14F5089a)')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Failed to send email from", sender_email, "to", recipient, ":", str(e))
        return False

# --- أوامر البوت ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id in allowed_users:
        add_user_to_data(user_id)
        bot.reply_to(message, 'أهلاً بك عزيزي في بوت الرفع الخارجي', reply_markup=keyboard)
    else:
        bot.reply_to(message, 'أنت غير مشترك في البوت. للاشتراك تواصل مع: @G_E_N')

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = str(message.from_user.id)
    user_info = user_data.get(user_id)
    if user_info:
        user_info['stop_sending'] = True
        bot.reply_to(message, 'تم إيقاف عملية الإرسال بنجاح!')
    else:
        bot.reply_to(message, 'لم تقم ببدء عملية الإرسال بعد.')

@bot.message_handler(commands=['admin'])
def show_admin_commands(message):
    if str(message.from_user.id) == admin_id or str(message.from_user.id) in allowed_users:  
        bot.send_message(message.chat.id, 'اختر الأمر الذي ترغب في تنفيذه:', reply_markup=admin_keyboard)
    else:
        bot.reply_to(message, 'أنت لست مطورًا مصرحًا له.')

# --- معالجة الضغط على الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    add_user_to_data(user_id)

    if call.data == 'add_recipient':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                               text="قم بإرسال إيميلات الشركة بهذه الطريقة:\nemail1@tele.com email2@tele.com")
        bot.register_next_step_handler(call.message, add_recipient, user_id)

    elif call.data == 'add_sender':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                               text="قم بإرسال إيميلات الشد بهذه الطريقة:\nemail1:pass1\nemail2:pass2")
        bot.register_next_step_handler(call.message, add_sender, user_id)

    elif call.data == 'set_subject_message':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                               text='الرجاء إرسال الموضوع والكليشة بهذه الطريقة: الموضوع:الكليشة')
        bot.register_next_step_handler(call.message, set_subject_message, user_id)

    elif call.data == 'set_interval_message_count':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                               text='الرجاء إرسال السليب وعدد الرسائل بهذه الطريقة: السليب:عدد الرسائل')
        bot.register_next_step_handler(call.message, set_interval_message_count, user_id)

    elif call.data == 'start_sending':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='جارٍ بدء إرسال الرسائل...')
        start_sending(user_id)

    elif call.data == 'show_accounts':
        show_accounts(call.message, user_id)

    elif call.data == 'show_all_info':
        show_all_info(call.message, user_id)

    elif call.data == 'clear_all_info':
        clear_all_info(call.message, user_id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='تم مسح جميع المعلومات بنجاح!')

    elif call.data == 'delete_email':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال رقم البريد الإلكتروني الذي ترغب في حذفه.')
        bot.register_next_step_handler(call.message, delete_email, user_id)

    elif call.data == 'stop_sending':
        user_data[user_id]['stop_sending'] = True
        bot.answer_callback_query(call.id, "تم طلب إيقاف الإرسال.")

    elif call.data == 'add_subscriber':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال ID الشخص الذي تريد إضافته لقائمة المشتركين')
        bot.register_next_step_handler(call.message, add_subscriber)

    elif call.data == 'show_subscribers':
        show_subscribers(call.message)

    elif call.data == 'remove_subscriber':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال ID الشخص الذي تريد حذفه من قائمة المشتركين')
        bot.register_next_step_handler(call.message, remove_subscriber)

    elif call.data.startswith('duration_'):
        handle_subscription_duration(call, user_id, call.data)

    elif call.data == 'add_more_subject_message':
        bot.answer_callback_query(call.id)
        if len(user_data[user_id]['email_subjects']) >= 5:
            bot.send_message(user_id, 'لا يمكن إضافة أكثر من 5 مواضيع وكليشة.')
        else:
            bot.send_message(user_id, 'الرجاء إرسال الموضوع والكليشة بالطريقة التالية: الموضوع:الكليشة')
            bot.register_next_step_handler(call.message, set_subject_message, user_id)

    elif call.data == 'finish_subject_message':
        bot.answer_callback_query(call.id, "تم إنهاء تعيين المواضيع والكليشة.")
        show_all_info(call.message, user_id)

    elif call.data == 'delete_klishes':
        delete_klishes(call.message, user_id)

    elif call.data == 'noop':
        bot.answer_callback_query(call.id)

# --- خطوات الإدخال والتسجيل ---
def add_recipient(message, user_id):
    recipients = message.text.split()
    if recipients:
        user_data[user_id]['recipients'].clear()  
        user_data[user_id]['recipients'].extend(recipients)
        bot.reply_to(message, 'تمت إضافة الحسابات المستلمة بنجاح!')
    else:
        bot.reply_to(message, 'خطأ في إضافة الحسابات المستلمة.')

def add_sender(message, user_id):
    email_password_pairs = message.text.split('\n')  
    success_count = 0
    failure_count = 0
    
    for pair in email_password_pairs:
        sender_email_password = pair.split(':')
        if len(sender_email_password) == 2:
            sender_email = sender_email_password[0].strip()
            sender_password = sender_email_password[1].strip()
            if sender_email and sender_password:
                user_data[user_id]['email_senders'].append(sender_email)
                user_data[user_id]['email_passwords'].append(sender_password)
                success_count += 1
            else:
                failure_count += 1
        else:
            failure_count += 1
    
    msg_out = "تمت إضافة " + str(success_count) + " حساب مرسل بنجاح!"
    if success_count > 0:
        bot.reply_to(message, msg_out)
    if failure_count > 0:
        bot.reply_to(message, "حدث خطأ في إضافة بضع حسابات. الصيغة الصحيحة (Email:pass).")

def set_subject_message(message, user_id):
    try:
        subject, email_message = message.text.split(':', 1)
        user_data[user_id]['current_subject'] = subject.strip()
        user_data[user_id]['current_message'] = email_message.strip()
        
        bot.reply_to(message, 'تم تعيين الموضوع والكليشة بنجاح! الآن أرسل إيميل الدعم المخصص لهذه الكليشة:')
        bot.register_next_step_handler(message, set_recipient_email, user_id)
    except ValueError:
        bot.reply_to(message, 'خطأ في الصيغة. أرسل بالطريقة: الموضوع:الكليشة')

def set_recipient_email(message, user_id):
    if len(user_data[user_id]['email_subjects']) >= 5:
        bot.reply_to(message, 'لا يمكن إضافة أكثر من 5 مواضيع وكليشة.')
        return
    
    recipient_email = message.text.strip()
    user_data[user_id]['email_subjects'].append(user_data[user_id]['current_subject'])
    user_data[user_id]['email_messages'].append(user_data[user_id]['current_message'])
    user_data[user_id]['recipients'].append(recipient_email)
    
    sub_keyboard = types.InlineKeyboardMarkup(row_width=2)
    yes_button = types.InlineKeyboardButton(text="نعم", callback_data='add_more_subject_message')
    no_button = types.InlineKeyboardButton(text="لا", callback_data='finish_subject_message')
    sub_keyboard.add(yes_button, no_button)
    
    bot.reply_to(message, 'تم تعيين إيميل الدعم بنجاح! هل تريد تعيين كليشة أخرى؟', reply_markup=sub_keyboard)

def set_interval_message_count(message, user_id):
    try:
        interval_seconds, message_count = message.text.split(':', 1)
        user_data[user_id]['interval_seconds'] = int(interval_seconds.strip())
        user_data[user_id]['message_count'] = int(message_count.strip())
        bot.reply_to(message, 'تم تعيين السليب وعدد الرسائل بنجاح!')
    except ValueError:
        bot.reply_to(message, 'خطأ في الصيغة. أرسل بالطريقة: السليب:عدد الرسائل')

def delete_email(message, user_id):
    try:
        index = int(message.text.strip()) - 1
        if 0 <= index < len(user_data[user_id]['email_senders']):
            del user_data[user_id]['email_senders'][index]
            del user_data[user_id]['email_passwords'][index]
            bot.reply_to(message, 'تم حذف البريد الإلكتروني بنجاح!')
        else:
            bot.reply_to(message, 'رقم البريد الإلكتروني غير موجود.')
    except ValueError:
        bot.reply_to(message, 'يرجى إدخال رقم صحيح.')

# --- دالة الإرسال المتعدد ---
def send_emails(user_id, user_info):
    success_count = 0
    error_count = 0
    blocked_senders = set()
    messages_sent = 0

    total_messages = user_info['message_count']
    klishes_subjects = list(zip(user_info['email_subjects'], user_info['email_messages'], user_info['recipients']))
    klisha_sent_counts = {index: 0 for index in range(len(klishes_subjects))}

    initial_message = "بدأت عملية الإرسال...\nأرسل /stop أو اضغط زر الإيقاف للإلغاء."
    
    stop_kbd = types.InlineKeyboardMarkup()
    stop_kbd.add(types.InlineKeyboardButton(text="🛑 إيقاف الإرسال", callback_data='stop_sending'))
    
    sent_msg = safe_send_message(user_id, initial_message, reply_markup=stop_kbd)
    prev_message_id = sent_msg.message_id if sent_msg else None

    while messages_sent < total_messages:
        if len(blocked_senders) == len(user_info['email_senders']):
            final_message = "تم الانتهاء.\nتم إرسال: " + str(success_count) + "\nفشل: " + str(error_count) + "\nجميع حسابات الإرسال محظورة."
            if prev_message_id:
                safe_edit_message_text(user_id, prev_message_id, final_message)
            return

        for sender, password in zip(user_info['email_senders'], user_info['email_passwords']):
            if sender in blocked_senders:
                continue

            if user_info.get('stop_sending'):
                user_info['stop_sending'] = False
                final_message = "تم إيقاف عملية الإرسال بنجاح.\nتم إرسال: " + str(success_count) + "\nفشل: " + str(error_count)
                safe_send_message(user_id, final_message)
                return

            subject_index = messages_sent % len(klishes_subjects)
            subject, message_body, recipient_email = klishes_subjects[subject_index]
            
            if send_email(sender, password, recipient_email, subject, message_body):
                success_count += 1
                messages_sent += 1
                klisha_sent_counts[subject_index] += 1
            else:
                error_count += 1
                blocked_senders.add(sender)
                safe_send_message(user_id, 'الحساب ' + str(sender) + ' فشل أو محظور، تم التوقف عن استخدامه.')

            if messages_sent >= total_messages:
                break

            remaining_messages = total_messages - messages_sent
            
            status_kbd = types.InlineKeyboardMarkup(row_width=2)
            sent_btn = types.InlineKeyboardButton(text="تم إرسال: " + str(success_count), callback_data='noop')
            err_btn = types.InlineKeyboardButton(text="فشل: " + str(error_count), callback_data='noop')
            rem_btn = types.InlineKeyboardButton(text="المتبقي: " + str(remaining_messages), callback_data='noop')
            stop_btn = types.InlineKeyboardButton(text="🛑 إيقاف الإرسال", callback_data='stop_sending')
            
            status_kbd.add(sent_btn, err_btn)
            status_kbd.add(rem_btn, stop_btn)

            for index, count in klisha_sent_counts.items():
                status_kbd.add(types.InlineKeyboardButton(text="كليشة " + str(index + 1) + ": " + str(count), callback_data='noop'))

            status_text = "عملية الإرسال قيد التنفيذ..."
            if prev_message_id:
                safe_edit_message_text(user_id, prev_message_id, status_text, reply_markup=status_kbd)

        time.sleep(user_info['interval_seconds'])

    final_message = "تم الانتهاء من الإرسال بنجاح.\nتم إرسال: " + str(success_count) + "\nفشل: " + str(error_count)
    if prev_message_id:
        safe_edit_message_text(user_id, prev_message_id, final_message)

def start_sending(user_id):
    user_info = user_data[user_id]
    if not user_info['recipients']:
        safe_send_message(user_id, 'لا توجد حسابات مستلمة. أضف حساب مستلم أولاً.')
        return

    if not user_info['email_senders']:
        safe_send_message(user_id, 'لا توجد حسابات مرسلة. أضف حساب مرسل أولاً.')
        return

    if not user_info['email_subjects'] or not user_info['email_messages']:
        safe_send_message(user_id, 'لم يتم تعيين المواضيع أو الكليشة.')
        return

    if user_info['message_count'] == 0:
        safe_send_message(user_id, 'لم يتم تعيين عدد الرسائل.')
        return

    user_info['stop_sending'] = False
    sending_thread = threading.Thread(target=send_emails, args=(user_id, user_info))
    sending_thread.start()

# --- دوال العرض والمسح ---
def show_accounts(message, user_id):
    user_info = user_data[user_id]
    if not user_info['email_senders']:
        bot.send_message(chat_id=message.chat.id, text='لم يتم إضافة أي حسابات مرسلة حتى الآن.')
    else:
        accounts = ["حساب رقم " + str(i + 1) + ": " + str(sender) for i, sender in enumerate(user_info['email_senders'])]
        full_message = '\n'.join(accounts)
        bot.send_message(chat_id=message.chat.id, text=full_message)

def show_all_info(message, user_id):
    user_info = user_data[user_id]
    info_message = "إيميلات الدعم:\n"
    for i, recipient in enumerate(user_info['recipients']):
        info_message += "إيميل دعم لكليشة " + str(i + 1) + ": " + str(recipient) + "\n"
    info_message += "\nالموضوعات والكليشة:\n\n"
    for i, (subject, msg) in enumerate(zip(user_info['email_subjects'], user_info['email_messages'])):
        info_message += "الموضوع " + str(i + 1) + ": " + str(subject) + "\nالكليشة " + str(i + 1) + ": " + str(msg) + "\n\n"
    info_message += "السليب: " + str(user_info['interval_seconds']) + " ثانية\n"
    info_message += "عدد الرسائل: " + str(user_info['message_count']) + "\n"
    
    bot.send_message(message.chat.id, info_message)

def clear_all_info(message, user_id):
    user_data[user_id] = {
        'email_senders': [],
        'email_passwords': [],
        'recipients': [],
        'email_subjects': [],
        'email_messages': [],
        'interval_seconds': 0,
        'message_count': 0,
        'current_subject': '',
        'current_message': '',
        'stop_sending': False
    }

def delete_klishes(message, user_id):
    user_data[user_id]['email_subjects'].clear()
    user_data[user_id]['email_messages'].clear()
    user_data[user_id]['recipients'].clear()
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='تم حذف جميع الكليشات والمواضيع وإيميلات المستلمين بنجاح!')

# --- إدارة المشتركين للأدمن ---
def add_subscriber(message):
    new_user_id = message.text.strip()
    bot.reply_to(message, 'اختر مدة الاشتراك:', reply_markup=duration_keyboard)
    subscription_data['temp_user_id'] = new_user_id

def handle_subscription_duration(call, admin_id, duration):
    temp_user_id = subscription_data.get('temp_user_id')
    if not temp_user_id:
        bot.send_message(admin_id, 'لم يتم العثور على المستخدم.')
        return

    duration_map = {
        'duration_1_day': timedelta(days=1),
        'duration_1_week': timedelta(weeks=1),
        'duration_1_month': timedelta(days=30),
        'duration_1_year': timedelta(days=365)
    }
    duration_timedelta = duration_map.get(duration)
    if not duration_timedelta:
        bot.send_message(admin_id, 'مدة غير صالحة.')
        return

    expiration_date = datetime.now() + duration_timedelta
    if temp_user_id not in allowed_users:
        allowed_users.append(temp_user_id)
    subscription_data[temp_user_id] = expiration_date
    
    bot.send_message(admin_id, 'تم إضافة المستخدم ' + str(temp_user_id) + ' بنجاح لمدة ' + str(duration_timedelta.days) + ' يوم.')

def show_subscribers(message):
    if not subscription_data:
        bot.reply_to(message, 'لا يوجد مشتركون حاليًا.')
        return

    subscribers_info = []
    for uid, expiration_date in subscription_data.items():
        if uid != 'temp_user_id':
            subscribers_info.append('ID: ' + str(uid) + ', الانتهاء: ' + str(expiration_date.strftime("%Y-%m-%d %H:%M")))

    bot.reply_to(message, '\n'.join(subscribers_info) if subscribers_info else 'لا يوجد مشتركون حاليًا.')

def remove_subscriber(message):
    user_id = message.text.strip()
    if user_id in allowed_users:
        allowed_users.remove(user_id)
        subscription_data.pop(user_id, None)
        bot.reply_to(message, 'تم حذف المستخدم ' + str(user_id) + ' بنجاح.')
    else:
        bot.reply_to(message, 'المستخدم غير موجود.')

# --- بداية التشغيل ---
if __name__ == '__main__':
    try:
        print("---------------------------------------")
        print("Connecting to Telegram...")
        bot.remove_webhook()
        time.sleep(1)
        
        bot_info = bot.get_me()
        print("Connected successfully!")
        print("Bot Name:", bot_info.first_name)
        print("Username: @", bot_info.username)
        print("---------------------------------------")
        print("Send /start to your bot in Telegram now")
        
        bot.infinity_polling()
    except Exception as e:
        print("Error:", e)
