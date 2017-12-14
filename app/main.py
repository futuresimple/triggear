import os

import github
import jenkins
import motor.motor_asyncio
from aiohttp import web

from app.config.triggear_config import TriggearConfig
from app.controllers.github_controller import GithubController
from app.controllers.health_controller import HealthController
from app.controllers.pipeline_controller import PipelineController


def main():
    app_config = TriggearConfig()

    gh_client = github.Github(login_or_token=app_config.github_token)
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient() if not os.environ.get('COMPOSE') == 'true' \
        else motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongodb:27017')
    jenkins_client = jenkins.Jenkins(url=app_config.jenkins_url,
                                     username=app_config.jenkins_user_id,
                                     password=app_config.jenkins_api_token)

    github_controller = GithubController(github_client=gh_client,
                                         mongo_client=mongo_client,
                                         jenkins_client=jenkins_client,
                                         config=app_config)
    pipeline_controller = PipelineController(github_client=gh_client,
                                             mongo_client=mongo_client,
                                             api_token=app_config.triggear_token)
    health_controller = HealthController(api_token=app_config.triggear_token)

    app = web.Application()
    app.router.add_post('/github', github_controller.handle_hook)
    app.router.add_post('/register', pipeline_controller.handle_register)
    app.router.add_post('/status', pipeline_controller.handle_status)
    app.router.add_post('/comment', pipeline_controller.handle_comment)
    app.router.add_get('/health', health_controller.handle_health_check)
    app.router.add_get('/missing/{eventType}', pipeline_controller.handle_missing)
    web.run_app(app)


if __name__ == "__main__":
    main()
