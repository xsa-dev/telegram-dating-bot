from telegram import ReplyKeyboardMarkup, KeyboardButton, Bot, Update
from validator import Validator
import logging

class Handler:
    
    
    def __init__(self, lang):
        self.lang = lang
        self.valr = Validator()
        self.logger = logging.getLogger(__name__)


    def refresh_markup(self):
        self.markup = {
            # выбор своего пола
            'sexChoice': ReplyKeyboardMarkup(
                [
                    [KeyboardButton(self.lang['man']), KeyboardButton(self.lang['woman'])]
                ],
                resize_keyboard=True, 
                one_time_keyboard=True),
            # выбор партнёра
            'partnerChoice': ReplyKeyboardMarkup(
                [
                    [KeyboardButton(self.lang['man']), KeyboardButton(self.lang['woman'])],
                    #[KeyboardButton(self.lang['search_for_all'])]
                ],
            resize_keyboard=True, one_time_keyboard=True),
            # выбор лайков
            'markChoice': 
            ReplyKeyboardMarkup([[KeyboardButton(self.lang['like']), KeyboardButton(self.lang['dislike']), 
            KeyboardButton(self.lang['abuse']), KeyboardButton(self.lang['menu_stop'])
            ]],
                resize_keyboard=True, one_time_keyboard=True),
            # продолжить поиск
            'mainMenu': ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(self.lang['menu_continue']),
                        KeyboardButton(self.lang['menu_stop']),
                        # KeyboardButton(self.lang['menu_delete']), # < not
                        KeyboardButton(self.lang['menu_edit']),
                        KeyboardButton(self.lang['menu_show'])
                    ]
                ], resize_keyboard=True
                ),
            # подтвердить выбор
            'confirmReg': ReplyKeyboardMarkup(
                    [[KeyboardButton(self.lang['confirm_reg'])],
                    [KeyboardButton(self.lang['repeat_reg'])]],
                    resize_keyboard=True, one_time_keyboard=True),
            'freezed': 
                ReplyKeyboardMarkup([[KeyboardButton(self.lang['menu_continue'])]], resize_keyboard=True),
            # пустая клавиатура
            'empty': ReplyKeyboardMarkup([]),
            'accept': ReplyKeyboardMarkup(
                [[ KeyboardButton(self.lang['accept']) ]],
                resize_keyboard=True, one_time_keyboard=True
            )
        }

    def getLang(self, user = None):
        # TODO: later refactor this
        if user is None:
            return self.lang
        
        if 'lang' not in user:
            return self.lang
        user_lang_code = user['lang']

        temp_lang = self.lang
            
        if user_lang_code == self.lang['russian']:
            print('Твой язык русский.')
            self.lang = temp_lang['ru']
            
        elif user_lang_code == self.lang['english']:
            self.lang = temp_lang['en']
            print('Твой язык английский.')

        elif user_lang_code == self.lang['chinesian']:
            print('Твой язык китайский')
            self.lang == temp_lang['cn']

        self.lang['ru'] = temp_lang['ru']
        self.lang['en'] = temp_lang['en']
        self.lang['cn'] = temp_lang['cn']

    # Print next suitable account which we haven't rate
    def printNext(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        for i in range(len(db.getUsers())):
            if self.valr.checkPartner(user, db.getUsers()[i]):
                partner = db.getUsers()[i]
                db.updateUserData(uid, 'last_profile', partner['id'])
                bot.sendPhoto(cid, partner['photo'], reply_markup=self.markup['markChoice'], 
                    caption=self.lang['account_info'] % (partner['name'], partner['age'], partner['city'], partner['desc']),)
                return
                
        bot.sendMessage(cid, self.lang['no_partners'], reply_markup=self.markup['mainMenu'])
    
    def printMe(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        bot.sendPhoto(cid, user['photo'], 
                caption=self.lang['account_info'] % (user['name'], user['age'], user['city'], user['desc']), reply_markup=self.markup['mainMenu'])

    def handle(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        status = user['dialog_status']

        print(status)
        if update.message.from_user.username == None:
            bot.sendMessage(cid, self.lang['tag_not_found'], reply_markup=self.markup['empty'])
            return

        self.getLang(user)
        self.refresh_markup()

        if status == 'start':
            db.updateUserData(int(uid), 'dialog_status', 'set_lang') 

        elif status == 'set_lang':
            user_lang = str(update.message.text).strip()
            if self.valr.validLang(user_lang):
                db.updateUserData(int(uid), 'lang', str(update.message.text).strip())
                self.getLang(user)
                bot.sendMessage(cid, self.lang['valid_lang'], reply_markup=self.markup['accept'])
                db.updateUserData(int(uid), 'dialog_status', 'greeting')
            else:
                bot.sendMessage(cid, self.lang['not_valid_lang'], reply_markup=self.markup['empty'])
                db.updateUserData(int(uid), 'dialog_status', 'set_lang')

        elif status == 'set_lang_process':
            user_lang = str(update.message.text).strip()
            if self.valr.validLang(user_lang):                
                db.updateUserData(int(uid), 'lang', str(update.message.text).strip())
                user = db.getUserByID(uid)
                self.getLang(user)
                self.refresh_markup()
                bot.sendMessage(cid, self.lang['valid_lang'], reply_markup=self.markup['mainMenu'])
                db.updateUserData(int(uid), 'dialog_status', 'process')
            else:
                bot.sendMessage(cid, self.lang['not_valid_lang'], reply_markup=self.markup['empty'])
                db.updateUserData(int(uid), 'dialog_status', 'set_lang_process')

        elif status == 'greeting':
            bot.sendMessage(cid, self.lang['greeting_new'])
            db.updateUserData(int(uid), 'dialog_status', 'write_name')


        # Enter username
        elif status == 'write_name':
            # если имя правильно, то 
            if self.valr.validName(update.message.text):
                # записывает сообщение имени в профиль и 
                db.updateUserData(uid, 'name', str(update.message.text).strip())
                # переходит к следующему статусу
                db.updateUserData(uid, 'dialog_status', 'write_age')
                bot.sendMessage(cid, self.lang['write_age'] % (update.message.text))
            else:
                bot.sendMessage(cid, self.lang['invalid_name'])

        # Enter age
        elif status == 'write_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'write_city')  
                bot.sendMessage(cid, self.lang['write_city'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Enter city
        elif status == 'write_city':
            db.updateUserData(uid, 'city', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_sex')  
            bot.sendMessage(cid, self.lang['write_sex'], reply_markup=self.markup['sexChoice'])

        # Choose gender
        elif status == 'write_sex':
            if update.message.text == self.lang['man']:
                db.updateUserData(uid, 'sex', 0)
            elif update.message.text == self.lang['woman']:
                db.updateUserData(uid, 'sex', 1)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])
                return
            db.updateUserData(uid, 'dialog_status', 'write_desc')  
            bot.sendMessage(cid, self.lang['write_desc'])

        # Write description
        elif status == 'write_desc_':
            db.updateUserData(uid, 'desc', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_contact')
            bot.sendMessage(cid, self.lang['write_p_sex'], reply_markup=self.markup['partnerChoice'])

        # Write contacts
        elif status == 'write_desc':
            db.updateUserData(uid, 'desc', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_p_sex')
            bot.sendMessage(cid, self.lang['write_p_sex'], reply_markup=self.markup['partnerChoice'])

        # Choose partner's gender
        elif status == 'write_p_sex':
            if update.message.text == self.lang['man']:
                db.updateUserData(uid, 'contact', update.message.from_user.username)
                db.updateUserData(uid, 'p_sex', 0)
            elif update.message.text == self.lang['woman']:
                db.updateUserData(uid, 'contact', update.message.from_user.username)
                db.updateUserData(uid, 'p_sex', 1)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])
                return
            db.updateUserData(uid, 'dialog_status', 'write_p_min_age')  
            bot.sendMessage(cid, self.lang['write_p_min_age'])

        # Enter min partner's age
        elif status == 'write_p_min_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'p_min_age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'write_p_max_age')  
                bot.sendMessage(cid, self.lang['write_p_max_age'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Enter max partner's age
        elif status == 'write_p_max_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'p_max_age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'send_photo')  
                bot.sendMessage(cid, self.lang['send_photo'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Handle the photo and ask if all right
        elif status == 'send_photo':
            # TODO: add video support
            photo = update.message.photo[2]
            if self.valr.validPhoto(photo):

                db.updateUserData(uid, 'dialog_status', 'registered')
                db.updateUserData(uid, 'photo', photo.file_id)

                self.printMe(db, bot, update)
                bot.sendMessage(cid, self.lang['registered'], reply_markup=self.markup['confirmReg'])
            else:
                bot.sendMessage(cid, self.lang['invalid_photo'])
            

        # Start giving accounts
        elif status == 'registered':
            if update.message.text == self.lang['confirm_reg']:
                db.updateUserData(uid, 'dialog_status', 'process')
                db.saveUser(uid)
                self.printNext(db, bot, update)
            elif update.message.text == self.lang['repeat_reg']:
                db.updateUserData(uid, 'dialog_status', 'write_name')
                bot.sendMessage(cid, self.lang['rewrite'], reply_markup=self.markup['mainMenu'])
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'], reply_markup=self.markup['mainMenu'])

        # Search cycle
        # TODO: monetisation . .. ...
        # не понимаю на сколько это будет нормально работать с точки зрения производительности.. если будет 1000 пользователей например...
        elif status == 'process' and True:
            user = db.getUserByID(uid)
            # Account's rate
            if update.message.text == self.lang['like']:
                mutually = db.addLiked(uid, bot, update)
                # если взаимно не пусто
                if mutually != None:
                    bot.sendMessage(uid, self.lang['mutually'] % (mutually['contact'], self.lang['menu_continue']) , reply_markup=None)
                # 
                else:
                    self.printNext(db, bot, update)
            elif update.message.text == self.lang['dislike']:
                db.addDisliked(uid, bot, update)
                self.printNext(db, bot, update)
            # Main menu
            elif update.message.text == '1' or update.message.text == self.lang['menu_continue']:
                self.printNext(db, bot, update)
            elif update.message.text == self.lang['menu_stop']:
                db.updateUserData(uid, 'dialog_status', 'freezed')
                bot.sendMessage(cid, self.lang['profile_freezed'] % (self.lang['menu_continue']), reply_markup=self.markup['freezed'])
            # elif update.message.text == '3' or update.message.text == self.lang['menu_delete']:
            #     db.removeUser(uid)
            #     bot.sendMessage(cid, self.lang['profile_removed'])
            elif update.message.text == '4' or update.message.text == self.lang['menu_edit']:
                db.updateUserData(uid, 'dialog_status', 'write_name')
                bot.sendMessage(cid, self.lang['rewrite'])
            elif update.message.text == '5' or update.message.text == self.lang['menu_show']:
                self.printMe(db, bot, update)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'], reply_markup=self.markup['mainMenu'])

        # Account is freezed
        elif status == 'freezed':
            if update.message.text == self.lang['menu_continue']:
                db.updateUserData(uid, 'dialog_status', 'process')
                bot.sendMessage(cid, self.lang['process_resume'], reply_markup=self.markup['mainMenu'])
                self.printNext(db, bot, update)
                
        # Other situations
        else:
            bot.sendMessage(cid, self.lang['not_understand'])
