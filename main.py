from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid

app = FastAPI()

class CodeRequest(BaseModel):
    language: str
    code: str
    stdin: str = ""

@app.post("/execute")
def execute_code(request: CodeRequest):

    unique_id = str(uuid.uuid4())
    work_dir = tempfile.mkdtemp()

    try:
        if request.language == "python":
            filename = os.path.join(work_dir, "main.py")
            with open(filename, "w") as f:
                f.write(request.code)

            cmd = ["python3", filename]

        elif request.language == "java":
            filename = os.path.join(work_dir, "Main.java")
            with open(filename, "w") as f:
                f.write(request.code)

            subprocess.run(["javac", filename], check=True)
            cmd = ["java", "-cp", work_dir, "Main"]

        elif request.language == "c":
            filename = os.path.join(work_dir, "main.c")
            exe_file = os.path.join(work_dir, "main")
            with open(filename, "w") as f:
                f.write(request.code)

            subprocess.run(["gcc", filename, "-o", exe_file], check=True)
            cmd = [exe_file]

        elif request.language == "cpp":
            filename = os.path.join(work_dir, "main.cpp")
            exe_file = os.path.join(work_dir, "main")
            with open(filename, "w") as f:
                f.write(request.code)

            subprocess.run(["g++", filename, "-o", exe_file], check=True)
            cmd = [exe_file]

        else:
            return {"error": "Unsupported language"}

        result = subprocess.run(
            cmd,
            input=request.stdin,
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}

    finally:
        subprocess.run(["rm", "-rf", work_dir])