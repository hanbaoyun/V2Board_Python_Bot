keyboard = []

for x in range(10):
    button = InlineKeyboardButton(text='a', url=f"url")
    if len(keyboard) == 0 or len(keyboard[len(keyboard)-1]) == 3:
        keyboard.append([button])
    elif len(keyboard[len(keyboard)-1]) < 3:
        keyboard[len(keyboard)-1].append(button)

print(keyboard)
