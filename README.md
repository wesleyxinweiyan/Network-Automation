# Network Automation

An Ansible-based network automation project for Cisco IOS-XE switches, designed to automate software upgrades, collect network state, and validate changes before and after maintenance operations.

## Overview

This project uses **Ansible**, **Cisco pyATS/Genie**, **Git Diff**, and **DeepDiff** to simplify Cisco IOS-XE switch maintenance and provide structured pre-change and post-change comparisons.

### Key Features

- **Precheck** — Collect running configurations and network operational data before maintenance.
- **Image Staging** — Transfer Cisco IOS-XE software images to switches.
- **IOS-XE Upgrade** — Execute software installation commands and verify the target software version.
- **Postcheck** — Collect running configurations and network state after maintenance.
- **Configuration Comparison** — Compare running configurations using Git Diff.
- **Network State Comparison** — Compare structured operational data using DeepDiff.
- **Multi-device Support** — Manage switches through Ansible Inventory.

## Project Structure

```text
Network-Automation/
├── ansible.cfg
├── inventory.ini
├── requirements.txt
├── collections-requirements.yml
├── .gitignore
│
├── playbook/
│   ├── ios_upgrade/
│   │   ├── main.yml
│   │   ├── 01_precheck.yml
│   │   ├── 02_stage_image.yml
│   │   ├── 03_install.yml
│   │   ├── 04_postcheck.yml
│   │   └── test.yml
│   ├── tasks/
│   │   └── cisco_state_collection.yml
│   ├── backup.yml
│   └── configration_compare/
│       └── cisco_iosxe_restart.yml
│
├── script/
│   └── compare_json.py
│
├── var/
│   └── ios_upgrade.yml
│
└── backup/
```

Some directories and local configuration files may be excluded from version control for security reasons.

## Requirements

- Linux or macOS as the Ansible Controller
- Python 3 and pip
- Git
- SSH connectivity to supported Cisco IOS-XE switches
- Appropriate privilege-level access on managed devices
- Sufficient storage and a validated, compatible IOS-XE software image

### Python Dependencies

Dependencies are managed through `requirements.txt`.

Key libraries include:

- Ansible Core
- Cisco pyATS
- Cisco Genie Parser
- DeepDiff

### Ansible Collections

The project requires:

- `cisco.ios`
- `ansible.netcommon`
- `ansible.utils`

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:wesleyxinweiyan/Network-Automation.git
cd Network-Automation
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install Ansible Collections

```bash
ansible-galaxy collection install -r collections-requirements.yml
```

### 5. Verify the Environment

```bash
ansible --version
python -m pip check
```

Check the Genie Parser and DeepDiff imports:

```bash
python -c "import pyats, genie, genie.libs.parser; from deepdiff import DeepDiff; print('Dependencies OK')"
```

## Configuration

### Inventory

Configure the target switches in `inventory.ini`.

Example:

```ini
[ios]
SW01 ansible_host=192.0.2.10
SW02 ansible_host=192.0.2.11

[ios:vars]
ansible_connection=ansible.netcommon.network_cli
ansible_network_os=cisco.ios.ios
ansible_user=your_username
ansible_become=true
ansible_become_method=enable
```

Replace the example addresses and username with your own environment details.

Use Ansible Vault or another secure credential-management mechanism for passwords and privilege escalation secrets.

### Upgrade Variables

Create the local file:

```text
var/ios_upgrade.yml
```

Example:

```yaml
---
target_image: "your-iosxe-image.bin"
target_ios_ver: "your-target-version"
```

The exact variable values must match the target platform, IOS-XE software release, and supported upgrade procedure.

## Usage

### Precheck

Collect network state and running configuration before upgrading:

```bash
ansible-playbook -i inventory.ini playbook/ios_upgrade/01_precheck.yml
```

### Stage Software Image

```bash
ansible-playbook -i inventory.ini playbook/ios_upgrade/02_stage_image.yml
```

### Install IOS-XE Software

```bash
ansible-playbook -i inventory.ini playbook/ios_upgrade/03_install.yml
```

**Warning:** The installation Playbook can initiate software installation and device reloads. Run it only during an approved maintenance window after verifying the image, platform compatibility, device readiness, and recovery procedures.

### Postcheck

```bash
ansible-playbook -i inventory.ini playbook/ios_upgrade/04_postcheck.yml
```

### Full Upgrade Workflow

The main Playbook imports the individual workflow Playbooks in sequence:

```bash
ansible-playbook -i inventory.ini playbook/ios_upgrade/main.yml
```

**Warning:** This command can execute the complete upgrade workflow, including image installation and reload. Do not use it simply to test the Python environment.

## Network State Collection

The project uses Cisco Genie Parser through Ansible to transform CLI output into structured data.

Operational checks may include:

| Network State | Cisco CLI Command |
|---|---|
| IS-IS Neighbors | `show isis neighbors` |
| IPv4 Routing Table | `show ip route` |
| MAC Address Table | `show mac address-table` |
| CDP Neighbors | `show cdp neighbors` |
| LLDP Neighbors | `show lldp neighbors` |

The exact commands depend on the active Playbook, device capabilities, and supported Genie parsers.

Example:

```yaml
- name: Collect MAC address table
  ansible.utils.cli_parse:
    command: show mac address-table
    parser:
      name: ansible.netcommon.pyats
      os: iosxe
  register: mac_result
```

The parsed data is available through:

```yaml
mac_result.parsed
```

## Configuration Comparison — Git Diff

Running configurations are captured before and after maintenance.

Git Diff can compare both files without requiring them to be tracked by Git:

```bash
git diff --no-index -- before.cfg after.cfg
```

Exit codes:

- `0` — No differences
- `1` — Differences detected
- Greater than `1` — Execution error

Configuration differences are saved as a `.diff` report for review.

## Network State Comparison — DeepDiff

The project uses Python DeepDiff to recursively compare structured JSON snapshots collected before and after maintenance.

Example workflow:

```text
Before Maintenance
      |
      v
before.json
      |
      |         After Maintenance
      |                |
      |                v
      |            after.json
      |                |
      +-------+--------+
              |
              v
         DeepDiff
              |
              v
     network_state.diff.json
```

The comparison can identify:

- Added or removed neighbors
- Routing-table changes
- MAC address-table changes
- Changes in structured network operational data

**Important:** Detected differences do not automatically indicate a failed upgrade. Dynamic routing entries, neighbor timers, and learned MAC addresses may change naturally during maintenance.

Critical network-state checks should use explicit validation rules and account for convergence time.

## Security

- Do not commit credentials, private SSH keys, or sensitive network configuration backups.
- Use `.gitignore` to exclude local secrets and generated snapshots.
- Use Ansible Vault or an approved secrets manager.
- Review `git status` before committing changes.
- Restrict access to backup files and comparison reports.
- Use a private GitHub repository when the project contains internal infrastructure details.
- Validate upgrade procedures in a lab before production use.

## Development Workflow

Make changes on the development machine:

```bash
git add .
git commit -m "Update network automation"
git push
```

Update the project on the Linux Ansible Controller:

```bash
git pull --ff-only
```

If dependencies have changed, reinstall them from the dependency files.

## Future Improvements

- Structured health-check reports
- Network state normalization
- Policy-based PASS / FAIL validation
- Additional switch platform support
- Automated upgrade readiness checks
- Integration with CI/CD pipelines

## Disclaimer

This project is intended for network automation development and controlled maintenance operations. Always validate platform-specific IOS-XE upgrade procedures and ensure appropriate backup and recovery plans are available before executing changes on production equipment.