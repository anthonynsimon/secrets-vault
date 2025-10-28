import invoke


@invoke.task
def fmt(ctx, check=False):
    cmds = ["uv", "format"]
    if check:
        cmds.append("--check")
    ctx.run(" ".join(cmds))


@invoke.task
def test(ctx):
    ctx.run("rm -rf tests/test-data")
    ctx.run("mkdir -p tests/test-data")
    ctx.run("pytest -v -s")


@invoke.task
def clean(ctx):
    ctx.run("rm -rf dist")


@invoke.task(clean)
def build(ctx):
    ctx.run("uv build")


@invoke.task()
def publish(ctx, token=None):
    cmds = ["uv", "publish"]
    if token:
        cmds.extend(["--username", "__token__"])
        cmds.extend(["--password", token])
    cmds.append("dist/*")
    ctx.run(" ".join(cmds))
