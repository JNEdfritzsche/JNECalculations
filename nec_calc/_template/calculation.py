from __future__ import annotations

from typing import Any


# ----------------------------
# results helper functions
# ----------------------------
def _method_result(
    calculated_value: float,
    intermediate_value: float | None = None,
) -> dict[str, Any]:
    return {
        "calculated_value": calculated_value,
        "intermediate_value": intermediate_value,
    }


def _build_calc_result(calc: dict[str, Any], **inputs: Any) -> dict[str, Any]:
    return {
        **inputs,
        "calculated_value": calc.get("calculated_value"),
        "intermediate_value": calc.get("intermediate_value"),
    }


# ----------------------------
# calculator helper functions
# ----------------------------
def template_example_method(
    base_quantity: float,
    multiplier: float,
    adder: float,
) -> dict[str, Any]:
    intermediate_value = base_quantity * multiplier
    calculated_value = intermediate_value + adder

    return _method_result(
        calculated_value=calculated_value,
        intermediate_value=intermediate_value,
    )


# ----------------------------
# main calculator function
# ----------------------------
def calc_template(
    template_mode: str,
    base_quantity: float,
    multiplier: float,
    adder: float,
) -> dict[str, Any]:
    common_args = {
        "base_quantity": base_quantity,
        "multiplier": multiplier,
        "adder": adder,
    }

    if template_mode == "example_method":
        calc = template_example_method(**common_args)
    else:
        raise ValueError(f"Unknown template calculation mode: {template_mode}")

    return _build_calc_result(
        calc=calc,
        template_mode=template_mode,
        **common_args,
    )
