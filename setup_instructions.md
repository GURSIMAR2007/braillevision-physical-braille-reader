# Setup Instructions

## 1. Open the Folder

Open this folder in VS Code.

## 2. Create a Virtual Environment

```powershell
py -m venv .venv
```

## 3. Activate It

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, you can still run Python directly from the virtual
environment.

## 4. Install Packages

```powershell
py -m pip install -r requirements.txt
```

## 5. Run One Sample

```powershell
py main.py
```

## 6. Run All Samples

```powershell
py run_all_samples.py
```

## 7. Check Output Folders

- `results/`
- `sample_outputs/`
