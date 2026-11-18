# Share and use this skill

This folder is a reusable Codex skill. It guides an agent to implement and deploy a publisher for the recipient's own account. It is not a standalone runnable app and does not include the original owner's credentials, video files or publishing database.

Unzip the package, then copy the `instagram-reels-cloud-publisher` folder into `~/.codex/skills/` (or your configured Codex skills directory). Reload Codex if it does not appear immediately.

Start with:

> Use $instagram-reels-cloud-publisher to build my Instagram Reels publisher using Meta Graph API and GitHub Actions. Publish one video daily at 7 PM Asia/Kolkata, use free captions, and keep my source videos and other schedules unchanged. Inspect my environment first. Do not publish or activate until I authorize it.

Tell the agent your desired account, source folder, timezone, time and GitHub repository visibility. Enter Meta credentials only through a protected local file or secure local prompt. A professional Instagram account, an eligible Meta app with the appropriate permissions, and GitHub authorization are required; the agent should verify current requirements.

Public repository/Release hosting makes uploaded videos accessible to everyone. Choose visibility deliberately. GitHub schedules can be delayed. Videos must already be synchronized for posting while your computer is off. Free captions are topic-based templates; paid AI caption generation is optional.

The skill authorizes no actions on behalf of its original creator. Every recipient uses their own account, history and permissions.
