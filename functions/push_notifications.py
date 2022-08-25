import sys
platform = sys.platform
if platform == "win32":
    try:
        import win10toast
        toast = win10toast.ToastNotifier()
    except ModuleNotFoundError as __err:
        print(f'Ошибка: {__err}. Модуль работает в тестовом режиме')
        test_flag = True

elif platform == "linux":
    try:
        import notify2
        notify2.init('Ashley notifications')
        toast = notify2.Notification('Toast from Ashley', icon='')
        toast.set_urgency(notify2.URGENCY_NORMAL)
        toast.set_timeout(1000)
    except ModuleNotFoundError as __err:
        print(f'Ошибка: {__err}. Модуль работает в тестовом режиме')
        test_flag = True


if __name__ == "__main__":
    if platform == "win32":
        toast.show_toast(
            title='Wake up, Neo...',
            msg='The Matrix has you...',
            duration=10
        )
    elif platform == "linux":
        toast.update('Toast from Ashley', 'Wake up, Neo...')
        toast.show()

