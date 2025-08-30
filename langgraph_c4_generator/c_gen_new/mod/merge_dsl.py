import re
from typing import Any, Dict, List

from .state import C4State


def build_unified_workspace_dsl(state: C4State) -> str:
    systems = state.get("systems", []) or []
    containers = state.get("containers", []) or []
    external_systems = state.get("external_systems", []) or []
    relationships = state.get("relationships", []) or []

    if not systems and not containers and not external_systems:
        return "// No architecture elements available to build DSL"

    def make_alias(name: str) -> str:
        base = re.sub(r"[^A-Za-z0-9_]", "_", (name or "").strip())
        base = re.sub(r"_+", "_", base)
        return base[:60] if base else "Element"

    system_alias: Dict[str, str] = {}
    container_alias: Dict[str, str] = {}
    external_alias: Dict[str, str] = {}

    for sys_obj in systems:
        name = sys_obj.get("name") or sys_obj.get("title") or "System"
        alias = make_alias(name)
        i, orig = 2, alias
        while alias in system_alias.values():
            alias = f"{orig}_{i}"; i += 1
        system_alias[name] = alias

    for ext in external_systems:
        name = ext.get("name") or "ExternalSystem"
        alias = make_alias(name)
        i, orig = 2, alias
        while alias in external_alias.values() or alias in system_alias.values():
            alias = f"{orig}_{i}"; i += 1
        external_alias[name] = alias

    for cont in containers:
        name = cont.get("name") or "Container"
        sys_name = cont.get("system") or cont.get("belongs_to") or (systems[0].get("name") if systems else None)
        key = (sys_name or "_global_", name)
        alias = make_alias(f"{system_alias.get(sys_name, sys_name or 'Sys')}_{name}")
        i, orig = 2, alias
        while alias in container_alias.values() or alias in system_alias.values() or alias in external_alias.values():
            alias = f"{orig}_{i}"; i += 1
        container_alias[key] = alias

    dsl_lines: List[str] = []
    dsl_lines.append("workspace \"C4 Workspace\" \"Unified context+container view\" {")
    dsl_lines.append("  model {")

    for sys_obj in systems:
        name = sys_obj.get("name") or "System"
        desc = sys_obj.get("description") or sys_obj.get("purpose") or ""
        tech = sys_obj.get("technology") or ""
        alias = system_alias[name]
        dsl_lines.append(f"    softwareSystem \"{name}\" as {alias} {{")
        if desc:
            dsl_lines.append(f"      description \"{desc}\"")
        if tech:
            dsl_lines.append(f"      technology \"{tech}\"")
        for cont in [c for c in containers if (c.get("system") or c.get("belongs_to")) == name]:
            c_name = cont.get("name") or "Container"
            c_desc = cont.get("description") or cont.get("purpose") or ""
            c_tech = cont.get("technology") or ""
            c_alias = container_alias.get((name, c_name)) or make_alias(f"{alias}_{c_name}")
            line = f"      container \"{c_name}\" as {c_alias}"
            if c_desc and c_tech:
                line += f" \"{c_desc}\" \"{c_tech}\""
            elif c_desc:
                line += f" \"{c_desc}\""
            elif c_tech:
                line += f" \"\" \"{c_tech}\""
            dsl_lines.append(line)
        dsl_lines.append("    }")

    for ext in external_systems:
        name = ext.get("name") or "ExternalSystem"
        desc = ext.get("description") or ext.get("purpose") or ""
        tech = ext.get("technology") or ""
        alias = external_alias[name]
        dsl_lines.append(f"    softwareSystem \"{name}\" as {alias} <<External>> {")
        if desc:
            dsl_lines.append(f"      description \"{desc}\"")
        if tech:
            dsl_lines.append(f"      technology \"{tech}\"")
        dsl_lines.append("    }")

    def rel_line(src_alias: str, dst_alias: str, rel: Dict[str, Any]) -> str:
        desc = rel.get("description") or rel.get("interaction") or ""
        tech = rel.get("technology") or ""
        if desc and tech:
            return f"    {src_alias} -> {dst_alias} \"{desc}\" \"{tech}\""
        if desc:
            return f"    {src_alias} -> {dst_alias} \"{desc}\""
        if tech:
            return f"    {src_alias} -> {dst_alias} \"\" \"{tech}\""
        return f"    {src_alias} -> {dst_alias}"

    name_to_alias: Dict[str, str] = {**{k: v for k, v in system_alias.items()}, **{k: v for k, v in external_alias.items()}}
    for (sys_name, cont_name), alias in container_alias.items():
        count = sum(1 for (s, c) in container_alias.keys() if c == cont_name)
        if count == 1:
            name_to_alias[cont_name] = alias

    for rel in relationships:
        src_name = rel.get("source") or rel.get("from")
        dst_name = rel.get("destination") or rel.get("to")
        if not src_name or not dst_name:
            continue
        src_alias = name_to_alias.get(src_name)
        dst_alias = name_to_alias.get(dst_name)
        if not src_alias:
            for (s, c), a in container_alias.items():
                if c == src_name:
                    src_alias = a; break
        if not dst_alias:
            for (s, c), a in container_alias.items():
                if c == dst_name:
                    dst_alias = a; break
        if not src_alias or not dst_alias:
            continue
        dsl_lines.append(rel_line(src_alias, dst_alias, rel))

    dsl_lines.append("  }")
    dsl_lines.append("  views {")
    for sys_obj in systems:
        name = sys_obj.get("name") or "System"
        alias = system_alias[name]
        dsl_lines.append(f"    systemContext {alias} \"{name} - System Context\" {")
        dsl_lines.append("      include *")
        dsl_lines.append("      autolayout lr")
        dsl_lines.append("    }")
        dsl_lines.append(f"    container {alias} \"{name} - Containers\" {")
        dsl_lines.append("      include *")
        dsl_lines.append("      autolayout lr")
        dsl_lines.append("    }")
    dsl_lines.append("    styles {")
    dsl_lines.append("      element \"Software System\" { background #1168bd color #ffffff }")
    dsl_lines.append("      element \"Container\" { background #438dd5 color #ffffff }")
    dsl_lines.append("      element \"Component\" { background #85bbf0 color #000000 }")
    dsl_lines.append("      element \"External\" { background #999999 color #ffffff }")
    dsl_lines.append("    }")
    dsl_lines.append("  }")
    dsl_lines.append("}")

    return "\n".join(dsl_lines)


