import argparse
from pipelines.plan_graph import Pipeline
from agents.prl import prl_clarify
from agents.sra import sra_rules
from agents.usg import usg_stories
from agents.qat import qat_tests
from utils.config import load_config, ConfigError

def main():
    parser = argparse.ArgumentParser(description="Run the agents pipeline")
    parser.add_argument("--config", default="configs/upa.yaml", help="Path to project config YAML")
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
    except ConfigError as e:
        raise SystemExit(str(e))

    pipeline = Pipeline([prl_clarify, sra_rules, usg_stories, qat_tests])
    initial = {"inputs": {"project_plan": cfg.get("project_name", "UPA MVP")}, "config": cfg}
    result = pipeline.run(initial)

    print(f"Loaded config: {args.config}")
    print("\n=== Clarifications ===\n", result["clarifications"])
    print("\n=== Rules JSON ===\n", result["rules_json"])
    print("\n=== Stories ===")
    for s in result["stories"]:
        print(s)
    print("\n=== Test Plan ===")
    for t in result["test_plan"]:
        print("-", t)

if __name__ == "__main__":
    main()
