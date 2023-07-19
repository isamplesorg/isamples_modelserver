from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # The absolute path to the FastText model
    fasttext_model_path: str = "UNSET"

    # The absolute path to the BERT model
    sesar_material_model_path: str = "UNSET"
    sesar_material_config_path: str = "UNSET"
    opencontext_material_model_path: str = "UNSET"
    opencontext_material_config_path: str = "UNSET"
    opencontext_sample_model_path: str = "UNSET"
    opencontext_sample_config_path: str = "UNSET"

    class Config:
        env_file = "isamples_modelserver.env"
        case_sensitive = False
