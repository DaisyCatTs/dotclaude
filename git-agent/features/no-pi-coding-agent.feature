Feature: git-agent is a Claude Code plugin only
  The git-agent tree under the Claude Code marketplace must not
  ship pi-coding-agent package surface (extensions, package.json
  pi fields, or pi install docs).

  Scenario: No pi extension surface
    Given the git-agent plugin directory
    Then there is no extensions/ directory
    And there is no package.json pi package manifest

  Scenario: No pi-coding-agent dependency strings
    Given plugin sources under git-agent/
    Then none contain "@earendil-works/pi-coding-agent"
    And none of the production sources contain pi package keywords
