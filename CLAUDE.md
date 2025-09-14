# Claude Configuration

## Development Workflow Rules

### Git Workflow
- **Before every implementation step**: Create git commit with current state
- **After every step**: Test the changes, document in relevant .md files, then commit
- **Never proceed** to next step without committing current changes
- **Commit message format**: Brief description + 🤖 Generated with [Claude Code](https://claude.ai/code)

### Testing Protocol  
- **Test every step** before moving to next one
- **Document results** in appropriate .md files
- **Update documentation** with any changes or discoveries

### Package Management
- **Always use UV** instead of pip for all Python package operations
- Commands: `uv add`, `uv remove`, `uv sync`, `uv run`

### Development Steps Execution
1. Read current step from DEVELOPMENT_STEPS.md
2. Implement the step
3. Test the implementation
4. Update relevant .md documentation
5. Git commit with descriptive message
6. Move to next step

### Git Best Practices
- **Never commit working directories** like `vystup/`, `uploads/`, `test_output/`
- **Always add to .gitignore** any directories that contain generated or temporary files
- **Use .gitignore** for build artifacts, logs, cache files, and user-specific content

This configuration ensures systematic, documented, and version-controlled development process.