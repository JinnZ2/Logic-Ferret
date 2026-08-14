"""
Tests for packaging metadata and the README's factual claims.

Both of these drifted badly before: setup.py sat at version 0.1.0
calling itself "logic-ferret-gui" while schema_contract independently
declared the public surface at 1.2.0, and README.md documented a quick
start (`pip install -r requirements.txt`, `cd logic-ferret-gui/gui`)
referencing a file and a directory that do not exist.

Neither failure is detectable by running the code, which is why they
survived. These tests read the docs as claims and check them.

Run directly:
    python tests/test_packaging.py
"""
import sys, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, REPO_ROOT)

from schema_contract import SCHEMA_VERSION


def setup_py(*args):
    result = subprocess.run(
        [sys.executable, "setup.py", *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"setup.py {args} failed:\n{result.stderr}"
    return result.stdout.strip().splitlines()[-1].strip()


def read(*parts):
    return open(os.path.join(REPO_ROOT, *parts), encoding="utf-8").read()


# ----------------------------------------------------------------------
# Packaging metadata
# ----------------------------------------------------------------------

def test_version_tracks_schema_contract():
    """One version number, not two. setup.py derives it from
    SCHEMA_VERSION so the pair cannot drift apart again."""
    print("[test_version_tracks_schema_contract]")
    declared = setup_py("--version")
    assert declared == SCHEMA_VERSION, (
        f"setup.py reports {declared}, schema_contract says {SCHEMA_VERSION}"
    )
    assert declared != "0.1.0", "still pinned at the stale GUI-era version"
    print(f"  both report {declared}")
    print("  PASS")


def test_package_name_is_not_the_gui():
    print("[test_package_name_is_not_the_gui]")
    name = setup_py("--name")
    assert name == "logic-ferret", f"unexpected package name {name!r}"
    print(f"  name is {name!r}")
    print("  PASS")


def test_description_covers_the_actual_repo():
    """The description used to call the whole project a GUI."""
    print("[test_description_covers_the_actual_repo]")
    description = setup_py("--description").lower()
    assert "gui" not in description, (
        "description still presents the project as a GUI"
    )
    for term in ("sensor", "text"):
        assert term in description, f"description does not mention {term!r}"
    print("  description describes the analysis core")
    print("  PASS")


def test_quarantine_and_tests_are_not_shipped():
    print("[test_quarantine_and_tests_are_not_shipped]")
    from setuptools import find_packages

    packages = find_packages(
        where=REPO_ROOT, exclude=["tests", "tests.*", "legacy", "legacy.*"]
    )
    for unwanted in ("tests", "legacy"):
        assert unwanted not in packages, f"{unwanted}/ would be shipped"
    for wanted in ("sensor_suite", "sensor_suite.sensors", "knowledge", "practice"):
        assert wanted in packages, f"{wanted} missing from the distribution"
    print(f"  ships {sorted(packages)}")
    print("  PASS")


def test_entry_point_targets_exist():
    """A console_scripts target that does not resolve produces a command
    that installs fine and then crashes on first use."""
    print("[test_entry_point_targets_exist]")
    source = read("setup.py")
    entries = re.findall(r'"[\w-]+=([\w.]+):(\w+)"', source)
    assert entries, "no console_scripts entry points found"
    for module, func in entries:
        path = os.path.join(REPO_ROOT, module.replace(".", os.sep) + ".py")
        assert os.path.exists(path), f"entry point module {module} not found"
        assert re.search(rf"^def {func}\(", read(os.path.basename(path)), re.MULTILINE), (
            f"{module}.py has no top-level def {func}()"
        )
    print(f"  {len(entries)} entry point(s) resolve: "
          f"{', '.join(m + ':' + f for m, f in entries)}")
    print("  PASS")


def test_pep517_build_declaration_present():
    """Without pyproject.toml, pip falls back to `setup.py develop`,
    which fails on Debian/Ubuntu with AttributeError: install_layout."""
    print("[test_pep517_build_declaration_present]")
    content = read("pyproject.toml")
    assert "[build-system]" in content
    assert "setuptools.build_meta" in content
    print("  PEP 517 build backend declared")
    print("  PASS")


def test_license_metadata_matches_license_file():
    print("[test_license_metadata_matches_license_file]")
    license_text = read("LICENSE")
    source = read("setup.py")
    declared = re.search(r'^\s*license="([^"]+)"', source, re.MULTILINE)
    assert declared, "setup.py declares no license"
    if "MIT License" in license_text:
        assert declared.group(1) == "MIT", (
            f"LICENSE is MIT but setup.py declares {declared.group(1)!r}"
        )
    print(f"  LICENSE and setup.py agree on {declared.group(1)}")
    print("  PASS")


# ----------------------------------------------------------------------
# README claims
# ----------------------------------------------------------------------

def test_readme_does_not_reference_missing_paths():
    """The specific stale claims that shipped for a year."""
    print("[test_readme_does_not_reference_missing_paths]")
    readme = read("README.md")
    for phantom in ("requirements.txt", "logic-ferret-gui/gui", "gui/fallacy_gui.py"):
        assert phantom not in readme, (
            f"README references {phantom!r}, which does not exist"
        )
    print("  no references to the missing requirements.txt or gui/ dir")
    print("  PASS")


def test_readme_commands_point_at_real_files():
    """Every `python <file>` in the README must name a file that exists."""
    print("[test_readme_commands_point_at_real_files]")
    readme = read("README.md")
    scripts = set(re.findall(r"python (\S+\.py)", readme))
    assert scripts, "README documents no runnable commands"
    for script in sorted(scripts):
        assert os.path.exists(os.path.join(REPO_ROOT, script)), (
            f"README documents `python {script}` but that file does not exist"
        )
    print(f"  {len(scripts)} documented command(s) resolve: {sorted(scripts)}")
    print("  PASS")


def test_readme_describes_the_current_repo():
    """It must name the parts that actually exist now."""
    print("[test_readme_describes_the_current_repo]")
    readme = read("README.md")
    for topic in (
        "schema_contract",
        "sensor_suite",
        "practice/",
        "knowledge/",
        "legacy/",
        "run_article_check.py",
        "run_conflict_diagnosis.py",
    ):
        assert topic in readme, f"README never mentions {topic}"
    print("  README names every top-level component")
    print("  PASS")


def test_readme_states_the_sensor_limits():
    """The sensors are keyword matchers. A front door that omits that
    invites exactly the deference the repo exists to argue against."""
    print("[test_readme_states_the_sensor_limits]")
    readme = read("README.md").lower()
    assert "keyword" in readme, "README does not say the sensors match keywords"
    assert "limit" in readme, "README has no limits section"
    print("  limits stated on the front page")
    print("  PASS")


def test_referenced_internal_docs_exist():
    """Relative Markdown links in the README must resolve."""
    print("[test_referenced_internal_docs_exist]")
    readme = read("README.md")
    links = re.findall(r"\]\((?!https?://)([^)#]+)", readme)
    assert links, "README has no internal links"
    for link in sorted(set(links)):
        assert os.path.exists(os.path.join(REPO_ROOT, link)), (
            f"README links to {link}, which does not exist"
        )
    print(f"  {len(set(links))} internal link(s) resolve")
    print("  PASS")


if __name__ == "__main__":
    test_version_tracks_schema_contract()
    test_package_name_is_not_the_gui()
    test_description_covers_the_actual_repo()
    test_quarantine_and_tests_are_not_shipped()
    test_entry_point_targets_exist()
    test_pep517_build_declaration_present()
    test_license_metadata_matches_license_file()
    test_readme_does_not_reference_missing_paths()
    test_readme_commands_point_at_real_files()
    test_readme_describes_the_current_repo()
    test_readme_states_the_sensor_limits()
    test_referenced_internal_docs_exist()
    print("\nall packaging tests passed.")
