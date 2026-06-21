#!/usr/bin/env python3
"""
Command-line version of the Password Generator
"""

import argparse
import sys
from password_generator import PasswordGenerator


def main():
    parser = argparse.ArgumentParser(description='Generate secure passwords')
    
    parser.add_argument('-l', '--length', type=int, default=16,
                       help='Password length (default: 16)')
    parser.add_argument('--no-lower', action='store_true',
                       help='Exclude lowercase letters')
    parser.add_argument('--no-upper', action='store_true',
                       help='Exclude uppercase letters')
    parser.add_argument('--no-digits', action='store_true',
                       help='Exclude digits')
    parser.add_argument('--no-symbols', action='store_true',
                       help='Exclude symbols')
    parser.add_argument('--exclude-ambiguous', action='store_true',
                       help='Exclude ambiguous characters (il1Lo0O)')
    parser.add_argument('--min-each-type', type=int, default=1,
                       help='Minimum characters from each selected type')
    parser.add_argument('--memorable', action='store_true',
                       help='Generate memorable passphrase')
    parser.add_argument('--words', type=int, default=4,
                       help='Number of words for memorable passphrase')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of passwords to generate')
    parser.add_argument('--evaluate', action='store_true',
                       help='Evaluate password strength')
    
    args = parser.parse_args()
    
    generator = PasswordGenerator()
    
    if args.memorable:
        for i in range(args.count):
            password = generator.generate_memorable_password(
                words=args.words,
                include_numbers=True,
                capitalize=True
            )
            print(password)
    else:
        for i in range(args.count):
            password = generator.generate_password(
                length=args.length,
                use_lower=not args.no_lower,
                use_upper=not args.no_upper,
                use_digits=not args.no_digits,
                use_symbols=not args.no_symbols,
                exclude_ambiguous=args.exclude_ambiguous,
                min_each_type=args.min_each_type
            )
            print(password)
            
            if args.evaluate:
                strength = generator.evaluate_strength(password)
                print(f"  Strength: {strength['strength']} ({strength['score']}/100)")
                if strength['feedback']:
                    print("  Feedback:")
                    for f in strength['feedback']:
                        print(f"    • {f}")
                print()


if __name__ == "__main__":
    main()
