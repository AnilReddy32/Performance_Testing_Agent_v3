import xml.etree.ElementTree as ET

from app.tools.artifact_generator import ArtifactGenerator


generator = ArtifactGenerator()

prompt = generator._build_prompt(
    tool="jmeter",
    application="Internet Banking",
    scenario="UPI Payment",
    api_name="/api/v1/payment",
)

response = generator.client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.2,
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert performance testing engineer. "
                "Generate valid performance-testing artifacts "
                "for the requested tool and format."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ],
)

content = response.choices[0].message.content or ""
content = content.strip()

print("STARTS XML:", content.startswith("<?xml"))
print(
    "STARTS JMETER:",
    content.startswith("<jmeterTestPlan"),
)

print("HAS ROOT:", "<jmeterTestPlan" in content)
print("HAS HASH:", "<hashTree" in content)
print("HAS TESTPLAN:", "<TestPlan" in content)
print("HAS THREADGROUP:", "<ThreadGroup" in content)
print(
    "HAS HTTP SAMPLER:",
    "<HTTPSamplerProxy" in content,
)

print(
    "PUBLIC CLASS:",
    "public class" in content,
)

print(
    "JMETER JAVA:",
    "import org.apache.jmeter" in content,
)

print(
    "ORG JMETER:",
    "org.apache.jmeter" in content,
)

print(
    "CODE FENCE:",
    "```" in content,
)

print(
    "HASH OPEN:",
    content.count("<hashTree"),
)

print(
    "HASH CLOSE:",
    content.count("</hashTree>"),
)

print(
    "ROOT OPEN:",
    content.count("<jmeterTestPlan"),
)

print(
    "ROOT CLOSE:",
    content.count("</jmeterTestPlan>"),
)

print("XML PARSE:", end=" ")

try:
    root = ET.fromstring(content)
    print("OK")

    print("ROOT TAG:", root.tag)

    print(
        "TESTPLAN:",
        root.find(".//TestPlan") is not None,
    )

    print(
        "THREADGROUP:",
        root.find(".//ThreadGroup") is not None,
    )

    print(
        "HTTP:",
        root.find(".//HTTPSamplerProxy") is not None,
    )

except ET.ParseError as error:
    print("FAILED")
    print("XML ERROR:", error)

print()
print("--- FIRST 3000 CHARACTERS ---")
print(content[:3000])
print("--- END ---")
