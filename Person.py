class Person:
    name = ""
    position = ""
    phone = ""
    email = ""
    extra = ""
    url = ""

    def __init__(self, name, position, phone, email, url):
        self.name = name
        self.position = position
        self.phone = phone
        self.email = email
        self.url = url

    def get_info(self):
        return [self.name, self.position, self.phone, self.email, self.url]
