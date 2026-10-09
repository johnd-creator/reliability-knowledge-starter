"""Public-code release manifest. Checksums are integrity, not signed approval."""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import argparse, json, os, re, subprocess

APP_ROOT = Path(__file__).resolve().parents[2]


def artifact_files(root):
    root = Path(root)
    paths = {"pyproject.toml"}
    paths.update(p.relative_to(root).as_posix() for p in (root/"src").rglob("*.py"))
    paths.update(p.relative_to(root).as_posix() for p in (root/"application-migrations").glob("*.sql"))
    return paths


def verify_release(manifest, root):
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version","source_sha","files"}
            or manifest["schema_version"] != "1.0"
            or not re.fullmatch("[a-f0-9]{40}", manifest["source_sha"])
            or not isinstance(manifest["files"], dict) or not 1 <= len(manifest["files"]) <= 512):
        raise ValueError("RELEASE_MANIFEST_INVALID")
    root = Path(root).resolve()
    if set(manifest["files"]) != artifact_files(root):
        raise ValueError("RELEASE_ARTIFACT_INVENTORY_MISMATCH")
    for name, checksum in manifest["files"].items():
        path = PurePosixPath(name)
        allowed = (name == "pyproject.toml" or (name.startswith("src/") and name.endswith(".py"))
                   or (name.startswith("application-migrations/") and name.endswith(".sql")))
        if (not allowed or path.is_absolute() or any(part in {"..","."} for part in path.parts)
                or not isinstance(checksum,str) or not re.fullmatch("[a-f0-9]{64}",checksum)):
            raise ValueError("RELEASE_ARTIFACT_PATH_INVALID")
        candidate = root / name
        if candidate.is_symlink() or candidate.resolve() != candidate:
            raise ValueError("RELEASE_ARTIFACT_SYMLINK_FORBIDDEN")
        if sha256(candidate.read_bytes()).hexdigest() != checksum:
            raise ValueError("RELEASE_ARTIFACT_CHECKSUM_MISMATCH")
    return manifest["source_sha"]


def make_release(root=APP_ROOT):
    root = Path(root)
    if subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip():
        raise ValueError("CLEAN_RELEASE_CHECKOUT_REQUIRED")
    sha = subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    tracked = set(subprocess.check_output(
        ["git","-C",str(root),"ls-files","--","src","application-migrations","pyproject.toml"],text=True).splitlines())
    paths = artifact_files(root)
    if not paths <= tracked:
        raise ValueError("UNTRACKED_RELEASE_ARTIFACT_FORBIDDEN")
    manifest={"schema_version":"1.0","source_sha":sha,
              "files":{name:sha256((root/name).read_bytes()).hexdigest() for name in sorted(paths)}}
    verify_release(manifest,root)
    return manifest


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,help="new private manifest path; public-code metadata only")
    args=parser.parse_args(argv)
    manifest=make_release()
    fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w") as f:
        json.dump(manifest,f,sort_keys=True,indent=2)
    print(json.dumps({"status":"RELEASE_MANIFEST_CREATED","source_sha":manifest["source_sha"],
                      "artifact_count":len(manifest["files"]),"network":0}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
