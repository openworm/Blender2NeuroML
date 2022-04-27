from pynput import keyboard

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False
def main():
# Collect events until released
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener: 
            listener.join()
137
if __name__ == "__main__":
    main()

# num. = 110
# num1 = 97
# num3 = 99
# num7 = 103

# # ...or, in a non-blocking fashion:.
# listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
# listener.start()hello.1 c