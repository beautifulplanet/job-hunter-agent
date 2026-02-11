import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import JobHunter

JD_TEXT = """
AI Deployment Engineer @ OpenAI
Location: New York, NY (Hybrid - 3 days/week in office)
Company: OpenAI

About the team:
The AI Deployment Engineering team ensures the safe and effective deployment of Generative AI applications for developers and enterprises. We act as trusted advisors and technical partners to our customers, helping them build and execute their AI adoption strategy post-sale. Our mission is to develop a strong backlog of GenAI use cases tailored to each customer's industry and to drive these initiatives from prototype to production through hands-on technical guidance and partnership.

As an AI Deployment Engineer, you will help customers across various industries transform their businesses through applications such as customer service automation, content generation, and entirely new offerings powered by our most advanced models.

About the role:
We are looking for a solutions-oriented technical leader to engage with customers post-sale and ensure they realize tangible business value from their investment in OpenAI's technologies. You will work closely with senior leaders and technical teams within customer organizations to establish GenAI roadmaps, strategies, prioritize high-value use cases, and guide projects from early prototyping through enterprise-grade production deployments.

You will take a holistic view of each customer's architecture and operations, designing solutions that leverage ChatGPT, OpenAI APIs, and our broader ecosystem of tools and services. You will work cross-functionally with Sales, Solutions Engineering, Applied Research, and Product teams, and report to the Head of Solutions Architecture for your segment.

In this role, you will:
- Serve as the primary technical subject matter expert post-sale for a portfolio of customers, embedding deeply with them to design and deploy GenAI solutions.
- Engage with senior business and technical stakeholders to identify, prioritize, and validate the highest-value GenAI applications in their roadmap.
- Accelerate customer time to value by providing architectural guidance, building hands-on prototypes, and advising on best practices for scaling solutions in production.
- Maintain strong relationships with leadership and technical teams to drive adoption, expansion, and successful outcomes.
- Contribute to open-source resources and enterprise-facing technical documentation to scale best practices across customers.
- Share learnings and collaborate with internal teams to inform product development and improve customer outcomes.
- Codify knowledge and operationalize technical success practices to help the Solutions Architecture team scale impact across industries and customer types.

You'll thrive in this role if you:
- Have 5+ years of technical consulting, post-sales engineering, solutions architecture, or similar experience working directly with customers.
- Are a strong communicator, able to explain technical and business concepts clearly to executive and practitioner audiences alike.
- Have experience leading complex deployments of Generative AI or traditional machine learning systems, ideally including infrastructure and network architecture considerations.
- Possess hands-on proficiency in languages like Python, JavaScript, or similar, and are comfortable building prototypes or proofs of concept.
- Take end-to-end ownership of challenges, proactively acquiring new skills or knowledge as needed to drive success.
- Bring a humble, collaborative mindset and an eagerness to support teammates and customers alike.
- Thrive in fast-paced environments, adeptly managing multiple workstreams and prioritizing for the highest customer impact.
"""

def run():
    hunter = JobHunter()
    
    print("Generating Master Prompt for OpenAI AI Deployment Engineer role...")
    prompt = hunter.prepare_resume_prompt(JD_TEXT)
    
    # Save the prompt to a file so user can easily copy it
    output_path = os.path.join(os.path.dirname(__file__), "output", "openai_prompt.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print(f"\nPrompt saved to: {output_path}")
    print(f"Prompt length: {len(prompt)} characters")
    print(f"PII scrub report:")
    print(hunter.scrubber.get_report())

if __name__ == "__main__":
    run()
