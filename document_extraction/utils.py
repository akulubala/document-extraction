import environ, os

def loadEnv():
    env = environ.Env()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(BASE_DIR, '.env')):
        environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    elif os.path.exists('/run/secrets/booking_v2_env'):
        environ.Env.read_env('/run/secrets/booking_v2_env')
    else:
        raise Exception("No .env file or secrets file found.")
    return env