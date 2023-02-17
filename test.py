from cfg.botConfig import BotConfig, OpenAiConfig

cfg = BotConfig.load_config()
cfg2 = OpenAiConfig.load_config()
print(cfg)
print(cfg2)