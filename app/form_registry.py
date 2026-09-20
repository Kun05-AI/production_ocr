from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = PROJECT_ROOT / "config" / "forms" / "registry.json"


class FormRegistryError(RuntimeError):
    """Raised when the form registry/profile is invalid."""


@dataclass(frozen=True)
class FormProfile:
    form_id: str
    version: str
    config_dir: Path
    cfg: dict[str, Any]

    @property
    def reference_image(self) -> Path:
        relative = self.cfg["registration"]["reference_image"]
        return self.config_dir / relative


class FormRegistry:
    """Load and validate versioned form profiles."""

    def __init__(self, registry_file: str | Path = REGISTRY_FILE) -> None:
        self.registry_file = Path(registry_file).resolve()
        if not self.registry_file.is_file():
            raise FormRegistryError(
                f"Registry file not found:\n{self.registry_file}"
            )

        try:
            with self.registry_file.open("r", encoding="utf-8") as f:
                self.registry = json.load(f)
        except json.JSONDecodeError as exc:
            raise FormRegistryError(
                f"Invalid registry JSON: {self.registry_file}\n{exc}"
            ) from exc

        if not isinstance(self.registry, dict):
            raise FormRegistryError("registry.json root must be an object.")

        forms = self.registry.get("forms")
        if not isinstance(forms, list):
            raise FormRegistryError("registry.json must contain a 'forms' list.")

    def list_forms(self) -> list[dict[str, Any]]:
        return list(self.registry["forms"])

    def resolve(self, form_id: str, version: str) -> FormProfile:
        matches = [
            item
            for item in self.registry["forms"]
            if item.get("form_id") == form_id
            and item.get("version") == version
        ]

        if len(matches) != 1:
            raise FormRegistryError(
                f"Expected exactly one profile for {form_id}/{version}, "
                f"found {len(matches)}."
            )

        entry = matches[0]
        config_path = entry.get("config_path")
        if not isinstance(config_path, str) or not config_path.strip():
            raise FormRegistryError(
                f"Missing config_path for {form_id}/{version}."
            )

        # Registry paths are relative to config/forms/.
        forms_root = self.registry_file.parent
        config_dir = (forms_root / config_path).resolve()
        form_file = config_dir / "form.json"

        if not form_file.is_file():
            raise FormRegistryError(
                f"Form profile not found:\n{form_file}"
            )

        try:
            with form_file.open("r", encoding="utf-8") as f:
                cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise FormRegistryError(
                f"Invalid form JSON: {form_file}\n{exc}"
            ) from exc

        self._validate_profile(form_id, version, config_dir, cfg)
        return FormProfile(
            form_id=form_id,
            version=version,
            config_dir=config_dir,
            cfg=cfg,
        )

    @staticmethod
    def _validate_profile(
        form_id: str,
        version: str,
        config_dir: Path,
        cfg: dict[str, Any],
    ) -> None:
        if not isinstance(cfg, dict):
            raise FormRegistryError("form.json root must be an object.")

        if cfg.get("form_id") != form_id:
            raise FormRegistryError(
                f"form.json form_id mismatch: expected {form_id!r}, "
                f"got {cfg.get('form_id')!r}."
            )

        if cfg.get("version") != version:
            raise FormRegistryError(
                f"form.json version mismatch: expected {version!r}, "
                f"got {cfg.get('version')!r}."
            )

        page = cfg.get("page")
        registration = cfg.get("registration")
        row_strategy = cfg.get("row_strategy")

        if not isinstance(page, dict):
            raise FormRegistryError("form.json missing object: page")
        if not isinstance(registration, dict):
            raise FormRegistryError("form.json missing object: registration")
        if not isinstance(row_strategy, dict):
            raise FormRegistryError("form.json missing object: row_strategy")

        width = page.get("width")
        height = page.get("height")
        if not isinstance(width, int) or not isinstance(height, int):
            raise FormRegistryError("page.width and page.height must be integers.")

        reference_image = registration.get("reference_image")
        if not isinstance(reference_image, str):
            raise FormRegistryError(
                "registration.reference_image must be a relative path."
            )

        if not (config_dir / reference_image).is_file():
            raise FormRegistryError(
                "Reference image not found:\n"
                f"{config_dir / reference_image}"
            )

        row_count = row_strategy.get("count")
        if not isinstance(row_count, int) or row_count <= 0:
            raise FormRegistryError(
                "row_strategy.count must be a positive integer."
            )

        geometry = cfg.get("geometry", {})
        if geometry and not isinstance(geometry, dict):
            raise FormRegistryError("geometry must be an object when present.")

        # Backwards compatibility with the existing row_detector.py.
        if "page_slots" in cfg and cfg["page_slots"] != row_count:
            raise FormRegistryError(
                "page_slots must equal row_strategy.count when both are present."
            )

    def print_profile(self, form_id: str, version: str) -> None:
        profile = self.resolve(form_id, version)
        print("=" * 72)
        print("FORM PROFILE")
        print("=" * 72)
        print(f"Form ID       : {profile.form_id}")
        print(f"Version       : {profile.version}")
        print(f"Config dir    : {profile.config_dir}")
        print(f"Form JSON     : {profile.config_dir / 'form.json'}")
        print(f"Reference     : {profile.reference_image}")
        print(f"Page          : {profile.cfg['page']['width']} x {profile.cfg['page']['height']}")
        print(f"Rows          : {profile.cfg['row_strategy']['count']}")
        print(f"Registration  : {profile.cfg['registration'].get('method', 'unknown')}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a versioned form registry.")
    parser.add_argument("--form", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--registry",
        default=str(REGISTRY_FILE),
        help="Path to registry.json",
    )
    args = parser.parse_args()

    registry = FormRegistry(args.registry)
    registry.print_profile(args.form, args.version)


if __name__ == "__main__":
    main()
