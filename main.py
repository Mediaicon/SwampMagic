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

    print()

    if not player.flags["met_ferryman"]:

        print("The ferryman watches the water.")
        print()
        print('"You\'re not from around here."')
        print()
        print(
            "The old man glances at you briefly before returning his attention to the river."
        )

        player.flags["met_ferryman"] = True

        add_journal_entry(
            "Met the ferryman. He immediately recognized I was an outsider."
        )

    elif player.awareness < 10:

        print("The ferryman spits into the river.")
        print()
        print('"You again."')
        print()
        print('"You ask a lot of questions for someone who just got here."')

    else:

        print("The ferryman stares into the fog.")
        print()
        print('"You still think Ferry Landing is a place."')
        print()
        print('"Most people figure out eventually that it\'s a consequence."')

        add_journal_entry(
            "The ferryman called Ferry Landing a consequence rather than a place."
        )

    print()
    input("Press Enter...")


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
            look_around()

        elif choice == "3":
            show_journal()

        elif choice == "4":

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