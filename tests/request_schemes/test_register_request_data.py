import pytest

from app.request_schemes.register_request_data import RegisterRequestData

pytestmark = pytest.mark.asyncio


class TestRegisterRequestData:
    @pytest.mark.parametrize("data", [
        {'eventType': ''},
        {'eventType': '', 'repository': ''},
        {'eventType': '', 'repository': '', 'jobName': ''},
        {'eventType': '', 'repository': '', 'jobName': '', 'labels': ''},
        {'eventType': '', 'repository': '', 'jobName': '', 'labels': '', 'jenkins_url': ''}
    ])
    async def test__when_data_does_not_have_mandatory_keys__should_not_be_valid(self, data):
        assert not RegisterRequestData.is_valid_register_request_data(data)

    async def test__when_data_has_mandatory_keys__and_no_requested_params__should_be_valid(self):
        data = {'eventType': '', 'repository': '', 'jobName': '', 'labels': [], 'requested_params': [], 'jenkins_url': ''}
        assert RegisterRequestData.is_valid_register_request_data(data)

    async def test__when_data_has_mandatory_keys__and_valid_requested_params__should_be_valid(self):
        data = {'eventType': '', 'repository': '', 'jobName': '', 'labels': [],
                'requested_params': ['branch', 'sha', 'tag', 'changes', 'pr_url', 'who', 'release_target', 'is_prerelease'], 'jenkins_url': ''}
        assert RegisterRequestData.is_valid_register_request_data(data)

    async def test__when_data_has_mandatory_keys__but_invalid_requested_params__should_not_be_valid(self):
        data = {'eventType': '', 'repository': '', 'jobName': '', 'labels': [],
                'requested_params': ['branch', 'SHA', 'TAG', 'IsPrerelease'], 'jenkins_url': ''}
        assert not RegisterRequestData.is_valid_register_request_data(data)

    async def test__when_data_has_mandatory_keys__and_requested_params_start_with_proper_prefixes__should_be_valid(self):
        data = {'eventType': '', 'repository': '', 'jobName': '', 'labels': [], 'requested_params': ['branch:customBranch',
                                                                                                     'sha:customSha',
                                                                                                     'tag:customTag',
                                                                                                     'changes:customChanges',
                                                                                                     'release_target:customRelease',
                                                                                                     'is_prerelease:PreRelease',
                                                                                                     'who:Label',
                                                                                                     'pr_url:url'],
                'jenkins_url': ''}
        assert RegisterRequestData.is_valid_register_request_data(data)

    async def test__when_data_has_mandatory_keys__and_requested_params_not_start_with_proper_prefixes__should_not_be_valid(self):
        data = {'eventType': '', 'repository': '', 'jobName': '', 'labels': [], 'requested_params': ['branch/customBranch',
                                                                                                     'sha\customSha',
                                                                                                     'tag@customTag',
                                                                                                     'changescustomChanges',
                                                                                                     'release_targetReleaseTarget',
                                                                                                     'isPrerelease',
                                                                                                     'who',
                                                                                                     'pr:url'],
                'jenkins_url': ''}
        assert not RegisterRequestData.is_valid_register_request_data(data)
