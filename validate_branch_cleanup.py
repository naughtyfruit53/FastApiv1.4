#!/usr/bin/env python3
"""
Branch Cleanup Validation Script

This script validates the repository branch structure to ensure:
1. No 'master' branch exists
2. 'main' is the canonical/default branch
3. Repository follows modern Git conventions

Author: GitHub Copilot
Date: 2024
"""

import subprocess
import sys
import json
from typing import List, Dict, Any


def run_command(cmd: List[str]) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def get_local_branches() -> List[str]:
    """Get list of local branches."""
    code, stdout, stderr = run_command(["git", "branch", "--format=%(refname:short)"])
    if code != 0:
        print(f"Error getting local branches: {stderr}")
        return []
    return [branch.strip() for branch in stdout.split('\n') if branch.strip()]


def get_remote_branches() -> List[str]:
    """Get list of remote branches."""
    code, stdout, stderr = run_command(["git", "ls-remote", "--heads", "origin"])
    if code != 0:
        print(f"Error getting remote branches: {stderr}")
        return []
    branches = []
    for line in stdout.split('\n'):
        if line.strip():
            # Extract branch name from "sha refs/heads/branch-name" format
            parts = line.strip().split('\t')
            if len(parts) == 2 and parts[1].startswith('refs/heads/'):
                branch_name = parts[1].replace('refs/heads/', '')
                branches.append(branch_name)
    return branches


def get_default_branch() -> str:
    """Get the default branch from remote."""
    code, stdout, stderr = run_command(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    if code != 0:
        # Try to get from remote show origin
        code, stdout, stderr = run_command(["git", "remote", "show", "origin"])
        if code == 0:
            for line in stdout.split('\n'):
                if 'HEAD branch:' in line:
                    return line.split(':')[1].strip()
        return "unknown"
    
    # Extract branch name from refs/remotes/origin/HEAD -> origin/main format
    return stdout.replace("refs/remotes/origin/", "")


def check_master_branch_exists() -> Dict[str, Any]:
    """Check if master branch exists locally or remotely."""
    local_branches = get_local_branches()
    remote_branches = get_remote_branches()
    
    master_local = "master" in local_branches
    master_remote = any("master" in branch for branch in remote_branches)
    
    return {
        "local_master_exists": master_local,
        "remote_master_exists": master_remote,
        "local_branches": local_branches,
        "remote_branches": remote_branches
    }


def check_main_canonical() -> Dict[str, Any]:
    """Check if main is the canonical branch."""
    default_branch = get_default_branch()
    local_branches = get_local_branches()
    remote_branches = get_remote_branches()
    
    return {
        "default_branch": default_branch,
        "main_is_default": default_branch == "main",
        "has_main_branch": "main" in local_branches or "main" in remote_branches
    }


def generate_report() -> Dict[str, Any]:
    """Generate comprehensive branch analysis report."""
    master_check = check_master_branch_exists()
    main_check = check_main_canonical()
    
    # Overall assessment
    repository_compliant = (
        not master_check["local_master_exists"] and
        not master_check["remote_master_exists"] and
        main_check["main_is_default"] and
        main_check["has_main_branch"]
    )
    
    return {
        "timestamp": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], 
                                  capture_output=True, text=True).stdout.strip(),
        "repository_compliant": repository_compliant,
        "master_branch_analysis": master_check,
        "main_branch_analysis": main_check,
        "recommendations": get_recommendations(master_check, main_check),
        "summary": get_summary(repository_compliant, master_check, main_check)
    }


def get_recommendations(master_check: Dict[str, Any], main_check: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis."""
    recommendations = []
    
    if master_check["local_master_exists"]:
        recommendations.append("Delete local 'master' branch: git branch -d master")
    
    if master_check["remote_master_exists"]:
        recommendations.append("Delete remote 'master' branch: git push origin --delete master")
    
    if not main_check["main_is_default"]:
        recommendations.append("Set 'main' as default branch in repository settings")
    
    if not main_check["has_main_branch"]:
        recommendations.append("Create 'main' branch as the primary development branch")
    
    if not recommendations:
        recommendations.append("✅ Repository is properly configured - no actions needed")
    
    return recommendations


def get_summary(compliant: bool, master_check: Dict[str, Any], main_check: Dict[str, Any]) -> str:
    """Generate human-readable summary."""
    if compliant:
        return (
            "✅ COMPLIANT: Repository follows modern Git conventions with 'main' as the "
            "default branch and no 'master' branch present."
        )
    else:
        issues = []
        if master_check["local_master_exists"] or master_check["remote_master_exists"]:
            issues.append("'master' branch exists")
        if not main_check["main_is_default"]:
            issues.append("'main' is not the default branch")
        if not main_check["has_main_branch"]:
            issues.append("'main' branch does not exist")
        
        return f"❌ NON-COMPLIANT: Issues found - {', '.join(issues)}"


def main():
    """Main function to run the validation."""
    print("🔍 Repository Branch Structure Analysis")
    print("=" * 50)
    
    try:
        # Generate comprehensive report
        report = generate_report()
        
        # Display results
        print(f"\n📊 Analysis Results (as of {report['timestamp']}):")
        print(f"Status: {report['summary']}")
        
        print(f"\n🔍 Master Branch Analysis:")
        print(f"  • Local 'master' exists: {'❌ YES' if report['master_branch_analysis']['local_master_exists'] else '✅ NO'}")
        print(f"  • Remote 'master' exists: {'❌ YES' if report['master_branch_analysis']['remote_master_exists'] else '✅ NO'}")
        
        print(f"\n🎯 Main Branch Analysis:")
        print(f"  • Default branch: {report['main_branch_analysis']['default_branch']}")
        print(f"  • 'main' is default: {'✅ YES' if report['main_branch_analysis']['main_is_default'] else '❌ NO'}")
        print(f"  • 'main' branch exists: {'✅ YES' if report['main_branch_analysis']['has_main_branch'] else '❌ NO'}")
        
        print(f"\n🌿 Available Branches:")
        print(f"  • Local: {', '.join(report['master_branch_analysis']['local_branches']) if report['master_branch_analysis']['local_branches'] else 'None'}")
        print(f"  • Remote: {', '.join(report['master_branch_analysis']['remote_branches']) if report['master_branch_analysis']['remote_branches'] else 'None'}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # Save detailed report
        with open('branch_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📝 Detailed report saved to: branch_analysis_report.json")
        
        # Exit with appropriate code
        sys.exit(0 if report['repository_compliant'] else 1)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()