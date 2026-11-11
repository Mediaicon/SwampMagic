from player import Player

player = Player()


def clear_screen():
    print("\n" * 5)


def ferry_landing_dock():
    while True:
        clear_screen()

        print("=" * 40)
        print("FERRY LANDING DOCK")
        print("=" * 40)
        print()

        print("The fog hangs low over the water.")
        print("An old ferryman sits beside the dock.")
        print()

        print("1. Talk to Ferryman")
        print("2. Look Around")
        print("3. Leave")
        print()

        choice = input("> ")

        if choice == "1":
            talk_to_ferryman()

        elif choice == "2":
            look_around()

        elif choice == "3":
            print()
            print("You leave the dock.")
            break

        else:
            print()
            print("Invalid choice.")
            input("Press Enter...")


def talk_to_ferryman():
    print()
    print("The ferryman watches the water.")
    print()
    print('"You\'re not from around here."')
    print()

    input("Press Enter...")


def look_around():
    print()
    print("The dock creaks beneath your feet.")
    print("A small settlement can be seen through the fog.")
    print()

    input("Press Enter...")


def main():
    ferry_landing_dock()


if __name__ == "__main__":
    main()