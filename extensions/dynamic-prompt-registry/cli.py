#!/usr/bin/env python3
"""
Prompt Registry CLI - Simple and Working

Usage:
    python cli.py list [--domain DOMAIN]
    python cli.py get NAME
    python cli.py select "problem description"
    python cli.py render NAME --var=value
"""

import sys
import os
import argparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from registry import PromptRegistry, Domain, create_default_registry
from selector import select_prompt, explain_selection


def cmd_list(args):
    """List all prompts."""
    r = create_default_registry()

    if args.domain:
        try:
            domain = Domain[args.domain.upper()]
            prompts = r.find_by_domain(domain)
        except KeyError:
            print(f"Unknown domain: {args.domain}")
            print(f"Valid domains: {[d.name for d in Domain]}")
            return 1
    else:
        prompts = r.list_all()

    if not prompts:
        print("No prompts found.")
        return 0

    print(f"Found {len(prompts)} prompt(s):\n")
    for p in prompts:
        print(f"  {p.name}")
        print(f"    Domain: {p.domain.name}")
        print(f"    Quality: {p.quality}")
        print(f"    Tags: {', '.join(p.tags) if p.tags else 'none'}")
        print()

    return 0


def cmd_get(args):
    """Get a specific prompt."""
    r = create_default_registry()
    prompt = r.get(args.name)

    if not prompt:
        print(f"Prompt not found: {args.name}")
        print(f"Available: {[p.name for p in r.list_all()]}")
        return 1

    print(f"Name: {prompt.name}")
    print(f"Domain: {prompt.domain.name}")
    print(f"Quality: {prompt.quality}")
    print(f"Tags: {', '.join(prompt.tags) if prompt.tags else 'none'}")
    print(f"\nTemplate:\n{prompt.template}")

    return 0


def cmd_select(args):
    """Select best prompt for a problem."""
    r = create_default_registry()

    if args.explain:
        print(explain_selection(args.problem, r))
    else:
        prompt = select_prompt(args.problem, r)
        if prompt:
            print(f"Selected: {prompt.name}")
            print(f"\nTemplate:\n{prompt.template}")
        else:
            print("No suitable prompt found.")
            return 1

    return 0


def cmd_render(args):
    """Render a prompt with variables."""
    r = create_default_registry()
    prompt = r.get(args.name)

    if not prompt:
        print(f"Prompt not found: {args.name}")
        return 1

    # Parse --var=value arguments
    variables = {}
    for item in args.vars:
        if '=' in item:
            key, value = item.split('=', 1)
            variables[key] = value

    rendered = prompt.render(**variables)
    print(rendered)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Registry CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cli.py list
    python cli.py list --domain security
    python cli.py get debug
    python cli.py select "fix this SQL injection bug"
    python cli.py select "fix this SQL injection bug" --explain
    python cli.py render debug --issue="TypeError on line 42"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List prompts")
    list_parser.add_argument("--domain", help="Filter by domain")

    # get command
    get_parser = subparsers.add_parser("get", help="Get a prompt by name")
    get_parser.add_argument("name", help="Prompt name")

    # select command
    select_parser = subparsers.add_parser("select", help="Select best prompt for problem")
    select_parser.add_argument("problem", help="Problem description")
    select_parser.add_argument("--explain", action="store_true", help="Explain selection")

    # render command
    render_parser = subparsers.add_parser("render", help="Render a prompt with variables")
    render_parser.add_argument("name", help="Prompt name")
    render_parser.add_argument("vars", nargs="*", help="Variables as --key=value")

    args = parser.parse_args()

    if args.command == "list":
        return cmd_list(args)
    elif args.command == "get":
        return cmd_get(args)
    elif args.command == "select":
        return cmd_select(args)
    elif args.command == "render":
        return cmd_render(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
