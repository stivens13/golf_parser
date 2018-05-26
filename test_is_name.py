from unittest import TestCase
import processor

urls = []
people = []
name_list = set()
positions_list = set()
filtered = set()

output_file = "doc.csv"
url_file = "urls.txt"
failed_file = "failed.txt"
names_file = "names_dict.txt"
positions_file = "positions.txt"

class TestIs_name(TestCase):

    def setUp(self):
        processor.get_names()
        processor.get_positions()

    def test_is_name(self):
        self.assertEqual(processor.is_name("Barbara"), True)
        self.assertEqual(processor.is_name("Ryan Taggart"), True)
        self.assertEqual(processor.is_name("Katie Petracich"), True)
        self.assertEqual(processor.is_name("Barbara"), True)
        self.assertEqual(processor.is_name("Barbara"), True)

    def test_not_name(self):
        self.assertEqual(processor.is_name("Assistant Green Superintendent"), False)

    def test_not_position(self):
        self.assertEqual(processor.is_position("chef@bhamcc.com"), False)

    def test_is_phone(self):
        # self.assertEqual(processor.is_phone_number('Contact Carl at 536-4465 or cgranberg@rgcc.org'), True)
        self.assertEqual(processor.is_phone_number('Contact David at dpetric@rgcc.org or at 507-316-4896'), True)
        self.assertEqual(processor.is_phone_number('989-832-4280'), True)
        self.assertEqual(processor.is_phone_number('989.832.4293'), True)
        self.assertEqual(processor.is_phone_number('203-655-9726 x205'), True)
        self.assertEqual(processor.is_phone_number('203-655-9726 x200'), True)
        self.assertEqual(processor.is_phone_number('203-655-7043'), True)
        self.assertEqual(processor.is_phone_number('704-896-7080 ext. 281'), True)
        self.assertEqual(processor.is_phone_number('704-896-7080 ext. 2918'), True)
        self.assertEqual(processor.is_phone_number('(704) 896-7060'), True)
        self.assertEqual(processor.is_phone_number('704-896-4916'), True)
        self.assertEqual(processor.is_phone_number('704-896-7080 ext. 245'), True)
        self.assertEqual(processor.is_phone_number('(704) 896-7676'), True)
        self.assertEqual(processor.is_phone_number('(770)-497-0055'), True)
        self.assertEqual(processor.is_phone_number('732-291-0533 x22'), True)


        # self.assertEqual(processor.is_phone_number(''), True)
        # self.assertEqual(processor.is_phone_number(''), True)

    def test_is_phone2(self):
        self.assertEqual(processor.is_phone_number('Ph. 914-941-8070, ext. 415'), True)
        self.assertEqual(processor.is_phone_number('Ph. 914-941-3062'), True)
        self.assertEqual(processor.is_phone_number('Ph. 914-941-8070, ext. 422'), True)

    def test_is_phone3(self):
        self.assertEqual(processor.is_phone_number('Contact Carl at 536-4465 or cgranberg@rgcc.org'), True)