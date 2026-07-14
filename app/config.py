class Config:
    def __init__(self):
        self.db_file_name = "database.db"
        self.db_url = f"sqlite:///{self.db_file_name}"
        self.db_connect_args = { "check_same_thread": False }

config = Config()