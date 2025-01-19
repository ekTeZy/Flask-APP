import re
# валидация имени, пароля и телефона пользователя
def user_data_validation(**user_data):    
    for key in user_data:
        value = user_data.get(key)
        if value is None:
            continue
        
        if key == 'username':        
            if len(value) < 4:
                return False
        
        if key == 'password':
            if len(value) < 6:
                return False

        if key == 'phone':
            if not re.match(r'^(?:\+7|7|8)\d{10}$', value):
                return False

    return True