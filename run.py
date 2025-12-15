# run.py
from app import create_app

app = create_app() # APENAS UMA VEZ!

if __name__ == "__main__":
    app.run(debug=True)