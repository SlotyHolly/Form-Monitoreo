from app import create_app
from app.migrate_db import migrateDb

app = create_app()

if __name__ == "__main__":
    migrateDb()
    app.run(host="0.0.0.0", port=5000, debug=True)
