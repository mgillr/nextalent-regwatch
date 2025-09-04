#!/bin/bash

# Remove diagnostic and temporary files
rm -f 0_update-regwatch.txt
rm -f analyze_feeds_and_fix_dates.py
rm -f check_feed_discovery.py
rm -f check_github_actions.py
rm -f check_specific_feeds.py
rm -f debug_classification.py
rm -f debug_feeds.py
rm -f generate_live_output.py
rm -f generate_live_output_from_config.py
rm -f generate_real_output.py
rm -f generate_simple_live_output.py
rm -f generate_test_output.py
rm -f improved_classification.py
rm -f monitor_workflow.sh
rm -f monitor_workflow2.sh
rm -f quick_diagnostic.py
rm -f refine_tech_focus.py
rm -f regwatch_diagnostic.py
rm -f regwatch_improved.py
rm -f test_classification.py
rm -f test_classification_only.py
rm -f test_feed.py
rm -f test_regwatch.py
rm -f test_sources.py
rm -rf runner-diagnostic-logs
rm -rf update-regwatch
rm -f workflow_logs.txt
rm -f workflow_logs.zip

# Remove test directory if it's not essential
rm -rf tests

# Git add the removals
git add -A

# Commit the changes
git commit -m "Clean up repository: Remove diagnostic and temporary files"

# Delete merged branches
git branch -d enhance-filtering fix-pages-environment fix-workflow fix-workflow-pull-before-push fix-workflow-stash-changes fix-workflow-temp gh-pages-update gh-pages-update-filtering gh-pages-update-fixed-dates gh-pages-update-live gh-pages-update-tech-focus optimize-keywords strict-iso-filtering update-sources add-infotech-deeptech-sections 2>/dev/null || true

# Push changes
git push origin master
