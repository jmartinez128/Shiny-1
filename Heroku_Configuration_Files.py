# File 1: requirements.txt
shiny>=0.5.1
pandas
numpy
plotly
shinywidgets
gunicorn
python-multipart

# File 2: Procfile (no file extension)
web: gunicorn app_Jorge_Merged_version:app --timeout 120

# File 3: runtime.txt
python-3.9.18

# File 4: .gitignore
.DS_Store
__pycache__/
*.pyc
.env
build/
dist/
*.egg-info/