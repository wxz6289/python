#! /usr/bin/env python3
import random
import argparse
from os.path import isfile


def parse_args():
    """Parse command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Randomly change the case of letters in the input text.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--seed",
        metavar="seed",
        type=int,
        default=None,
        help="Seed for the random number generator (default: None)",
    )

    parser.add_argument(
        "text", metavar="text", type=str, help="Input text to transform"
    )

    args = parser.parse_args()

    if isfile(args.text):
        args.text = open(args.text).read().rstrip()

    return args


def main():
    """Main program function"""

    args = parse_args()
    # print(args)
    # if args
    random.seed(args.seed)

    transformed_chars = [
        char.upper() if random.choice([True, False]) else char.lower()
        for char in args.text
    ]

    transformed_text = "".join(transformed_chars)
    print(transformed_text)


# return transformed_text

if __name__ == "__main__":
    main()
