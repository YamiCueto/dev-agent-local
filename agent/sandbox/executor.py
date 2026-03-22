import concurrent.futures
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.PrintCollector import PrintCollector


TIMEOUT_SECONDS = 10

# Builtins seguros adicionales no incluidos en safe_globals por defecto
_EXTRA_BUILTINS = {
    "sum": sum, "min": min, "max": max, "abs": abs, "round": round,
    "sorted": sorted, "reversed": reversed, "enumerate": enumerate,
    "zip": zip, "map": map, "filter": filter, "any": any, "all": all,
    "len": len, "list": list, "dict": dict, "set": set, "tuple": tuple,
    "int": int, "float": float, "str": str, "bool": bool,
    "isinstance": isinstance, "issubclass": issubclass,
    "hasattr": hasattr, "type": type, "repr": repr,
    "range": range, "chr": chr, "ord": ord, "hex": hex, "oct": oct, "bin": bin,
}


def _run_restricted(byte_code: bytes) -> str:
    """
    RestrictedPython 8.x compila print(x) como:
      _print = _print_(_getattr_)   ← factory call
      _print._call_print(x)         ← print al collector
    El collector queda en restricted_locals['_print'].
    """
    safe_builtins = {**safe_globals["__builtins__"], **_EXTRA_BUILTINS}
    restricted_globals = {
        **safe_globals,
        "_print_": PrintCollector,   # clase como factory, no instancia
        "_getiter_": iter,
        "_getattr_": getattr,
        "__builtins__": safe_builtins,
    }
    restricted_locals: dict = {}
    exec(byte_code, restricted_globals, restricted_locals)  # noqa: S102

    collector = restricted_locals.get("_print")
    return collector() if collector is not None else ""


def execute(code: str, timeout: int = TIMEOUT_SECONDS) -> dict:
    """
    Ejecuta código Python en sandbox RestrictedPython con timeout cross-platform.
    Retorna {'output': str, 'error': str | None}.
    """
    try:
        byte_code = compile_restricted(code, filename="<agent>", mode="exec")
    except SyntaxError as e:
        return {"output": "", "error": f"SyntaxError: {e}"}

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_restricted, byte_code)
        try:
            output = future.result(timeout=timeout)
            return {"output": output, "error": None}
        except concurrent.futures.TimeoutError:
            future.cancel()
            return {"output": "", "error": f"SandboxTimeoutError: execution exceeded {timeout}s"}
        except Exception as e:
            return {"output": "", "error": f"{type(e).__name__}: {e}"}
