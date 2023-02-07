import sys

from ampel import energy_mix


def main():
    hour = 0
    if len(sys.argv) >= 2:
        hour = int(sys.argv[1])
    print(energy_mix.get_sustainable_energy_distribution(hour))


if __name__ == "__main__":
    main()
