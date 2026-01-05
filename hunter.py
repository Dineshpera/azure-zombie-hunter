#!/usr/bin/env python3
"""
hunter.py
List 'zombie' (unattached) Azure Managed Disks in a subscription and estimate monthly cost.

Usage:
  python hunter.py --subscription-id <SUBSCRIPTION_ID>

Optional:
  --rate 1.50   # $ per GB per month (placeholder)
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Tuple, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient


DEFAULT_RATE_PER_GB_MONTH = 1.50


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find unattached Azure Managed Disks (zombies).")
    p.add_argument(
        "--subscription-id",
        required=True,
        help="Azure subscription ID to scan (GUID).",
    )
    p.add_argument(
        "--rate",
        type=float,
        default=DEFAULT_RATE_PER_GB_MONTH,
        help=f"Estimated $ per GB per month (default: {DEFAULT_RATE_PER_GB_MONTH}).",
    )
    return p.parse_args()


def extract_resource_group(resource_id: str) -> str:
    """
    Extract resource group name from an Azure resource ID.
    Example:
      /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/disks/<name>
    """
    if not resource_id:
        return "Unknown"
    parts = resource_id.strip("/").split("/")
    # Find "resourceGroups" and take the next segment
    for i, part in enumerate(parts):
        if part.lower() == "resourcegroups" and i + 1 < len(parts):
            return parts[i + 1]
    return "Unknown"


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def make_table(rows: List[Tuple[str, int, str, float]]) -> str:
    """
    rows: (disk_name, size_gb, resource_group, monthly_cost)
    """
    headers = ["Disk Name", "Size (GB)", "Resource Group", "Est. Monthly Cost"]
    str_rows = [
        [name, str(size), rg, format_money(cost)]
        for (name, size, rg, cost) in rows
    ]

    # Compute column widths
    cols = list(zip(*([headers] + str_rows)))
    widths = [max(len(cell) for cell in col) for col in cols]

    def line(sep: str = "-") -> str:
        return "+".join(sep * (w + 2) for w in widths).join(["+", "+"])

    def row(cells: List[str]) -> str:
        return "|" + "|".join(f" {c:<{w}} " for c, w in zip(cells, widths)) + "|"

    out = []
    out.append(line("-"))
    out.append(row(headers))
    out.append(line("="))
    for r in str_rows:
        out.append(row(r))
    out.append(line("-"))
    return "\n".join(out)


def main() -> int:
    args = parse_args()

    try:
        credential = DefaultAzureCredential()
        client = ComputeManagementClient(credential, args.subscription_id)

        zombies: List[Tuple[str, int, str, float]] = []

        # List all managed disks in the subscription
        for disk in client.disks.list():
            # disk_state can be: Attached, Unattached, Reserved, ActiveSAS, etc.
            disk_state = getattr(disk, "disk_state", None)
            if disk_state != "Unattached":
                continue

            name = disk.name or "Unnamed"
            size_gb = int(getattr(disk, "disk_size_gb", 0) or 0)
            rg = extract_resource_group(getattr(disk, "id", "") or "")
            monthly_cost = size_gb * float(args.rate)

            zombies.append((name, size_gb, rg, monthly_cost))

        if not zombies:
            print("No zombies detected. Good job!")
            return 0

        # Sort by highest estimated waste first
        zombies.sort(key=lambda x: x[3], reverse=True)

        print(make_table(zombies))
        total = sum(r[3] for r in zombies)
        print(f"\nTotal estimated monthly waste: {format_money(total)} (rate: ${args.rate:.2f}/GB-month)")
        return 0

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        print(
            "\nTips:\n"
            " - Ensure you can authenticate with DefaultAzureCredential:\n"
            "   * az login\n"
            "   * or use Managed Identity / VS Code Azure extension / environment variables\n"
            " - Verify the subscription ID is correct.\n",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
