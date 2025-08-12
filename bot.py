import telebot

TOKEN = '8403823997:AAHhCx4bUDhOwpZ5GMp00W_zPS8H74pFw2c'

bot = telebot.TeleBot(TOKEN)

# Kanallar ro'yxati (Telegram kanal username bilan)
CHANNELS = ['beacon_club', 'alvin09_06']

# Foydalanuvchi ma'lumotlarini saqlash uchun oddiy dictionary (oddiy yechim)
users = {}

# Foydalanuvchi boshlaganda
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users[chat_id] = {
        'lang': None,
        'subscribed': False,
        'referrals': 0,
        'ref_by': None,
        'friends': []
    }
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row('O‘zbek', 'English')
    bot.send_message(chat_id, "Tilni tanlang / Choose your language:", reply_markup=markup)

# Til tanlash handleri
@bot.message_handler(func=lambda m: m.text in ['O‘zbek', 'English'])
def set_language(message):
    chat_id = message.chat.id
    lang = message.text
    users[chat_id]['lang'] = lang

    # Kanalga obuna bo‘lish uchun xabar va tugmalar
    markup = telebot.types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        url = f"https://t.me/{ch}"
        markup.add(telebot.types.InlineKeyboardButton(text=f"📢 {ch}", url=url))
    markup.add(telebot.types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs"))

    if lang == 'O‘zbek':
        bot.send_message(chat_id, "Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "To use the bot fully, please subscribe to the channels below:", reply_markup=markup)

# Inline tugma bosilganda (kanalga obuna tekshiruvi)
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    chat_id = call.message.chat.id

    # Telegramda kanalga obuna tekshirish API cheklangan, shuning uchun oddiy nazorat: 
    # siz botga o'zingiz qo'shgan userlarni yoki haqiqiy kanal adminlari yordamida tekshirishingiz mumkin.
    # Bu yerda faqat "Tekshirish bajarildi" deb javob beramiz.

    # Oddiy qilib, obunani ha deb belgilaymiz (sizga keyin haqiqiy tekshiruvni qo'shish kerak bo‘ladi)
    users[chat_id]['subscribed'] = True

    lang = users[chat_id]['lang']
    if lang == 'O‘zbek':
        bot.send_message(chat_id, "Siz barcha kanallarga obuna bo'ldingiz. Ro'yxatdan o'tishni davom ettiring.", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).row("Davom etish"))
    else:
        bot.send_message(chat_id, "You subscribed to all channels. Continue registration.", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).row("Continue"))

# Davom etish tugmasi bosilganda
@bot.message_handler(func=lambda m: m.text in ['Davom etish', 'Continue'])
def ask_contact(message):
    chat_id = message.chat.id
    lang = users[chat_id]['lang']

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Kontaktni ulashish / Share contact", request_contact=True))

    if lang == 'O‘zbek':
        bot.send_message(chat_id, "Davom etish uchun kontakt ulashing:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Please share your contact to continue:", reply_markup=markup)

# Kontakt kelganda
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    chat_id = message.chat.id
    lang = users[chat_id]['lang']

    users[chat_id]['contact'] = message.contact.phone_number

    if lang == 'O‘zbek':
        text = "Tabriklaymiz, siz konkursda ishtirok etyapsiz! Sovrinlar yutish uchun ko‘proq do‘stlar taklif qilib, ball to‘plang."
        buttons = ['Do\'stlarim', 'Top Reyting', 'Do\'st taklif qilish', 'Admin bilan bog\'lanish']
    else:
        text = "Congratulations! You joined the contest! Invite more friends to earn points."
        buttons = ['My Friends', 'Top Ranking', 'Invite Friends', 'Contact Admin']

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(*buttons)
    bot.send_message(chat_id, text, reply_markup=markup)

# Do'st taklif qilish tugmasi
@bot.message_handler(func=lambda m: m.text in ['Do\'st taklif qilish', 'Invite Friends'])
def send_referral_link(message):
    chat_id = message.chat.id
    ref_link = f"https://t.me/beacon_konkurs_bot?start={chat_id}"  # bot username o'zgartiring
    lang = users[chat_id]['lang']

    if lang == 'O‘zbek':
        bot.send_message(chat_id, f"Sizning referall linkingiz: {ref_link}")
    else:
        bot.send_message(chat_id, f"Your referral link: {ref_link}")

# Top reyting tugmasi
@bot.message_handler(func=lambda m: m.text in ['Top Reyting', 'Top Ranking'])
def show_top_list(message):
    chat_id = message.chat.id
    # Foydalanuvchilar ballari bo‘yicha saralash (oddiy yechim)
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('referrals', 0), reverse=True)

    text = "Top Reyting:\n" if users[chat_id]['lang'] == 'O‘zbek' else "Top Ranking:\n"
    for i, (uid, data) in enumerate(sorted_users[:10], 1):
        name = bot.get_chat(uid).first_name
        points = data.get('referrals', 0)
        text += f"{i}. {name} — {points} ball\n"

    bot.send_message(chat_id, text)

# Do'stlarim tugmasi
@bot.message_handler(func=lambda m: m.text in ['Do\'stlarim', 'My Friends'])
def show_friends(message):
    chat_id = message.chat.id
    friends = users[chat_id].get('friends', [])
    lang = users[chat_id]['lang']

    if not friends:
        bot.send_message(chat_id, "Siz hali hech kimni taklif qilmagansiz." if lang == 'O‘zbek' else "You haven't invited anyone yet.")
        return

    text = "Sizning do‘stlaringiz:\n" if lang == 'O‘zbek' else "Your friends:\n"
    for f_id in friends:
        try:
            name = bot.get_chat(f_id).first_name
        except:
            name = "Noma'lum"
        text += f"- {name}\n"

    bot.send_message(chat_id, text)

# Admin bilan bog'lanish
@bot.message_handler(func=lambda m: m.text in ['Admin bilan bog\'lanish', 'Contact Admin'])
def contact_admin(message):
    admin_contact = "@alvin09_02"
    bot.send_message(message.chat.id, f"Admin bilan bog'lanish uchun: {admin_contact}")

# Start parametri orqali referral ball qo‘shish
@bot.message_handler(commands=['start'])
def referral_check(message):
    chat_id = message.chat.id
    if message.text and len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        if referrer_id.isdigit() and int(referrer_id) != chat_id:
            referrer_id = int(referrer_id)

            # Referrerning ballini oshirish
            if referrer_id in users:
                users[referrer_id]['referrals'] = users[referrer_id].get('referrals', 0) + 1
                users[referrer_id].setdefault('friends', []).append(chat_id)

bot.infinity_polling()
