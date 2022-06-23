import sys
platform = sys.platform
if platform == "win32":
    import win10toast
    toast = win10toast.ToastNotifier()

elif platform == "linux":
    import notify2
    notify2.init('Ashley notifications')
    toast = notify2.Notification('Toast from Ashley',icon='')
    toast.set_urgency(notify2.URGENCY_NORMAL)
    toast.set_timeout(1000)




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

