import os.path
import subprocess
from datetime import date

subprocess.run(
    [
        "docker",
        "build",
        "--tag",
        "cnife/thumbnailer:latest",
        "--tag",
        f"cnife/thumbnailer:{date.today().strftime('%Y-%m-%d')}",
        os.path.dirname(__file__),
    ],
    check=True,
)
