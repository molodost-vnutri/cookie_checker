from typing import Optional

from regex import search, compile
from bs4 import BeautifulSoup as bs
from loguru import logger

from source.services.request import RequestAPI
from source.services.writer import save_result
from source.config import ServiceModel

class Checker:
    session: RequestAPI = None
    service: ServiceModel = None
    proxy: Optional[str] = None
    def __init__(self, service: ServiceModel, proxy: Optional[str]):
        self.session = RequestAPI(headers=service.headers)
        self.service = service
        self.proxy = proxy
    
    async def checker(self):
        response = await self.session.request(method=self.service.method, url=str(self.service.url), proxy=self.proxy)
        if self.is_valid(response):
            logger.success('Куки валид')
            result = self.parse_data(response)
            if result:
                for key, value in result.items():
                    logger.success(f'Нашёл {key} с значением {value}')
            await save_result(cookie=self.service.headers.get('Cookie'), path=self.service.log_path, service=self.service.hostname, parse_data=result)
        else:
            logger.error('Куки невалид')
    def is_valid(self, response: str) -> bool:
        if self.service.validation_type == "regex":
            validator = compile(self.service.validator)
            return search(validator, response)
        if self.service.validation_type == "text":
            return any(x in response for x in self.service.validator)
        if self.service.validation_type == "html.parser":
            soup = bs(response, self.service.validation_type)
            return soup.find(self.service.validator[0], class_=self.service.validator[1])   

    def parse_data(self, response: str):
        result = {}
        if not self.service.parse_data:
            return result
        for parse_model in self.service.parse_data:
            if parse_model.field_param == "html.parser":
                soup = bs(response, parse_model.field_param)
                parse = soup.find_all(parse_model.field_parse[0], class_=parse_model.field_parse[1])
                finding = []
                if parse:
                    for parse in parse:
                        finding.append(parse.text)
                    result[parse_model.name] = finding
            if parse_model.field_param == "regex":
                regex_pattern = compile(parse_model.field_parse)
                result_regex = regex_pattern.findall(response)
                finding = []
                for res in result_regex:
                    finding.append(res)
                if finding:
                    result[parse_model.name] = finding
        return result if result else None