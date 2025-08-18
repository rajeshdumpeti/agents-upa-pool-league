import argparse
import logging
from utils.config import load_config, ConfigError
from pipelines.plan_graph import Pipeline
from agents.prl import prl_clarify
from agents.sra import sra_rules
from agents.usg import usg_stories
from agents.qat import qat_tests

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the agents pipeline")
    parser.add_argument(
        "--config",
        default="configs/upa.yaml",
        help="Path to project config YAML",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
    except ConfigError as e:
        logger.error("Failed to load config: %s", e)
        raise SystemExit(1)

    pipeline = Pipeline([prl_clarify, sra_rules, usg_stories, qat_tests])
    pipeline.run(cfg)
