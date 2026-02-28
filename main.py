from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import shutil

app = FastAPI()


class CodeRequest(BaseModel):
    language: str
    code: str
    stdin: str = ""


@app.post("/execute")
def execute_code(request: CodeRequest):

    work_dir = tempfile.mkdtemp()
    unique_id = str(uuid.uuid4())

    try:
        # ================= PYTHON =================
        if request.language == "python":
            filename = os.path.join(work_dir, "main.py")

            with open(filename, "w") as f:
                f.write(request.code)

            cmd = ["python3", filename]

        # ================= JAVA =================
        elif request.language == "java":
            filename = os.path.join(work_dir, "Main.java")

            with open(filename, "w") as f:
                f.write(request.code)

            compile_process = subprocess.run(
                ["javac", filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # compile error
            if compile_process.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_process.stderr,
                    "exit_code": compile_process.returncode
                }

            cmd = ["java", "-cp", work_dir, "Main"]

        # ================= C =================
        elif request.language == "c":
            filename = os.path.join(work_dir, "main.c")
            exe_file = os.path.join(work_dir, "main")

            with open(filename, "w") as f:
                f.write(request.code)

            compile_process = subprocess.run(
                ["gcc", filename, "-o", exe_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if compile_process.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_process.stderr,
                    "exit_code": compile_process.returncode
                }

            cmd = [exe_file]

        # ================= CPP =================
        elif request.language == "cpp":
            filename = os.path.join(work_dir, "main.cpp")
            exe_file = os.path.join(work_dir, "main")

            with open(filename, "w") as f:
                f.write(request.code)

            compile_process = subprocess.run(
                ["g++", filename, "-o", exe_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if compile_process.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_process.stderr,
                    "exit_code": compile_process.returncode
                }

            cmd = [exe_file]

        # ================= UNSUPPORTED =================
        else:
            return {
                "stdout": "",
                "stderr": "Unsupported language",
                "exit_code": 1
            }

        # ================= RUN PROGRAM =================
        result = subprocess.run(
            cmd,
            input=request.stdin,
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

    # ================= TIMEOUT =================
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out",
            "exit_code": 124
        }

    # ================= UNKNOWN ERROR =================
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1
        }

    # ================= CLEANUP =================
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)