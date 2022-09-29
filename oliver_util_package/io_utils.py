def get_config_data(param: str) -> dict():
    """
    Read configuration from config_file

    :param param:str in {email: 'SMTP,TELEGRAM: TELEGRAM,REAL_DB: RDS_DB,TEST_DB: TEST_DB}
    :return config_data:dict
    """
    param_dict = {
        'email': 'SMTP',
        'telegram': 'TELEGRAM',
        'readl_db': 'RDS_DB',
        'test_db': 'TEST_DB'
    }

    with open('./config_file', 'r') as f:
        config_data = param_dict[param]
        configs = f.readlines()
        config_dict = {}
        for config in configs:
            if config.startswith(config_data):
                key, value = config.rstrip().split('=')
                if key.startswith(config_data):
                    config_dict[key.strip()] = value.strip()

    return config_dict
