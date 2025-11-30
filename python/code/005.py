import shelve, sys

def store_person(db):
    pid = input("Enter unique ID number:")
    person = {}
    person["pid"] = pid
    person["name"] = input("Enter Name:")
    person["phone"] = input("Enter phone number:")
    db[pid] = person


def lookup_person(db):
    pid = input("Enter unique ID number:")
    filed = input("What would you like to know? (name, phone)")
    filed = filed.strip().lower()
    print(f"{filed.capitalize()} : {db[pid][filed]}")


def print_help():
    print("The available command are: ")
    print("store: Stores information about a person")
    print("lookup: Look up a person from id number")
    print("quit: Save changes and exit")
    print("?: Print this message")


def enter_command():
    cmd = input("Enter command (? for help) ")
    cmd = cmd.strip().lower()
    return cmd


def main():
    print("fuck")
    db = shelve.open("./test/test.dat", writeback=True)
    try:
        while True:
            cmd = enter_command()
            if cmd == "store":
                store_person(db)
            elif cmd == "lookup":
                lookup_person(db)
            elif cmd == "?":
                print_help()
            elif cmd == "quit":
                return
    finally:
        db.close()


if __name__ == "__main__":
    main()
