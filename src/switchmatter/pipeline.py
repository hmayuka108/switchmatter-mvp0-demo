import argparse
import json
from .pipeline_core import PipelineError, extract_and_parse, run_analysis, run_pipeline


def main(argv=None):
    cli = argparse.ArgumentParser()
    cli.add_argument("pdf_path")
    args = cli.parse_args(argv)
    try:
        print(json.dumps(run_pipeline(args.pdf_path), indent=2))
    except RuntimeError as exc:
        cli.exit(1, f"Pipeline failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
