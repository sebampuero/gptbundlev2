from messaging.models import Chat

def init() -> None:
    Chat.create_table()

if __name__ == "__main__":
    init()
    print("Tables initialized")