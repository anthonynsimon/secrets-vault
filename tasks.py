import invoke


@invoke.task
def fmt(ctx, check=False):
    cmds = ["black", "-l", "120", "-t", "py311"]
    if check:
        cmds.append("--check")
    cmds.append(".")
    ctx.run(" ".join(cmds))


@invoke.task
def test(ctx):
    ctx.run("rm -rf tests/test-data")
    ctx.run("mkdir -p tests/test-data")
    ctx.run("pytest -v -s")


@invoke.task
def test_py2_compat(ctx):
    ctx.run("docker build -f Dockerfile.py27 -t secrets-py27 . && docker run secrets-py27")


@invoke.task
def clean(ctx):
    ctx.run("rm -rf dist")
    ctx.run("python setup.py clean --all")


@invoke.task(clean)
def build(ctx):
    ctx.run("python setup.py sdist bdist_wheel")


@invoke.task()
def publish(ctx, token=None):
    cmds = ["twine", "upload"]
    if token:
        cmds.extend(["--username", "__token__"])
        cmds.extend(["--password", token])
    cmds.append("dist/*")
    ctx.run(" ".join(cmds))
