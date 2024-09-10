import grpc
import logging
from concurrent import futures
from . import audit_pb2, audit_pb2_grpc
from services import (
    DumpSourceCodeService,
    AnalyzeSourceCodeService,
    WatchPullRequestsService,
)


class AuditServicer(audit_pb2_grpc.AuditServiceServicer):
    def __init__(self):
        self.dump_service = DumpSourceCodeService()
        self.analyze_service = AnalyzeSourceCodeService()
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
        self.active_processes[request.id_work] = self.analyze_service
        try:
            async for response in self.analyze_service.process(
                request.id_work, request.id_repository, request.code_dump
            ):
                yield audit_pb2.AnalyzeSourceCodeResponse(**response)
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
