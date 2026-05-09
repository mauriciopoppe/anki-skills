import os
import re
import sys

def validate_skill(skill_path):
    skill_file = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        print(f"❌ Missing SKILL.md in {skill_path}")
        return False

    with open(skill_file, "r") as f:
        content = f.read()

    # Check for frontmatter
    frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        print(f"❌ Missing frontmatter in {skill_file}")
        return False

    frontmatter = frontmatter_match.group(1)
    
    # Check for name and description
    if "name:" not in frontmatter:
        print(f"❌ Missing 'name' in frontmatter: {skill_file}")
        return False
    if "description:" not in frontmatter:
        print(f"❌ Missing 'description' in frontmatter: {skill_file}")
        return False

    # Check for Markdown structure (Heading 1)
    if not re.search(r"^# .+", content, re.MULTILINE):
        print(f"❌ Missing H1 title in {skill_file}")
        return False

    # Check for Scripts directory if mentioned in content
    if "scripts/" in content:
        scripts_dir = os.path.join(skill_path, "scripts")
        if not os.path.exists(scripts_dir):
            print(f"⚠️ Mentioned 'scripts/' but directory missing in {skill_path}")
    
    print(f"✅ {os.path.basename(skill_path)} is valid")
    return True

def main():
    skills_dir = "skills"
    if not os.path.exists(skills_dir):
        print("❌ Skills directory not found")
        sys.exit(1)

    all_valid = True
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_path):
            if not validate_skill(skill_path):
                all_valid = False

    if not all_valid:
        sys.exit(1)

if __name__ == "__main__":
    main()
