# Класс для валидаций

class Validator:
    def validName(self, name):
        # name or not name?
        if len(name) > 1 and len(name) < 30:
            return True
        return False
    
    def validPhoto(self, photo):
        # check foto validation
        # TODO: human or fallos?
        return True
    
    def validAge(self, age):
        # age validation function
        try:
            age = int(age)
            if age > 10 and age < 100:
                return True
            return False
        except:
            return False
            
    def validLang(self, lang):
        # supported languages
        try:
            if lang.lower() == 'russian' or lang.lower() == 'english' or lang.lower() == 'chinesian':
                return True
            else:
                return False
        except:
            return False
        

    def checkPartner(self, user, partner):
        # функция метчинга партнёров
        pCity = partner['city'].lower().strip()
        uCity = user['city'].lower().strip()
        if (partner['age'] >= user['p_min_age']) and (partner['age'] <= user['p_max_age']) and (partner['sex'] == user['p_sex']) and (pCity == uCity):
            if (partner['id'] not in user['liked']) and (partner['id'] not in user['disliked']):
                return True
        return False