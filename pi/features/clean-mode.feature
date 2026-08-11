Feature: pi clean mode for Claude Code bridge
  /pi:delegate and /pi:review must run the pi CLI without the user's
  global pi packages, extensions, or skills by default, so bridge
  tasks stay isolated from interactive pi configuration.

  Scenario: Default pi-agent command disables packages and skills
    Given the pi-agent command assembly for MODE delegate or review
    When WITH_PACKAGES is not true
    Then the assembled command includes --no-extensions
    And the assembled command includes --no-skills
    And the assembled command still includes --no-session --no-context-files --approve

  Scenario: Opt-in keeps packages and skills
    Given the pi-agent command assembly for MODE delegate or review
    When WITH_PACKAGES is true
    Then the assembled command does not include --no-extensions
    And the assembled command does not include --no-skills
    And the assembled command still includes --no-session --no-context-files --approve

  Scenario: Skills expose the escape hatch
    Given the delegate and review skill entry points
    Then --with-packages is documented as a CLI flag
    And withPackages is readable from the shared settings chain
