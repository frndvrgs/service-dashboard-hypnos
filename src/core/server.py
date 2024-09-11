import grpc
from concurrent import futures
from . import audit_pb2, audit_pb2_grpc
from services import (
    DumpSourceCodeService,
    AnalyzeSourceCodeService,
    WatchPullRequestsService,
    AnalyzePullRequestService,
)
import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")

from . import audit_pb2 as audit__pb2


class AuditServicer(audit_pb2_grpc.AuditServiceServicer):
    def __init__(self):
        self.dump_service = DumpSourceCodeService()
        self.analyze_source_code_service = AnalyzeSourceCodeService(api_key=LLM_API_KEY)
        self.analyze_source_pull_request_service = AnalyzePullRequestService(
            api_key=LLM_API_KEY
        )
        self.watch_service = WatchPullRequestsService()
        self.active_processes = {}

    async def DumpSourceCode(self, request, context):
        self.active_processes[request.id_work] = self.dump_service
        try:
            async for response in self.dump_service.process(
                request.id_work, request.id_repository, request.github_token
            ):
                yield audit_pb2.DumpSourceCodeResponse(**response)
        finally:
            del self.active_processes[request.id_work]

    async def AnalyzeSourceCode(self, request, context):
        self.active_processes[request.id_work] = self.analyze_source_code_service
        try:
            async for response in self.analyze_source_code_service.process(
                request.id_work, request.id_repository, request.code_dump
            ):
                yield audit_pb2.AnalyzeSourceCodeResponse(**response)
        finally:
            del self.active_processes[request.id_work]

    async def AnalyzePullRequest(self, request, context):
        self.active_processes[request.id_work] = (
            self.analyze_source_pull_request_service
        )
        try:
            async for response in self.analyze_source_pull_request_service.process(
                request.id_work,
                request.id_repository,
                request.id_pull_request,
                request.code_dump,
            ):
                yield audit_pb2.AnalyzePullRequestResponse(**response)
        finally:
            del self.active_processes[request.id_work]

    async def WatchPullRequests(self, request, context):
        self.active_processes[request.id_work] = self.watch_service
        try:
            async for response in self.watch_service.process(
                request.id_work,
                request.id_repository,
                request.code_dump,
                request.github_token,
            ):
                yield audit_pb2.WatchPullRequestsResponse(**response)
        finally:
            del self.active_processes[request.id_work]

    async def InterruptProcess(self, request, context):
        if request.id_work in self.active_processes:
            self.active_processes[request.id_work].interrupt()
            return audit_pb2.InterruptProcessResponse(
                id_work=request.id_work, success=True
            )
        return audit_pb2.InterruptProcessResponse(
            id_work=request.id_work, success=False
        )


async def serve(host, port):
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    audit_pb2_grpc.add_AuditServiceServicer_to_server(AuditServicer(), server)
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    await server.start()
    return server
