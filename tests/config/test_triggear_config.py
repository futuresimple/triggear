import os
from typing import Dict

import pytest
import yaml
from mockito import when

from app.config.triggear_config import TriggearConfig

pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures('unstub')
class TestTriggearConfig:
    VALID_CREDS_DATA = {
        'jenkins_url': 'URL',
        'jenkins_user_id': 'USER',
        'jenkins_api_token': 'JENKINS_TOKEN',
        'github_token': 'GITHUB_TOKEN',
        'triggear_token': 'TRIGGEAR_TOKEN'
    }

    async def test__when_creds_path_is_invalid__should_raise_file_not_found_error(self):
        when(os).getenv('CREDS_PATH').thenReturn('does/not/exist')

        with pytest.raises(FileNotFoundError) as file_not_found_error:
            TriggearConfig()
        assert str(file_not_found_error.value) == "[Errno 2] No such file or directory: 'does/not/exist'"

    @pytest.mark.parametrize("yaml_data, missing_key", [
        ({}, 'jenkins_url'),
        ({'jenkins_url': ''}, 'jenkins_user_id'),
        ({'jenkins_url': '', 'jenkins_user_id': ''}, 'jenkins_api_token'),
        ({'jenkins_url': '', 'jenkins_user_id': '', 'jenkins_api_token': ''}, 'github_token'),
        ({'jenkins_url': '', 'jenkins_user_id': '', 'jenkins_api_token': '', 'github_token': ''}, 'triggear_token')
    ])
    async def test__when_any_key_is_missing_in_creds_file__should_raise_proper_key_error(self, yaml_data: Dict, missing_key: str):
        when(os).getenv('CREDS_PATH').thenReturn('./tests/config/example_configs/creds.yaml')
        when(yaml).load(any).thenReturn(yaml_data)

        with pytest.raises(KeyError) as key_error:
            TriggearConfig()
        assert str(key_error.value) == f"'{missing_key}'"

    async def test__when_key_is_missing_in_config_file__should_set_default_timeout(self):
        when(os).getenv('CREDS_PATH').thenReturn('./tests/config/example_configs/creds.yaml')
        when(os).getenv('CONFIG_PATH').thenReturn('./tests/config/example_configs/config.yaml')
        when(yaml).load(any).thenReturn(self.VALID_CREDS_DATA).thenReturn({})

        triggear_config = TriggearConfig()

        assert triggear_config.rerun_time_limit == 30

    async def test__when_yaml_files_are_valid__should_store_proper_values(self):
        when(os).getenv('CREDS_PATH').thenReturn('./tests/config/example_configs/creds.yaml')
        when(os).getenv('CONFIG_PATH').thenReturn('./tests/config/example_configs/config.yaml')

        triggear_config = TriggearConfig()

        assert triggear_config.rerun_time_limit == 2
        assert triggear_config.RERUN_DEFAULT_TIME == 30
        assert triggear_config.triggear_token == 'TRIGGEAR_TOKEN'
        assert triggear_config.github_token == 'GITHUB_TOKEN'
        assert triggear_config.jenkins_api_token == 'JENKINS_USER_API_TOKEN'
        assert triggear_config.jenkins_url == 'http://JENKINS_URL/'
        assert triggear_config.jenkins_user_id == 'JENKINS_USER'