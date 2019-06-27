#!/usr/bin/env python3


from fbs_runtime.application_context.PyQt5 import ApplicationContext
from liquidswap.gui.app import main


class AppContext(ApplicationContext):
    def run(self):
        main(parse=False)
        return self.app.exec_()


if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
