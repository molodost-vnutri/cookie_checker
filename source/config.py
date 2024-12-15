from typing import Optional, Literal, Union, Tuple
from pathlib import Path

from regex import compile
from loguru import logger
from pydantic import BaseModel, field_validator, ValidationInfo, HttpUrl, FilePath, PositiveInt
from pydantic_settings import BaseSettings

class ParseModel(BaseModel):
    name: str
    field_param: Literal["regex", "html.parser"]
    field_parse: Union[str, Tuple[str, str]]

    @field_validator("field_parse")
    def validate_param(cls, v: Union[str, Tuple[str, str]], info: ValidationInfo):
        field_param = info.data.get("field_param")
        
        if field_param == "regex":
            if isinstance(v, str):
                try:
                    compile(v)
                    return v
                except Exception as e:
                    raise ValueError("Указано не регулярное выражение") from e
            else:
                raise ValueError("field_parse должно быть строкой для regex.")
        
        elif field_param == "html.parser":
            if isinstance(v, tuple):
                if all(isinstance(x, str) for x in v):
                    return v
                else:
                    raise ValueError('Аргументы должны быть строками example ["arg_one", "arg_two"]')
            else:
                raise ValueError('field_parse должно быть кортежем для html.parse.')

        return v

class ServiceModel(BaseModel):
    cookie_name: list[str]
    url: HttpUrl
    method: Literal["get", "post"]
    validation_type: Literal["html.parser", "regex", "text"]
    validator: Union[str, Tuple[str, str], list[str]]
    headers: Optional[dict]
    parse_data: Optional[list[ParseModel]]
    log_path: Optional[str] = None

    @field_validator('validator')
    def validation_method_search(cls, v: Union[str, Tuple[str, str]], info: ValidationInfo):
        validator = info.data.get('validation_type')
        if isinstance(v, tuple) and validator == "html.parser":
            if not any(isinstance(x, str) for x in v):
                raise ValueError('Аргументы должны быть строками example ["arg_one", "arg_two"]')
            return v
        if validator == "regex":
            try:
                compile(v)
                return v
            except Exception as e:
                raise e
        if validator == "text":
            if isinstance(v, list):
                return v
        raise ValueError("Указан не html.parse тег")


    @property
    def hostname(self):
        return self.url.host


class Config(BaseSettings):
    services: list[ServiceModel]
    proxy_type: Optional[Literal["http", "https", "socks4", "socks5", "auto", "off"]]
    proxy_path: Optional[FilePath]
    save_to: Literal["sqlite", "file"]
    path: str
    threads: PositiveInt

    @field_validator("proxy_path")
    def validator_proxy_path(cls, v, info: ValidationInfo):
        if not v and info.data.get("proxy_type") != "off":
            raise ValueError("Не указан путь до прокси")
        return v


    @field_validator("path")
    def validator_type_save(cls, v: str, info: ValidationInfo):
        save_to = info.data.get('save_to')
        if save_to == "sqlite" and not v.endswith("db"):
            raise ValueError("База данных должна заканчиваться на .db")
        if save_to == "file":
            path = Path(v)
            try:
                if not path.is_dir():
                    path.mkdir()
            except Exception as e:
                raise e
        return v


def loading_config():
    try:
        with open('config.json', encoding='utf-8', errors='ignore') as file:
            return Config.model_validate_json(json_data=file.read())
    except Exception as e:
        logger.error(e)
        exit()

config = loading_config()
