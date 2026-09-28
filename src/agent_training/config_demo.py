import os
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

print(os.getenv("MY_NAME"))
print(os.getenv("AGE"))

try:
    age = int(os.getenv("AGE"))
except ValueError:
    print("AGE 配置错误")
logging.info("config loaded")
logging.warning("test warning")
logging.error("test error")
