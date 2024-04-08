import os.path
import subprocess
from datetime import date

subprocess.run(
    [
        "docker",
        "build",
        "--tag",
        "cnife/video-thumbnail:latest",
        "--tag",
        f"cnife/video-thumbnail:{date.today().strftime('%Y-%m-%d')}",
        os.path.dirname(__file__),
    ],
    check=True,
)
