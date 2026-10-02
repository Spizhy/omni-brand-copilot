import re
from typing import List
from app.models.schemas import ChannelPost, ChannelType
from app.providers.base import BaseContentLLMProvider


class MockContentLLMProvider(BaseContentLLMProvider):
    def generate_multi_channel(
        self,
        source_text: str,
        target_channels: List[ChannelType]
    ) -> List[ChannelPost]:
        posts: List[ChannelPost] = []

        # Extract a short hook from source
        first_line = source_text.strip().splitlines()[0] if source_text else "New Product Release"
        clean_headline = re.sub(r"^[#\s]+", "", first_line)[:70]

        channels = target_channels or [
            "TWITTER_THREAD",
            "LINKEDIN_POST",
            "NEWSLETTER_DIGEST",
            "EXECUTIVE_ANNOUNCEMENT"
        ]

        if "TWITTER_THREAD" in channels:
            tweet_1 = f"1/3 🚀 Today we are introducing {clean_headline}. Here is what we built, why it matters, and how it accelerates your engineering workflow 🧵👇"
            tweet_2 = "2/3 By automating routine data reconciliation and incident triage, teams recover an average of 14 hours per engineer every month. Tested in real production pipelines with zero downtime."
            tweet_3 = "3/3 Ready to explore? Read the full engineering breakdown and open documentation here: https://example.com/blog/release-notes #Engineering #DevOps #Automation"
            content = f"{tweet_1}\n\n{tweet_2}\n\n{tweet_3}"
            posts.append(ChannelPost(
                channel="TWITTER_THREAD",
                title=f"Twitter Thread: {clean_headline}",
                content=content,
                character_count=len(content),
                tags=["Engineering", "DevOps", "Automation"]
            ))

        if "LINKEDIN_POST" in channels:
            content = (
                f"We just published our latest technical update: {clean_headline}.\n\n"
                f"For the past six months, our engineering and operations teams focused on one fundamental objective: "
                f"eliminating manual bottlenecks in mission-critical workflows.\n\n"
                f"Key Takeaways:\n"
                f"• Automated reconciliation with strict mathematical validation.\n"
                f"• Sub-minute incident triage directly linked to local code AST.\n"
                f"• Full compatibility across enterprise environments with zero external lock-in.\n\n"
                f"What manual processes is your team actively automating this quarter? I'd love to hear your thoughts in the comments.\n\n"
                f"Read the full story: https://example.com/blog\n\n"
                f"#SoftwareEngineering #DevOps #ProcessAutomation #TechLeadership"
            )
            posts.append(ChannelPost(
                channel="LINKEDIN_POST",
                title=f"LinkedIn Update: {clean_headline}",
                content=content,
                character_count=len(content),
                tags=["SoftwareEngineering", "DevOps", "ProcessAutomation"]
            ))

        if "NEWSLETTER_DIGEST" in channels:
            content = (
                f"## 📬 Engineering Monthly Digest: {clean_headline}\n\n"
                f"Welcome back to our monthly architectural deep dive! In this issue, we examine our new automation release.\n\n"
                f"### What Changed?\n"
                f"{source_text[:350]}...\n\n"
                f"### Why It Matters For Teams\n"
                f"- High reliability with zero-dependency mock modes for local development.\n"
                f"- Strict schema validation preventing downstream data corruption.\n"
                f"- Instant deployability via Docker and automated CI pipelines.\n\n"
                f"Until next month,\n"
                f"The Engineering Team"
            )
            posts.append(ChannelPost(
                channel="NEWSLETTER_DIGEST",
                title=f"Newsletter: {clean_headline}",
                content=content,
                character_count=len(content),
                tags=["Newsletter", "EngineeringDigest"]
            ))

        if "EXECUTIVE_ANNOUNCEMENT" in channels:
            content = (
                f"Subject: Product & Engineering Milestone: {clean_headline}\n\n"
                f"Team & Stakeholders,\n\n"
                f"I am pleased to share that our team has successfully deployed our latest automation initiative.\n\n"
                f"Strategic Value:\n"
                f"1. Operational Efficiency: Reduces manual review cycles by over 60%.\n"
                f"2. Risk Mitigation: Enforces brand guardrails and mathematical verification at every step.\n"
                f"3. Time to Value: Fully containerized and verified across our core infrastructure.\n\n"
                f"Detailed technical documentation and rollout schedules are now accessible internally.\n\n"
                f"Regards,\nVP of Engineering"
            )
            posts.append(ChannelPost(
                channel="EXECUTIVE_ANNOUNCEMENT",
                title=f"Executive Brief: {clean_headline}",
                content=content,
                character_count=len(content),
                tags=["ExecutiveUpdate", "CompanyMilestone"]
            ))

        return posts
