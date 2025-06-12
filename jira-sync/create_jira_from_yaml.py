import yaml
import subprocess

# Path to your YAML configuration file
CONFIG_PATH = "~/Workspace/mock-offseason-tools/jira-sync/jira-sync-config.yml"

# --------------------------------------------
# Run a shell command with optional output capture
# --------------------------------------------
def run(cmd, capture=False):
    print(f"> {cmd}")
    if capture:
        res = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return res.stdout.strip()
    else:
        subprocess.run(cmd, shell=True, check=True)

# --------------------------------------------
# Load YAML config (project key, teams, epics)
# --------------------------------------------
def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

# --------------------------------------------
# Create a new Epic in Jira using `jira epic create`
# Returns the epic key (e.g. NBAOFF-42)
# --------------------------------------------
def create_epic(project, label, summary, description):
    # -p = project key
    # -n = epic name (required, same as summary here)
    # -s = epic summary (appears in backlog)
    # -b = description
    # -l = label
    # --no-input = non-interactive
    cmd = (
        f"jira epic create -p {project} "
        f"-n \"{summary}\" -s \"{summary}\" -b \"{description}\" "
        f"-l {label} --no-input"
    )
    output = run(cmd, capture=True)

    # Parse and return epic key from command output
    for line in output.splitlines():
        if line.strip().startswith("Created"):
            return line.split()[-1]  # Returns something like NBAOFF-42

    raise RuntimeError(f"Failed to parse epic key from output:\n{output}")

# --------------------------------------------
# Create a task for each team linked to the given Epic
# --------------------------------------------
def create_team_tasks(project, label, epic_key, summary_prefix, teams):
    for team in teams:
        summary = f"{summary_prefix} – {team}"
        description = f"{summary_prefix} for the {team} cap sheet."

        # -p = project
        # -t = issue type (Task)
        # -s = summary
        # -b = body (description)
        # -l = label
        # -P = parent epic
        cmd = (
            f"jira issue create -p {project} -t Task "
            f"-s \"{summary}\" -b \"{description}\" "
            f"-l {label} -P {epic_key} --no-input"
        )
        run(cmd)

# --------------------------------------------
# Main entry point: load config, create epics + tasks
# --------------------------------------------
def main():
    cfg = load_config(CONFIG_PATH)
    pk = cfg["project_key"]
    lbl = cfg.get("label", "nba-sync")
    teams = cfg["teams"]

    for epic in cfg["epics"]:
        print(f"\n🛠️ Creating epic: {epic['summary']}")
        ek = create_epic(pk, lbl, epic["summary"], epic["description"])
        print(f"✔ Epic created: {ek}")
        create_team_tasks(pk, lbl, ek, epic["summary"], teams)

    print("\n✅ Done.")

# Run main program
if __name__ == "__main__":
    main()
