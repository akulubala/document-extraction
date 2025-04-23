import environ, os

def loadEnv():
    env = environ.Env()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(BASE_DIR, '.env')):
        environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    elif os.path.exists('/run/secrets/booking_v2_ai_env'):
        environ.Env.read_env('/run/secrets/booking_v2_ai_env')
    else:
        raise Exception("No .env file or secrets file found.")
    return env


env = loadEnv()

OPENAI_API_KEY = env.str('OPENAI_API_KEY')
BASE_DOCUMENT_PATH = env.str('BASE_DOCUMENT_PATH', '/code/booking_v2/mediafiles/extract-files/')