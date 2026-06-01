# BrailleVision Simple Submission Folder

This is a beginner-friendly BrailleVision project folder prepared for
submission.

The project reads Braille from image files and saves:

- cropped image
- grayscale image
- mask image
- dot-center debug image
- annotated output image
- decoded text file

## Main Files

- `main.py` - run one image
- `run_all_samples.py` - run all sample images
- `requirements.txt` - Python packages
- `setup_instructions.md` - install and run steps
- `dataset_info.md` - sample image information
- `ai_tools_disclosure.md` - AI usage disclosure

## Folder Layout

```text
project/
├─ main.py
├─ run_all_samples.py
├─ requirements.txt
├─ README.md
├─ setup_instructions.md
├─ dataset_info.md
├─ ai_tools_disclosure.md
├─ sample_inputs/
├─ sample_outputs/
├─ demo/
└─ results/
```

## Quick Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py main.py
```

If PowerShell blocks activation:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

## Run All Bundled Sample Images

```powershell
py run_all_samples.py
```

This creates one output folder per image inside `sample_outputs`.

## Default Sample

The default sample used by `main.py` is:

- `sample_inputs/physical_front_view_1.jpeg`

## Important Note

This is still a simple baseline, not a high-accuracy production Braille reader.
It is strongest on:

- front-view images
- single-line Braille
- fairly clean lighting

The folder is designed to be easy to run, inspect, and explain.
