from environs import Env


class Settings:

	def __init__(self):
		self.env = Env()
		self.env.read_env()

		self.TOKEN_API = self.env.str("TOKEN_API")
		self.ADMIN = self.env.int("ADMIN")

settings = Settings()