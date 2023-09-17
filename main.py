from core.judger import RowCompare
from i18n import switch_language

cmp = RowCompare()

print(cmp.judge("1\n2\n3", "1\n2\n4 5"))

switch_language("en_US")

print(cmp.judge("1\n2\n3", "1\n2\n4 5"))