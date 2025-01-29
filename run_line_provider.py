from line_provider.app import app
from common import config
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.LINE_PROVIDER_PORT)
