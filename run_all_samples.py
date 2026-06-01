from pathlib import Path
import shutil

from main import process_image


SAMPLE_INPUTS = Path("sample_inputs")
SAMPLE_OUTPUTS = Path("sample_outputs")


def main() -> None:
    SAMPLE_OUTPUTS.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        [
            path
            for path in SAMPLE_INPUTS.iterdir()
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
        ]
    )

    if not image_paths:
        print("No sample images found in sample_inputs.")
        return

    for image_path in image_paths:
        output_dir = SAMPLE_OUTPUTS / image_path.stem
        if output_dir.exists():
            shutil.rmtree(output_dir)

        print(f"Running: {image_path.name}")
        process_image(image_path, output_dir)
        print(f"Saved:   {output_dir}")
        print()


if __name__ == "__main__":
    main()
