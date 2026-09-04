"""Resolve teacher-friendly bond labels to deterministic RDKit bond indices."""
from __future__ import annotations

from rdkit import Chem


def resolve_bond_indices(mol: Chem.Mol, descriptions: list[str]) -> list[int]:
    requested = {description.upper().replace(" ", "") for description in descriptions}
    resolved: list[int] = []
    for bond in mol.GetBonds():
        first = bond.GetBeginAtom()
        second = bond.GetEndAtom()
        symbols = f"{first.GetSymbol()}-{second.GetSymbol()}".upper()
        reverse = f"{second.GetSymbol()}-{first.GetSymbol()}".upper()
        aliases = {symbols, reverse}
        # Hydroxyl is rendered by RDKit as a C-O bond whose oxygen carries H.
        if {first.GetSymbol(), second.GetSymbol()} == {"C", "O"}:
            oxygen = first if first.GetSymbol() == "O" else second
            if oxygen.GetTotalNumHs() > 0:
                aliases.update({"C-OH", "OH-C"})
        if requested.intersection(aliases):
            resolved.append(bond.GetIdx())
    return resolved
