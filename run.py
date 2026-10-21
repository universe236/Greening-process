"""Train the temperature surrogate or generate greening allocations."""

import argparse
from pathlib import Path

from greening.data import load_config
from greening.engine import evaluate, train
from greening.planning import plan


def main():
    parser = argparse.ArgumentParser(description="Generic temperature surrogate and greening planner")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("train", "evaluate", "plan"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--input", required=True, help="Directory of aligned city NPZ arrays")
        cmd.add_argument("--output", required=True)
        if name == "train":
            cmd.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
        else:
            cmd.add_argument("--checkpoint", required=True)
        if name == "plan":
            cmd.add_argument("--route", choices=("heat", "cool", "random"))
            cmd.add_argument("--route-seed", type=int)
    args = parser.parse_args()
    if args.command == "train":
        checkpoint = train(args.input, load_config(args.config), args.output)
        evaluate(checkpoint, args.input, Path(args.output) / "holdout")
    elif args.command == "evaluate":
        evaluate(args.checkpoint, args.input, args.output)
    else:
        overrides = {key: getattr(args, key) for key in ("route", "route_seed")
                     if getattr(args, key) is not None}
        plan(args.checkpoint, args.input, args.output, overrides)


if __name__ == "__main__":
    main()
