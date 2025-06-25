import importlib.util
import sys

USER_APP_FILE = "main.py"
MODULE_NAME = "main"

spec = importlib.util.spec_from_file_location(MODULE_NAME, USER_APP_FILE)
main_app = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = main_app
spec.loader.exec_module(main_app)

if hasattr(main_app, 'app'):
    main_app.app.run(host='0.0.0.0', port=3000)
else:
    print("Error: Flask app instance not found in main.py")
