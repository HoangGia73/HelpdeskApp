# -*- coding: utf-8 -*-
"""IT Support Tool Suite launcher.

The UI intentionally runs as the signed-in user so Desktop, Documents,
Downloads, Chrome, and Outlook paths always belong to that user. Individual
system operations request elevation only when they need it.
"""

from .logging_config import configure_logging, install_exception_hook
from .gui import ITSupportApp


def main():
    configure_logging()
    install_exception_hook()
    app = ITSupportApp()
    app.mainloop()


if __name__ == "__main__":
    main()
