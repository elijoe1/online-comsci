import random
import math

num = 1000000

coords = [(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(num)]

count = 0

for item in coords:
    if math.sqrt(item[0] ** 2 + item[1] ** 2) <= 1:
        count += 1
    else:
        pass

print(count/num * 4)

# making some changes to check that my fresh git reinstall worked
