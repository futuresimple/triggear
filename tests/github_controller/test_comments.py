import pytest
from asynctest import MagicMock, call
from pytest_mock import MockFixture

from app.controllers.github_controller import GithubController
from app.dto.hook_details import HookDetails
from app.enums.event_types import EventTypes
from app.enums.labels import Labels

pytestmark = pytest.mark.asyncio


async def test_run_test_no_params(gh_sut: GithubController,
                                  mocker: MockFixture,
                                  mock_trigger_unregistered_jobs: MagicMock):
    pr_labels_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    hook_data = {'comment': {'body': 'Triggear run test'},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1}}

    await gh_sut.handle_comment(hook_data)

    pr_labels_mock.assert_called_once_with(1, 'test_repo')
    mock_trigger_unregistered_jobs.assert_called_once_with('test', 'test_branch', {}, 'test_repo', 1)


async def test_run_test_with_params(gh_sut: GithubController,
                                    mocker: MockFixture,
                                    mock_trigger_unregistered_jobs: MagicMock):
    pr_labels_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    hook_data = {'comment': {'body': 'Triggear run test param1=value1 param2=value2'},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1}}

    await gh_sut.handle_comment(hook_data)

    pr_labels_mock.assert_called_once_with(1, 'test_repo')
    mock_trigger_unregistered_jobs.assert_called_once_with('test', 'test_branch',
                                                           {'param1': 'value1', 'param2': 'value2'}, 'test_repo', 1)


async def test_triggear_resync_labels(gh_sut: GithubController,
                                      mocker: MockFixture,
                                      mock_trigger_registered_jobs: MagicMock):
    pr_branch_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    pr_sha_mock = mocker.patch.object(gh_sut, 'get_latest_commit_sha',
                                      return_value='sha')
    hook_data = {'comment': {'body': Labels.label_sync},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1, 'labels': [{'name': 'label1'}, {'name': 'label2'}]}}

    await gh_sut.handle_comment(hook_data)

    pr_branch_mock.assert_called_once_with(1, 'test_repo')
    pr_sha_mock.assert_called_once_with(1, 'test_repo')
    assert mock_trigger_registered_jobs.call_count == 2
    hook_details_1 = call(HookDetails(event_type=EventTypes.labeled,
                                      branch='test_branch',
                                      repository='test_repo',
                                      sha='sha',
                                      labels='label1'))
    hook_details_2 = call(HookDetails(event_type=EventTypes.labeled,
                                      branch='test_branch',
                                      repository='test_repo',
                                      sha='sha',
                                      labels='label2'))
    assert mock_trigger_registered_jobs.call_args_list[0] == hook_details_1
    assert mock_trigger_registered_jobs.call_args_list[1] == hook_details_2


async def test_triggear_resync_commit(gh_sut: GithubController,
                                      mocker: MockFixture,
                                      mock_trigger_registered_jobs: MagicMock):
    pr_branch_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    pr_sha_mock = mocker.patch.object(gh_sut, 'get_latest_commit_sha',
                                      return_value='sha')
    hook_data = {'comment': {'body': Labels.pr_sync},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1, 'labels': [{'name': 'label1'}, {'name': 'label2'}]}}

    await gh_sut.handle_comment(hook_data)

    pr_branch_mock.assert_called_once_with(1, 'test_repo')
    pr_sha_mock.assert_called_once_with(1, 'test_repo')
    assert mock_trigger_registered_jobs.call_count == 1
    calls = [call(HookDetails(event_type=EventTypes.pr_opened,
                              branch='test_branch',
                              repository='test_repo',
                              sha='sha'))]
    mock_trigger_registered_jobs.assert_has_calls(calls)


async def test_triggear_resync_no_labels(gh_sut: GithubController,
                                         mocker: MockFixture,
                                         mock_trigger_registered_jobs: MagicMock):
    pr_labels_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    hook_data = {'comment': {'body': Labels.label_sync},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1, 'labels': []}}

    await gh_sut.handle_comment(hook_data)

    pr_labels_mock.assert_called_once_with(1, 'test_repo')
    mock_trigger_registered_jobs.assert_not_called()


async def test_not_relevant_comment(gh_sut: GithubController,
                                    mocker: MockFixture,
                                    mock_trigger_registered_jobs: MagicMock):
    pr_labels_mock = mocker.patch.object(gh_sut, 'get_pr_branch',
                                         return_value='test_branch')
    hook_data = {'comment': {'body': 'Triggear do something'},
                 'repository': {'full_name': 'test_repo'},
                 'issue': {'number': 1, 'labels': []}}

    await gh_sut.handle_comment(hook_data)

    pr_labels_mock.assert_not_called()
    mock_trigger_registered_jobs.assert_not_called()