import re
from rest_framework.exceptions import ValidationError

email_regax = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}")
phone_regax = re.compile(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$")

def check_email_or_phone(email_or_phone) :
    if email_regax.fullmatch(email_or_phone) :
        return 'email'
    elif phone_regax.fullmatch(email_or_phone):
        return 'phone'
    
    data = {
        'success' : False,
        'message' : 'Email yoki Telefon raqam notogri yuborilgan '
    }
    
    raise ValidationError(data)
    
