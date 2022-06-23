import easyocr

def text_recognition(file_path):
    reader = easyocr.Reader(lang_list=["ru", "en"], gpu=False)
    result = reader.readtext(file_path, detail=0, paragraph=True)

    return result

def main():
    file_path = "test.png"
    print(text_recognition(file_path=file_path))

if __name__ == "__main__":
    main()

