import prompt

COMMANDS = (
    "<command> exit - выйти из программы\n"
    "<command> help - справочная информация"
)


def welcome() -> None:
    print("Первая попытка запустить проект!\n\n***")
    print(COMMANDS)

    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
        except EOFError:
            return

        if command == "exit":
            return
        if command == "help":
            print(f"\n{COMMANDS}")
