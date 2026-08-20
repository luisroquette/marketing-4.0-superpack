#!/usr/bin/env bash
# Marketing 4.0 client kit installer.
# Runs inside the client's workspace. Installs the 5 engine skills and the
# onboarding wizard into .claude/skills/, and appends a CLAUDE.md pointer.
# Owner is overridable: MARKETING40_OWNER=myorg bash install.sh
set -euo pipefail

OWNER="${MARKETING40_OWNER:-luisroquette}"
REPOS=(
  "${OWNER}/My_LP_Makes_Neil_Proud:my-lp-makes-neil-proud"
  "${OWNER}/My_UTMs_Make_Me_Proud:my-utms-make-me-proud"
  "${OWNER}/My_MailMKT_makes_Neil_Proud:my-mailmkt-makes-neil-proud"
  "${OWNER}/My_Blog_Makes_Neil_Proud:my-blog-makes-neil-proud"
  "AgriciDaniel/claude-seo:claude-seo"
)
DEST="marketing40"
SKILLS_DIR=".claude/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIZARD_SRC="${SCRIPT_DIR}/.claude/skills/marketing40-onboarding"

if ! command -v git >/dev/null 2>&1; then
  echo "install.sh: git is required (https://git-scm.com)" >&2
  exit 1
fi

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "would create ${DEST}/"
  for entry in "${REPOS[@]}"; do
    repo="${entry%%:*}"; name="${entry##*:}"
    echo "would clone https://github.com/${repo}.git -> ${DEST}/${name}"
    echo "would copy skills from ${DEST}/${name} -> ${SKILLS_DIR}/${name}"
  done
  echo "would copy wizard ${WIZARD_SRC} -> ${SKILLS_DIR}/marketing40-onboarding"
  echo "would append CLAUDE.md pointer at repo root"
  exit 0
fi

mkdir -p "${DEST}" "${SKILLS_DIR}"
for entry in "${REPOS[@]}"; do
  repo="${entry%%:*}"; name="${entry##*:}"
  if [[ ! -d "${DEST}/${name}" ]]; then
    git clone --depth 1 "https://github.com/${repo}.git" "${DEST}/${name}"
  else
    echo "already present: ${DEST}/${name} (skipping clone)"
  fi
  if [[ -f "${DEST}/${name}/SKILL.md" ]]; then
    mkdir -p "${SKILLS_DIR}/${name}"
    for entry_path in SKILL.md references scripts assets templates; do
      if [[ -e "${DEST}/${name}/${entry_path}" ]]; then
        cp -R "${DEST}/${name}/${entry_path}" "${SKILLS_DIR}/${name}/"
      fi
    done
  fi
  if [[ -d "${DEST}/${name}/skills" ]]; then
    for skill_dir in "${DEST}/${name}"/skills/*/; do
      [[ -f "${skill_dir}SKILL.md" ]] || continue
      skill_name="$(basename "${skill_dir}")"
      rm -rf "${SKILLS_DIR}/${skill_name}"
      cp -R "${skill_dir}" "${SKILLS_DIR}/${skill_name}"
    done
  fi
  if [[ ! -f "${DEST}/${name}/SKILL.md" && ! -d "${DEST}/${name}/skills" ]]; then
    echo "warning: no SKILL.md in ${name} — engine cloned only; the wizard assembles it in Phase 5" >&2
  fi
done

if [[ -d "${WIZARD_SRC}" ]]; then
  rm -rf "${SKILLS_DIR}/marketing40-onboarding"
  cp -R "${WIZARD_SRC}" "${SKILLS_DIR}/marketing40-onboarding"
else
  echo "warning: wizard skill not found at ${WIZARD_SRC} — the pack will run without /marketing40-onboarding" >&2
fi

if ! grep -q "This workspace runs the Marketing 4.0 pack" CLAUDE.md 2>/dev/null; then
  cat >> CLAUDE.md <<'EOF'

# Marketing 4.0
This workspace runs the Marketing 4.0 pack inside Claude Code.
Start with `/marketing40-onboarding`.
EOF
fi

echo "Done. Open Claude Code in this workspace and run /marketing40-onboarding"
