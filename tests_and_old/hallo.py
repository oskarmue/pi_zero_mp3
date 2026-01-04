from collections import deque


widgets = deque(maxlen=5)

for i in range(5):
    widgets.append(i)


print(widgets)

widgets.appendleft(widgets[-1])

print(widgets)