import logging
from pathlib import Path
from .bert_model import BertCRFModel


class LanEngine(object):
    def __init__(self, config) -> None:
        self.config = config
        self.log = None  # will be initialized into logger
        self._log_config()

    def _log_config(self) -> None:
        log_file = f"{self.config['prog_dir']}/output/engine.log"
        if isinstance(log_file, Path):
            log_file = str(log_file)
        log_format = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
            datefmt='%m/%d/%Y %H:%M:%S')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.handlers = [console_handler]
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        # file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        self.log = logger

    def _init_ner_network(self, model_config):
        cache_dir = f"{self.config['prog_dir']}/cache"
        self.ner_model = BertCRFModel.from_pretrained('bert-base-chinese', config=model_config, cache_dir=cache_dir)


if __name__ == "__main__":
    pass
