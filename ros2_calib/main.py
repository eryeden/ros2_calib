# MIT License
#
# Copyright (c) 2025 Institute for Automotive Engineering (ika), RWTH Aachen University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os
from datetime import datetime
import traceback
import logging

from PySide6.QtWidgets import QApplication, QMessageBox

from .main_window import MainWindow


def _setup_logging():
    """Configure app-wide logging to a file and stderr."""
    log_dir = os.path.join(os.path.expanduser("~"), ".cache", "ros2_calib")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    logger = logging.getLogger("ros2_calib")
    logger.setLevel(logging.DEBUG)
    # Avoid duplicate handlers on re-run (e.g., in dev)
    if not logger.handlers:
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger


def main():
    logger = _setup_logging()
    app = QApplication(sys.argv)

    # Install a global exception hook to capture and display any uncaught errors
    def _excepthook(exctype, value, tb):
        tb_text = "".join(traceback.format_exception(exctype, value, tb))
        # Print to stderr
        try:
            print(tb_text, file=sys.stderr)
        except Exception:
            pass

        # Persist to a log file
        try:
            log_dir = os.path.join(os.path.expanduser("~"), ".cache", "ros2_calib")
            os.makedirs(log_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = os.path.join(log_dir, f"error_{ts}.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(tb_text)
        except Exception:
            log_path = None

        # Show a simple error dialog with the head of the traceback
        head = tb_text.splitlines()[:8]
        head_text = "\n".join(head)
        if log_path:
            head_text += f"\n\nFull traceback saved to:\n{log_path}"
        try:
            QMessageBox.critical(None, "ros2_calib - Unhandled Error", head_text)
        except Exception:
            pass

    sys.excepthook = _excepthook
    # Log basic environment info
    try:
        logger.info("ros2_calib starting; argv=%s", sys.argv)
        logger.info("Python: %s", sys.version)
        logger.info("Main module path: %s", __file__)
    except Exception:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
