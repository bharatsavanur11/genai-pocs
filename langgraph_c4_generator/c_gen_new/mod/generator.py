import json
from pathlib import Path
from typing import Any, Dict, List

from .state import C4State
from .workflow import create_c4_workflow


def generate_c4_architecture(technical_spec: str) -> Dict[str, Any]:
    print("🚀 Starting C4 Architecture Generation...")
    print("=" * 60)

    workflow = create_c4_workflow()

    initial_state = C4State(
        raw_spec=technical_spec,
        systems=None,
        containers=None,
        components=None,
        relationships=None,
        external_systems=None,
        missing_info=None,
        summary=None,
        dsl_context=None,
        dsl_container=None,
        dsl_context_container=None,
        dsl_component=None,
        architecture_analysis=None,
    )

    try:
        result = workflow.invoke(initial_state)
        print("✅ C4 Architecture Generation Completed!")
        print("=" * 60)
        return {
            "success": True,
            "summary": result.get("summary", "No summary available"),
            "systems": result.get("systems", []),
            "containers": result.get("containers", []),
            "components": result.get("components", []),
            "relationships": result.get("relationships", []),
            "external_systems": result.get("external_systems", []),
            "missing_info": result.get("missing_info", []),
            "dsl": {
                "context": result.get("dsl_context"),
                "container": result.get("dsl_container"),
                "context_container": result.get("dsl_context_container"),
                "component": result.get("dsl_component"),
            },
            "architecture_analysis": result.get("architecture_analysis"),
        }
    except Exception as e:
        print(f"❌ Error in C4 architecture generation: {e}")
        return {"success": False, "error": str(e), "summary": "Generation failed due to an error"}


def save_dsl_files(result: Dict[str, Any], output_dir: str = "generated_c4") -> List[str]:
    Path(output_dir).mkdir(exist_ok=True)
    saved_files: List[str] = []

    if result.get("success"):
        dsl = result.get("dsl", {})
        if dsl.get("context"):
            p = Path(output_dir) / "system_context.dsl"
            p.write_text(dsl["context"])
            saved_files.append(str(p))
            print(f"💾 Saved System Context DSL: {p}")
        if dsl.get("container"):
            p = Path(output_dir) / "container.dsl"
            p.write_text(dsl["container"])
            saved_files.append(str(p))
            print(f"💾 Saved Container DSL: {p}")
        if dsl.get("component"):
            p = Path(output_dir) / "component.dsl"
            p.write_text(dsl["component"])
            saved_files.append(str(p))
            print(f"💾 Saved Component DSL: {p}")
        if dsl.get("context_container"):
            p = Path(output_dir) / "context_container.dsl"
            p.write_text(dsl["context_container"])
            saved_files.append(str(p))
            print(f"💾 Saved Merged Context+Container DSL: {p}")

        summary_file = Path(output_dir) / "architecture_summary.json"
        summary_file.write_text(
            json.dumps(
                {
                    "summary": result.get("summary"),
                    "systems": result.get("systems", []),
                    "containers": result.get("containers", []),
                    "components": result.get("components", []),
                    "relationships": result.get("relationships", []),
                    "external_systems": result.get("external_systems", []),
                    "missing_info": result.get("missing_info", []),
                },
                indent=2,
            )
        )
        saved_files.append(str(summary_file))
        print(f"💾 Saved Architecture Summary: {summary_file}")

    return saved_files


