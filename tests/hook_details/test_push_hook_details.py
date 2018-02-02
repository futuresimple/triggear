import pytest
from mockito import mock, expect

from app.clients.github_client import GithubClient
from app.enums.event_types import EventType
from app.hook_details.push_hook_details import PushHookDetails
from app.mongo.registration_cursor import RegistrationCursor
from tests.async_mockito import async_value

pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures('unstub')
class TestPushHookDetails:
    async def test__repr(self):
        assert f"{PushHookDetails('repo', 'master', '123321', {'README.md'})}" \
               == "<PushHookDetails repository: repo, branch: master, sha: 123321, changes: {'README.md'} >"

    async def test__get_query(self):
        assert PushHookDetails('repo', 'master', '123321', {'README.md'}).get_query() == {'repository': 'repo'}

    async def test__get_allowed_parameters(self):
        assert PushHookDetails('repo', 'master', '123321', {'README.md'}).get_allowed_parameters() \
               == {'branch': 'master', 'sha': '123321', 'changes': 'README.md'}

    async def test__get_ref(self):
        assert PushHookDetails('repo', 'master', '123321', {'README.md'}).get_ref() == '123321'

    async def test__setup_final_params(self):
        registration_cursor = mock({'change_restrictions': ['.gitignore']}, spec=RegistrationCursor, strict=True)
        push_hook_details = PushHookDetails('repo', 'master', '123321', {'README.md'})
        push_hook_details.setup_final_param_values(registration_cursor)
        assert push_hook_details.changes == set()

        registration_cursor = mock({'change_restrictions': ['README.md']}, spec=RegistrationCursor, strict=True)
        push_hook_details = PushHookDetails('repo', 'master', '123321', {'README.md', '.gitignore'})
        push_hook_details.setup_final_param_values(registration_cursor)
        assert push_hook_details.changes == {'README.md'}

    async def test__should_trigger__with_file_restrictions(self):
        github_client = mock(spec=GithubClient, strict=True)

        registration_cursor = mock({'file_restrictions': [], 'branch_restrictions': [], 'change_restrictions': []},
                                   spec=RegistrationCursor, strict=True)
        assert await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

        registration_cursor = mock({'file_restrictions': ['README.md'], 'branch_restrictions': [], 'change_restrictions': []},
                                   spec=RegistrationCursor, strict=True)
        expect(github_client).are_files_in_repo('repo', '123321', ['README.md']).thenReturn(async_value(False))
        assert not await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

        registration_cursor = mock({'file_restrictions': ['README.md'], 'branch_restrictions': [], 'change_restrictions': []},
                                   spec=RegistrationCursor, strict=True)
        expect(github_client).are_files_in_repo('repo', '123321', ['README.md']).thenReturn(async_value(True))
        assert await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

    async def test__should_trigger__with_branch_restrictions(self):
        github_client = mock(spec=GithubClient, strict=True)

        registration_cursor = mock({'file_restrictions': [], 'branch_restrictions': ['master', 'staging'], 'change_restrictions': []},
                                   spec=RegistrationCursor, strict=True)
        assert await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

        registration_cursor = mock({'file_restrictions': [], 'branch_restrictions': ['sandbox', 'staging'], 'change_restrictions': []},
                                   spec=RegistrationCursor, strict=True)
        assert not await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

    async def test__should_trigger__with_change_restrictions(self):
        github_client = mock(spec=GithubClient, strict=True)

        registration_cursor = mock({'file_restrictions': [], 'branch_restrictions': [], 'change_restrictions': ['README']},
                                   spec=RegistrationCursor, strict=True)
        assert await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

        registration_cursor = mock({'file_restrictions': [], 'branch_restrictions': [], 'change_restrictions': ['readme.md']},
                                   spec=RegistrationCursor, strict=True)
        assert not await PushHookDetails('repo', 'master', '123321', {'README.md'}).should_trigger(registration_cursor, github_client)

    async def test__get_event_type(self):
        assert PushHookDetails('repo', 'master', '123321', {'README.md'}).get_event_type() == EventType.PUSH
