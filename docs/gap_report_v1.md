# T23 Module & Documentation Inventory — Gap Report v1

Generated from `configs/module_inventory.json` by `scripts/generate_gap_report.py`.

## Summary

- **Total modules tracked:** 25
- **Documented (>= 80 bytes):** 1
- **Stub only (< 80 bytes):** 14
- **Missing:** 10

## Modules With No Substantive Documentation

| Module | Category | Owner / Lead | Phase | Status | Expected Doc(s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Perception Camera | subteam | Perception Camera Subteam (2 members) | P2 | `missing` | `docs/subteams/perception_camera.md` (missing) |
| Perception LiDAR | subteam | Perception LiDAR Subteam (3 members) | P2 | `missing` | `docs/subteams/perception_lidar.md` (missing) |
| SLAM & Localization | subteam | SLAM Subteam (3 members) | P2 | `missing` | `docs/subteams/slam.md` (missing) |
| Planning Deep Learning | subteam | Planning DL Subteam (2 members) | P3 | `missing` | `docs/subteams/planning_dl.md` (missing) |
| Planning Classical | subteam | Planning Classical Subteam (2 members) | P3 | `missing` | `docs/subteams/planning_classical.md` (missing) |
| Planning Skidpad | subteam | Planning Skidpad Subteam (2 members) | P3 | `missing` | `docs/subteams/planning_skidpad.md` (missing) |
| Control MPC | subteam | Control MPC Subteam (3 members) | P3 | `missing` | `docs/subteams/control_mpc.md` (missing) |
| Platform & Supervision Integration (PSI) | subteam | PSI Subteam (3 members) | P2 | `missing` | `docs/subteams/psi.md` (missing) |
| Continuous Integration (CI Team) | subteam | CI Team (2 members) | P1 | `missing` | `docs/subteams/ci_team.md` (missing) |
| Simulation (CARLA & Gazebo) | subteam | Simulation Subteam (4 members) | P3 | `missing` | `docs/subteams/simulation.md` (missing) |
| System Architecture Doc | agentic_package | Agentic AI Core | P1 | `stub_only` | `docs/architecture.md` (stub_only) |
| core/llm | agentic_package | Mohamed Samy | P1 | `stub_only` | `src/fsai_agents/core/llm/README.md` (stub_only) |
| core/memory | agentic_package | Amir | P1 | `stub_only` | `src/fsai_agents/core/memory/README.md` (stub_only) |
| core/observability | agentic_package | Mohamed Samy | P1 | `stub_only` | `src/fsai_agents/core/observability/README.md` (stub_only) |
| core/orchestrator | agentic_package | Agentic AI Core | P2 | `stub_only` | `src/fsai_agents/core/orchestrator/README.md` (stub_only) |
| core/policy | agentic_package | Amir | P1 | `stub_only` | `src/fsai_agents/core/policy/README.md` (stub_only) |
| core/tools | agentic_package | Mohamed Samy | P2 | `stub_only` | `src/fsai_agents/core/tools/README.md` (stub_only) |
| integrations | agentic_package | Agentic AI Core | P2 | `stub_only` | `src/fsai_agents/integrations/README.md` (stub_only) |
| modules/github_automation | agentic_package | Mohamed Samy | P4 | `stub_only` | `src/fsai_agents/modules/github_automation/README.md` (stub_only) |
| modules/ros2_ci | agentic_package | Mohamed Samy | P3 | `stub_only` | `src/fsai_agents/modules/ros2_ci/README.md` (stub_only) |
| modules/simulation_testing | agentic_package | Mohamed Samy | P3 | `stub_only` | `src/fsai_agents/modules/simulation_testing/README.md` (stub_only) |
| modules/log_monitoring | agentic_package | Mohamed Samy | P3 | `stub_only` | `src/fsai_agents/modules/log_monitoring/README.md` (stub_only) |
| modules/notion_automation | agentic_package | Amir | P4 | `stub_only` | `src/fsai_agents/modules/notion_automation/README.md` (stub_only) |
| modules/rag_chatbot | agentic_package | Amir / Omar | P2 | `stub_only` | `src/fsai_agents/modules/rag_chatbot/README.md` (stub_only) |

## Full Inventory

| Module ID | Name | Category | Status | Expected Doc(s) |
| :--- | :--- | :--- | :--- | :--- |
| `perception_camera` | Perception Camera | subteam | `missing` | `docs/subteams/perception_camera.md` (0 B) |
| `perception_lidar` | Perception LiDAR | subteam | `missing` | `docs/subteams/perception_lidar.md` (0 B) |
| `slam` | SLAM & Localization | subteam | `missing` | `docs/subteams/slam.md` (0 B) |
| `planning_dl` | Planning Deep Learning | subteam | `missing` | `docs/subteams/planning_dl.md` (0 B) |
| `planning_classical` | Planning Classical | subteam | `missing` | `docs/subteams/planning_classical.md` (0 B) |
| `planning_skidpad` | Planning Skidpad | subteam | `missing` | `docs/subteams/planning_skidpad.md` (0 B) |
| `control_mpc` | Control MPC | subteam | `missing` | `docs/subteams/control_mpc.md` (0 B) |
| `psi` | Platform & Supervision Integration (PSI) | subteam | `missing` | `docs/subteams/psi.md` (0 B) |
| `ci_team` | Continuous Integration (CI Team) | subteam | `missing` | `docs/subteams/ci_team.md` (0 B) |
| `simulation` | Simulation (CARLA & Gazebo) | subteam | `missing` | `docs/subteams/simulation.md` (0 B) |
| `agentic_ai` | Agentic AI | subteam | `documented` | `README.md` (3806 B), `docs/hardware.md` (804 B) |
| `docs_architecture` | System Architecture Doc | agentic_package | `stub_only` | `docs/architecture.md` (0 B) |
| `core_llm` | core/llm | agentic_package | `stub_only` | `src/fsai_agents/core/llm/README.md` (56 B) |
| `core_memory` | core/memory | agentic_package | `stub_only` | `src/fsai_agents/core/memory/README.md` (48 B) |
| `core_observability` | core/observability | agentic_package | `stub_only` | `src/fsai_agents/core/observability/README.md` (22 B) |
| `core_orchestrator` | core/orchestrator | agentic_package | `stub_only` | `src/fsai_agents/core/orchestrator/README.md` (65 B) |
| `core_policy` | core/policy | agentic_package | `stub_only` | `src/fsai_agents/core/policy/README.md` (50 B) |
| `core_tools` | core/tools | agentic_package | `stub_only` | `src/fsai_agents/core/tools/README.md` (63 B) |
| `integrations` | integrations | agentic_package | `stub_only` | `src/fsai_agents/integrations/README.md` (56 B) |
| `github_automation` | modules/github_automation | agentic_package | `stub_only` | `src/fsai_agents/modules/github_automation/README.md` (0 B) |
| `ros2_ci` | modules/ros2_ci | agentic_package | `stub_only` | `src/fsai_agents/modules/ros2_ci/README.md` (0 B) |
| `simulation_testing` | modules/simulation_testing | agentic_package | `stub_only` | `src/fsai_agents/modules/simulation_testing/README.md` (0 B) |
| `log_monitoring` | modules/log_monitoring | agentic_package | `stub_only` | `src/fsai_agents/modules/log_monitoring/README.md` (0 B) |
| `notion_automation` | modules/notion_automation | agentic_package | `stub_only` | `src/fsai_agents/modules/notion_automation/README.md` (0 B) |
| `rag_chatbot` | modules/rag_chatbot | agentic_package | `stub_only` | `src/fsai_agents/modules/rag_chatbot/README.md` (0 B) |
