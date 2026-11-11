from player import Player

player = Player()


def clear_screen():
    print("\n" * 5)


def add_journal_entry(entry):

    if entry not in player.journal:
        player.journal.append(entry)


def show_journal():

    print()
    print("=" * 40)
    print("JOURNAL")
    print("=" * 40)
    print()

    if not player.journal:
        print("No entries.")

    else:
        for entry in player.journal:
            print(f"- {entry}")

    print()
    input("Press Enter...")


def talk_to_ferryman():

    while True:

        print()
        print("The ferryman watches the water.")
        print()

        print("1. Ask about Ferry Landing")
        print("2. Ask about the Original Preacher")
        print("3. Leave")
        print()

        choice = input("> ")

        if choice == "1":

            print()

            if player.awareness < 10:

                print('"Ferry Landing takes anybody nobody else wants."')

            else:

                print('"You still think Ferry Landing is a place."')
                print()
                print('"It is a consequence."')

                add_journal_entry(
                    "The ferryman described Ferry Landing as a consequence."
                )

            print()
            input("Press Enter...")

        elif choice == "2":

            print()

            print('"Folks ask about him."')
            print()

            print('"Funny thing is nobody asks why he left."')

            add_journal_entry(
                "The ferryman suggested the Original Preacher fled for a reason."
            )

            print()
            input("Press Enter...")

        elif choice == "3":

            break

def look_around():

    print()

    if player.awareness < 10:

        print("The dock creaks beneath your feet.")
        print("A small settlement can be seen through the fog.")

        player.awareness += 5

        print()
        print("Awareness increased.")

    else:

        print("The dock creaks beneath your feet.")
        print("The ferryman never seems to look directly at you.")
        print("You are no longer sure the fog is moving with the wind.")

    print()
    input("Press Enter...")

def talk_to_storekeeper():

    while True:

        print()
        print("The storekeeper studies you carefully.")
        print()

        print("1. Ask about Ferry Landing")
        print("2. Ask about the Original Preacher")
        print("3. Leave")
        print()

        choice = input("> ")

        if choice == "1":

            print()

            print('"Don\'t let the ferryman fill your head."')
            print()

            print('"Some people need mysteries to survive."')

            add_journal_entry(
                "The storekeeper believes the ferryman sees meaning everywhere."
            )

            print()
            input("Press Enter...")

        elif choice == "2":

            print()

            print('"The Original Preacher?"')
            print()

            print('"Most people think he ran."')
            print()

            print('"Most people are lazy thinkers."')

            add_journal_entry(
                "The storekeeper does not believe the Original Preacher simply ran away."
            )

            print()
            input("Press Enter...")

        elif choice == "3":

            break


def ferry_landing_dock():

    while True:

        clear_screen()

        print("=" * 40)
        print("FERRY LANDING DOCK")
        print("=" * 40)

        print(f"Awareness: {player.awareness}")

        print()
        print("The fog hangs low over the water.")
        print("An old ferryman sits beside the dock.")
        print()

        print("1. Talk to Ferryman")
        print("2. Look Around")
        print("3. Journal")
        print("4. Leave")
        print()

        choice = input("> ")

        if choice == "1":
            talk_to_ferryman()

        elif choice == "2":
            talk_to_storekeeper()

        elif choice == "3":
            look_around()

        elif choice == "4":
            show_journal()

        elif choice == "5":
            print()
            print("You leave the dock.")
            break

        else:

            print()
            print("Invalid choice.")
            input("Press Enter...")


def main():
    ferry_landing_dock()


if __name__ == "__main__":
    main()