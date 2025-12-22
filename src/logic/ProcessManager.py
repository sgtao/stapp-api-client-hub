# ProcessManager.py
import os
import time

# import streamlit as st
import subprocess
import signal

SUBPROCESS_PROG = "src/api_server.py"


class ProcessInfo:
    def __init__(self, server_id: str, process, port: int):
        self.server_id = server_id
        self.process = process
        self.port = port
        self.start_time = time.time()


class ProcessManager:
    def __init__(self):
        self.servers: dict[str, ProcessInfo] = {}
        self.num_server = 0

    # def start_server(self, server_id: str, port: int, use_package=False):
    def start_server(self, port: int, use_package=False):
        """
        FastAPIサーバーをバックグラウンドで起動します。
        """
        # if server_id in self.servers:
        #     raise ValueError(f"Server '{server_id}' already exists")
        # --- port 重複チェック ---
        self.num_server = 0
        for info in self.servers.values():
            if port == info.port:
                raise ValueError(f"Port {port} is already in use")
            self.num_server += 1

        # --- server_id 自動採番 ---
        server_id = f"sid{self.num_server:04d}"

        try:
            # APIサーバーを起動し、プロセスをセッション状態に保存
            # command = ["python", "api_server.py", "--port", str(port)]
            command = ["python", SUBPROCESS_PROG, "--port", str(port)]
            if use_package:
                package_prog = "dist/api_server/api_server"
                command = [package_prog, "--port", str(port)]

            process = self.launch_local(command)

            self.servers[server_id] = ProcessInfo(server_id, process, port)
            # st.session_state.servers = self.servers
            # st.success(f"API Server started on port {port}")
            return True
        except Exception as e:
            # st.error(f"API Server failed to start: {e}")
            raise f"API Server failed to start: {e}"

    def stop_server(self, server_id: str):
        info = self.servers.get(server_id)
        if not info:
            raise ValueError(f"Server '{server_id}' has no info")
            # return False

        info.process.terminate()
        info.process.wait()
        del self.servers[server_id]
        return True

    def get_servers(self):
        return self.servers

    def set_servers(self, servers):
        self.servers = servers

    def get_status(self, server_id: str):
        info = self.servers.get(server_id)
        if not info:
            return None
        return {
            "server_id": server_id,
            "running": info.process.poll() is None,
            "port": info.port,
            "uptime": time.time() - info.start_time,
        }

    def list_servers(self):
        return {sid: self.get_status(sid) for sid in self.servers.keys()}

    def launch_local(self, command) -> int:
        process = subprocess.Popen(
            command,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            start_new_session=True,
        )
        # print(f"start local (pid: {process})")
        return process

    def stop_local(self, pid):
        """
        バックグラウンドで実行中のFastAPIサーバーを停止します。
        """
        # if st.session_state.api_process:
        try:
            # Windows環境とLinux環境でプロセス停止処理を場合分け
            if os.name == "nt":
                # Windows: taskkillを使用
                subprocess.run(
                    [
                        "taskkill",
                        "/F",
                        "/PID",
                        # str(st.session_state.api_process.pid),
                        str(pid),
                    ]
                )
            else:
                # Linux, macOS: プロセスグループにSIGTERMを送信
                os.killpg(
                    # os.getpgid(st.session_state.api_process.pid),
                    os.getpgid(pid),
                    signal.SIGTERM,
                )

            # st.session_state.api_process = None  # プロセスをリセット
            return True
        except Exception as e:
            raise f"Failed to stop API Server: {e}"
