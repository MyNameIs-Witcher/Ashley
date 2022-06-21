import win10toast

toast = win10toast.ToastNotifier()


if __name__ == "__main__":
    toast.show_toast(
        title='Wake up, Neo...',
        msg='The Matrix has you...',
        duration=10
    )

