#!/usr/bin/env python3
"""
Report Cleanup Utility
Helps clean up old and duplicate report files to make output more intuitive.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import argparse

def get_results_directory():
    """Get the results directory path"""
    return Path(__file__).parent / "results"

def analyze_report_folders(results_dir: Path) -> Dict[str, Any]:
    """Analyze existing report folders and identify cleanup opportunities"""
    
    if not results_dir.exists():
        return {"error": "Results directory does not exist"}
    
    folders = []
    files = []
    
    for item in results_dir.iterdir():
        if item.is_dir():
            folders.append({
                "name": item.name,
                "path": str(item),
                "modified": datetime.fromtimestamp(item.stat().st_mtime),
                "size": sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            })
        elif item.is_file():
            files.append({
                "name": item.name,
                "path": str(item),
                "modified": datetime.fromtimestamp(item.stat().st_mtime),
                "size": item.stat().st_size
            })
    
    # Group folders by type
    folder_groups = {
        "discovery": [],
        "content_analysis": [],
        "competitive_intelligence": [],
        "monitoring": [],
        "dashboards": [],
        "other": []
    }
    
    for folder in folders:
        name = folder["name"]
        if name.startswith("discovery_baseline_"):
            folder_groups["discovery"].append(folder)
        elif name.startswith("content_analysis_"):
            folder_groups["content_analysis"].append(folder)
        elif name.startswith("competitive_intelligence_"):
            folder_groups["competitive_intelligence"].append(folder)
        elif name.startswith("monitoring_run_"):
            folder_groups["monitoring"].append(folder)
        elif name == "dashboards":
            folder_groups["dashboards"].append(folder)
        else:
            folder_groups["other"].append(folder)
    
    # Sort by date (newest first)
    for group in folder_groups.values():
        group.sort(key=lambda x: x["modified"], reverse=True)
    
    return {
        "total_folders": len(folders),
        "total_files": len(files),
        "folder_groups": folder_groups,
        "standalone_files": files
    }

def create_cleanup_plan(analysis: Dict[str, Any], keep_recent: int = 3) -> Dict[str, Any]:
    """Create a cleanup plan based on the analysis"""
    
    if "error" in analysis:
        return analysis
    
    cleanup_plan = {
        "folders_to_remove": [],
        "folders_to_keep": [],
        "files_to_remove": [],
        "space_to_save": 0
    }
    
    folder_groups = analysis["folder_groups"]
    
    # For each group, keep only the most recent N folders
    for group_name, folders in folder_groups.items():
        if group_name == "dashboards" or group_name == "other":
            # Keep special folders
            cleanup_plan["folders_to_keep"].extend(folders)
            continue
        
        if len(folders) <= keep_recent:
            # Keep all if we have few folders
            cleanup_plan["folders_to_keep"].extend(folders)
        else:
            # Keep recent N, remove the rest
            keep = folders[:keep_recent]
            remove = folders[keep_recent:]
            
            cleanup_plan["folders_to_keep"].extend(keep)
            cleanup_plan["folders_to_remove"].extend(remove)
            
            # Calculate space savings
            cleanup_plan["space_to_save"] += sum(f["size"] for f in remove)
    
    # Check for old standalone files that might be outdated
    for file_info in analysis["standalone_files"]:
        name = file_info["name"]
        # Remove old database files and logs that might be outdated
        if name.endswith(('.log', '.db')) and file_info["modified"] < datetime.now().replace(month=datetime.now().month-1):
            cleanup_plan["files_to_remove"].append(file_info)
            cleanup_plan["space_to_save"] += file_info["size"]
    
    return cleanup_plan

def execute_cleanup(cleanup_plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Execute the cleanup plan"""
    
    results = {
        "folders_removed": 0,
        "files_removed": 0,
        "space_saved": 0,
        "errors": []
    }
    
    if dry_run:
        print("🔍 DRY RUN - No files will be deleted")
        print("=" * 50)
    
    # Remove folders
    for folder_info in cleanup_plan["folders_to_remove"]:
        folder_path = Path(folder_info["path"])
        
        if dry_run:
            print(f"Would remove folder: {folder_info['name']} ({format_size(folder_info['size'])})")
        else:
            try:
                shutil.rmtree(folder_path)
                results["folders_removed"] += 1
                results["space_saved"] += folder_info["size"]
                print(f"✅ Removed folder: {folder_info['name']}")
            except Exception as e:
                error_msg = f"Failed to remove folder {folder_info['name']}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
    
    # Remove files
    for file_info in cleanup_plan["files_to_remove"]:
        file_path = Path(file_info["path"])
        
        if dry_run:
            print(f"Would remove file: {file_info['name']} ({format_size(file_info['size'])})")
        else:
            try:
                file_path.unlink()
                results["files_removed"] += 1
                results["space_saved"] += file_info["size"]
                print(f"✅ Removed file: {file_info['name']}")
            except Exception as e:
                error_msg = f"Failed to remove file {file_info['name']}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
    
    return results

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_latest_symlinks(results_dir: Path, analysis: Dict[str, Any]) -> None:
    """Create 'latest' symlinks for each report type"""
    
    folder_groups = analysis["folder_groups"]
    
    for group_name, folders in folder_groups.items():
        if not folders or group_name in ["dashboards", "other"]:
            continue
        
        # Get the most recent folder
        latest_folder = folders[0]
        
        # Create symlink name
        symlink_name = f"latest_{group_name}"
        symlink_path = results_dir / symlink_name
        
        # Remove existing symlink if it exists
        if symlink_path.is_symlink() or symlink_path.exists():
            try:
                symlink_path.unlink()
            except:
                pass
        
        # Create new symlink
        try:
            symlink_path.symlink_to(latest_folder["name"])
            print(f"📎 Created symlink: {symlink_name} -> {latest_folder['name']}")
        except Exception as e:
            print(f"⚠️  Failed to create symlink {symlink_name}: {str(e)}")

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Clean up GEO optimization report files")
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be deleted without actually deleting (default: True)"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the cleanup (overrides dry-run)"
    )
    
    parser.add_argument(
        "--keep-recent",
        type=int,
        default=3,
        help="Number of recent reports to keep for each type (default: 3)"
    )
    
    parser.add_argument(
        "--create-symlinks",
        action="store_true",
        help="Create 'latest' symlinks for each report type"
    )
    
    args = parser.parse_args()
    
    # Override dry_run if execute is specified
    dry_run = not args.execute
    
    print("🧹 GEO Optimization Report Cleanup Utility")
    print("=" * 50)
    
    results_dir = get_results_directory()
    
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return 1
    
    print(f"📁 Analyzing directory: {results_dir}")
    print()
    
    # Analyze current state
    analysis = analyze_report_folders(results_dir)
    
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return 1
    
    # Print current state summary
    print("📊 Current State Summary:")
    print(f"   Total folders: {analysis['total_folders']}")
    print(f"   Total files: {analysis['total_files']}")
    print()
    
    for group_name, folders in analysis["folder_groups"].items():
        if folders:
            total_size = sum(f["size"] for f in folders)
            print(f"   {group_name.replace('_', ' ').title()}: {len(folders)} folders ({format_size(total_size)})")
    
    print()
    
    # Create cleanup plan
    cleanup_plan = create_cleanup_plan(analysis, args.keep_recent)
    
    if not cleanup_plan["folders_to_remove"] and not cleanup_plan["files_to_remove"]:
        print("✨ No cleanup needed - everything looks organized!")
        
        if args.create_symlinks:
            print()
            print("📎 Creating latest symlinks...")
            create_latest_symlinks(results_dir, analysis)
        
        return 0
    
    # Show cleanup plan
    print("🗑️  Cleanup Plan:")
    print(f"   Folders to remove: {len(cleanup_plan['folders_to_remove'])}")
    print(f"   Files to remove: {len(cleanup_plan['files_to_remove'])}")
    print(f"   Space to save: {format_size(cleanup_plan['space_to_save'])}")
    print()
    
    if cleanup_plan["folders_to_remove"]:
        print("📂 Folders to be removed:")
        for folder in cleanup_plan["folders_to_remove"]:
            age_days = (datetime.now() - folder["modified"]).days
            print(f"   • {folder['name']} ({format_size(folder['size'])}, {age_days} days old)")
        print()
    
    # Execute cleanup
    results = execute_cleanup(cleanup_plan, dry_run)
    
    if dry_run:
        print()
        print("💡 To actually perform the cleanup, run with --execute")
    else:
        print()
        print("✅ Cleanup completed!")
        print(f"   Folders removed: {results['folders_removed']}")
        print(f"   Files removed: {results['files_removed']}")
        print(f"   Space saved: {format_size(results['space_saved'])}")
        
        if results["errors"]:
            print(f"   Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"     - {error}")
    
    # Create symlinks if requested
    if args.create_symlinks and not dry_run:
        print()
        print("📎 Creating latest symlinks...")
        create_latest_symlinks(results_dir, analysis)
    
    return 0

if __name__ == "__main__":
    exit(main())