# from collections import namedtuple
# from typing import Iterable

# City = namedtuple('City', 'name country population coordinates')
# CLT = ('Charlotte', 'USA', '1,000,000', ('100', '200'))
# Charlotte = City('Charlotte', 'USA', '1,000,000', ('100', '200'))
# print(Charlotte._fields, Charlotte._asdict(), City._make(CLT))


example = [i for i in range(0, 10)]
example[2:6] = ["second place","third Place", 'forth', 'fifth']

print(example * 3)