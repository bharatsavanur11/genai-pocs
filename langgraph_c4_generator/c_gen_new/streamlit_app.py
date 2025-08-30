#!/usr/bin/env python3
"""
Streamlit UI for interactive C4 DSL generation.

- Upload or paste technical specification iteratively
- Append new content and re-run to evolve the generated DSL
- View System Context, Container, Unified Context+Container, and Component DSLs
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

import streamlit as st

# Local imports
from mod.generator import generate_c4_architecture, save_dsl_files


APP_TITLE = "C4 Architecture Generator (Interactive)"


def init_session_state():
    if "spec_text" not in st.session_state:
        st.session_state.spec_text = ""
    if "auto_run" not in st.session_state:
        st.session_state.auto_run = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "output_dir" not in st.session_state:
        st.session_state.output_dir = "generated_c4"


def render_sidebar() -> None:
    st.sidebar.header("Controls")

    # API key visibility
    api_present = bool(os.getenv("OPENAI_API_KEY"))
    st.sidebar.markdown(
        f"API Key: {'✅ Detected' if api_present else '❌ Missing'}"
    )
    if not api_present:
        st.sidebar.info("Set OPENAI_API_KEY in your environment or .env file.")

    # Upload spec file
    uploaded = st.sidebar.file_uploader("Upload spec file (.txt/.md)", type=["txt", "md"])
    if uploaded is not None:
        try:
            content = uploaded.read().decode("utf-8", errors="ignore")
            if st.sidebar.button("Append Uploaded Content"):
                st.session_state.spec_text = (st.session_state.spec_text + "\n\n" + content).strip()
                st.sidebar.success("Content appended to spec")
                if st.session_state.auto_run:
                    run_generation()
        except Exception as e:
            st.sidebar.error(f"Failed to read file: {e}")

    # Output directory
    st.session_state.output_dir = st.sidebar.text_input(
        "Output directory", st.session_state.output_dir
    )

    # Auto-run toggle
    st.session_state.auto_run = st.sidebar.toggle("Auto-generate on change", value=st.session_state.auto_run)

    # Save results
    if st.sidebar.button("Save current DSLs"):
        res = st.session_state.last_result
        if res and res.get("success"):
            files = save_dsl_files(res, st.session_state.output_dir)
            st.sidebar.success(f"Saved {len(files)} files → {st.session_state.output_dir}")
        else:
            st.sidebar.warning("No successful generation available to save.")

    # Clear spec
    if st.sidebar.button("Clear spec"):
        st.session_state.spec_text = ""
        st.session_state.last_result = None
        st.sidebar.success("Cleared.")


def run_generation() -> None:
    spec = st.session_state.spec_text.strip()
    if not spec:
        st.warning("Provide or upload specification content first.")
        return
    with st.spinner("Generating C4 DSLs..."):
        result = generate_c4_architecture(spec)
        st.session_state.last_result = result
        if result.get("success"):
            st.success("Generation complete.")
        else:
            st.error(f"Generation failed: {result.get('error')}")


def render_body():
    st.title(APP_TITLE)
    st.caption("Upload or paste spec text iteratively. Click Generate to update DSLs.")

    # Spec editor
    st.subheader("Specification")
    new_text = st.text_area(
        "Paste or edit specification (append new info over time)",
        value=st.session_state.spec_text,
        height=280,
        key="spec_text_area",
    )
    if new_text != st.session_state.spec_text:
        st.session_state.spec_text = new_text
        if st.session_state.auto_run:
            run_generation()

    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("Generate / Update", type="primary"):
            run_generation()
    with cols[1]:
        if st.button("Append Example Text"):
            example = (
                "\nNew detail: Add \"Search Service\" container (FastAPI) under the E-commerce Platform to index products."
            )
            st.session_state.spec_text = (st.session_state.spec_text + example).strip()
            if st.session_state.auto_run:
                run_generation()

    # Results
    st.subheader("Results")
    res: Dict[str, Any] = st.session_state.last_result or {}
    if not res:
        st.info("No results yet. Generate to see outputs.")
        return

    # Summary
    with st.expander("Summary", expanded=True):
        st.write(res.get("summary", "No summary available."))

    # DSL tabs
    dsl = res.get("dsl", {}) if res.get("success") else {}
    tabs = st.tabs(["Unified (Context+Container)", "System Context", "Container", "Component", "JSON"])

    with tabs[0]:
        cc = dsl.get("context_container")
        if cc:
            st.code(cc, language="dsl")
        else:
            st.caption("Unified DSL not available yet.")

    with tabs[1]:
        ctx = dsl.get("context")
        if ctx:
            st.code(ctx, language="dsl")
        else:
            st.caption("Context DSL not available.")

    with tabs[2]:
        cont = dsl.get("container")
        if cont:
            st.code(cont, language="dsl")
        else:
            st.caption("Container DSL not available.")

    with tabs[3]:
        comp = dsl.get("component")
        if comp:
            st.code(comp, language="dsl")
        else:
            st.caption("Component DSL not available.")

    with tabs[4]:
        st.json({
            "systems": res.get("systems", []),
            "containers": res.get("containers", []),
            "components": res.get("components", []),
            "relationships": res.get("relationships", []),
            "external_systems": res.get("external_systems", []),
            "missing_info": res.get("missing_info", []),
        })

    # Save hint
    st.caption(
        f"Use the sidebar → 'Save current DSLs' to write files to {st.session_state.output_dir}."
    )


def main():
    init_session_state()
    render_sidebar()
    render_body()


if __name__ == "__main__":
    main()


