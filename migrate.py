#!/usr/bin/env python3
"""
Migration script to move existing files into project structure.

This script:
1. Moves newsletter_examples.md to project root (version controlled)
2. Copies transcript files to ./transcripts/ (git ignored)
3. Copies output files to ./outputs/ (git ignored)
4. Creates archive of originals in ~/youtube_archive/
5. Optionally removes original directories after verification
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Source directories
HOME = Path.home()
OLD_TRANSCRIPTS = HOME / "youtube_transcripts"
OLD_OUTPUTS = HOME / "youtube_outputs"

# Destination directories (relative to script location)
SCRIPT_DIR = Path(__file__).parent
NEW_TRANSCRIPTS = SCRIPT_DIR / "transcripts"
NEW_OUTPUTS = SCRIPT_DIR / "outputs"
NEWSLETTER_EXAMPLES = SCRIPT_DIR / "newsletter_examples.md"

# Archive directory
ARCHIVE_DIR = HOME / "youtube_archive"

def create_archive_backup():
    """Create timestamped archive of original directories"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_path = ARCHIVE_DIR / f"backup_{timestamp}"
    archive_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📦 Creating backup archive: {archive_path}")

    if OLD_TRANSCRIPTS.exists():
        shutil.copytree(OLD_TRANSCRIPTS, archive_path / "youtube_transcripts")
        print(f"  ✓ Backed up transcripts")

    if OLD_OUTPUTS.exists():
        shutil.copytree(OLD_OUTPUTS, archive_path / "youtube_outputs")
        print(f"  ✓ Backed up outputs")

    return archive_path

def migrate_newsletter_examples():
    """Move newsletter_examples.md to project root"""
    source = OLD_TRANSCRIPTS / "newsletter_examples.md"

    if not source.exists():
        print(f"⚠️  newsletter_examples.md not found at {source}")
        print(f"   Skipping newsletter examples migration")
        return False

    if NEWSLETTER_EXAMPLES.exists():
        print(f"⚠️  newsletter_examples.md already exists in project root")
        overwrite = input(f"   Overwrite with version from {source}? (y/n): ").strip().lower()
        if overwrite != 'y':
            print(f"   Skipping newsletter examples migration")
            return False

    shutil.copy2(source, NEWSLETTER_EXAMPLES)
    print(f"✓ Moved newsletter_examples.md to project root (will be version controlled)")
    return True

def migrate_transcripts():
    """Copy transcript files to ./transcripts/"""
    if not OLD_TRANSCRIPTS.exists():
        print(f"⚠️  Source directory not found: {OLD_TRANSCRIPTS}")
        return 0

    count = 0
    skipped = []

    for file in OLD_TRANSCRIPTS.iterdir():
        if file.is_file():
            # Skip newsletter_examples.md (handled separately)
            if file.name == "newsletter_examples.md":
                continue

            # Skip hidden files and processed tracking
            if file.name.startswith('.'):
                skipped.append(file.name)
                continue

            # Copy transcript files
            if file.suffix in ['.txt', '.md', '.json']:
                dest = NEW_TRANSCRIPTS / file.name
                shutil.copy2(file, dest)
                count += 1
                print(f"  ✓ Copied: {file.name}")

    if skipped:
        print(f"\n  Skipped hidden/system files: {', '.join(skipped)}")

    return count

def migrate_outputs():
    """Copy output directories to ./outputs/"""
    if not OLD_OUTPUTS.exists():
        print(f"⚠️  Source directory not found: {OLD_OUTPUTS}")
        return 0

    count = 0

    for item in OLD_OUTPUTS.iterdir():
        # Skip hidden files and processed tracking
        if item.name.startswith('.'):
            continue

        dest = NEW_OUTPUTS / item.name

        if item.is_file():
            shutil.copy2(item, dest)
            count += 1
            print(f"  ✓ Copied: {item.name}")
        elif item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
            count += 1
            print(f"  ✓ Copied: {item.name}/ (directory)")

    return count

def verify_migration():
    """Verify files were copied successfully"""
    print("\n🔍 Verifying migration...")

    issues = []

    # Check newsletter examples
    if NEWSLETTER_EXAMPLES.exists():
        print(f"  ✓ newsletter_examples.md in project root")
    else:
        issues.append("newsletter_examples.md not found in project root")

    # Check transcripts
    transcript_count = len(list(NEW_TRANSCRIPTS.glob('*'))) - 1  # Exclude .gitkeep
    print(f"  ✓ {transcript_count} files in ./transcripts/")

    # Check outputs
    output_count = len(list(NEW_OUTPUTS.glob('*'))) - 1  # Exclude .gitkeep
    print(f"  ✓ {output_count} items in ./outputs/")

    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print("\n✅ Migration verified successfully!")
    return True

def cleanup_originals():
    """Ask user if they want to remove original directories"""
    print("\n" + "="*60)
    print("CLEANUP OPTIONS")
    print("="*60)
    print(f"\nOriginal directories:")
    print(f"  - {OLD_TRANSCRIPTS}")
    print(f"  - {OLD_OUTPUTS}")
    print(f"\nArchive backup created at:")
    print(f"  - {ARCHIVE_DIR}")
    print(f"\nYou can safely remove the original directories now.")
    print(f"All files have been copied to the project and backed up.")

    choice = input(f"\nRemove original directories? (y/n): ").strip().lower()

    if choice == 'y':
        try:
            if OLD_TRANSCRIPTS.exists():
                shutil.rmtree(OLD_TRANSCRIPTS)
                print(f"  ✓ Removed: {OLD_TRANSCRIPTS}")

            if OLD_OUTPUTS.exists():
                shutil.rmtree(OLD_OUTPUTS)
                print(f"  ✓ Removed: {OLD_OUTPUTS}")

            print(f"\n✅ Cleanup complete!")
            print(f"   Backup available at: {ARCHIVE_DIR}")
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            print(f"   Original files remain at their locations")
            print(f"   You can manually delete them later")
    else:
        print(f"\n📁 Original directories kept at:")
        print(f"   - {OLD_TRANSCRIPTS}")
        print(f"   - {OLD_OUTPUTS}")
        print(f"   You can manually delete them when ready")

def main():
    """Main migration workflow"""
    print("="*60)
    print("🚚 First Cup Processor - Migration Script")
    print("="*60)
    print(f"\nThis script will:")
    print(f"  1. Create backup archive in ~/youtube_archive/")
    print(f"  2. Move newsletter_examples.md to project root (tracked in git)")
    print(f"  3. Copy transcript files to ./transcripts/ (ignored by git)")
    print(f"  4. Copy output files to ./outputs/ (ignored by git)")
    print(f"  5. Optionally remove original directories")

    proceed = input(f"\nProceed with migration? (y/n): ").strip().lower()
    if proceed != 'y':
        print("\n❌ Migration cancelled")
        sys.exit(0)

    # Create backup archive
    archive_path = create_archive_backup()

    # Migrate newsletter examples
    print(f"\n📝 Migrating newsletter examples...")
    migrate_newsletter_examples()

    # Migrate transcripts
    print(f"\n📄 Migrating transcript files...")
    transcript_count = migrate_transcripts()
    print(f"\n  ✓ Migrated {transcript_count} transcript files")

    # Migrate outputs
    print(f"\n📁 Migrating output files...")
    output_count = migrate_outputs()
    print(f"\n  ✓ Migrated {output_count} output items")

    # Verify migration
    if verify_migration():
        # Cleanup originals
        cleanup_originals()

        print(f"\n" + "="*60)
        print("✅ MIGRATION COMPLETE")
        print("="*60)
        print(f"\nNext steps:")
        print(f"  1. Run: python3 youtube_processor.py")
        print(f"     (Now uses ./transcripts/ and ./outputs/ by default)")
        print(f"  2. Add newsletter_examples.md to git:")
        print(f"     git add newsletter_examples.md")
        print(f"  3. Commit changes:")
        print(f"     git add config.json .gitignore transcripts/.gitkeep outputs/.gitkeep")
        print(f"     git commit -m 'feat: restructure project with config and local directories'")
    else:
        print(f"\n⚠️  Migration completed with issues. Please review above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
