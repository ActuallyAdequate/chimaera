from collections import OrderedDict
from pathlib import Path
from ssl import TLSVersion
from typing import cast
import yaml
import pandas as pd
import os
import re
import argparse
import json

BodyPart = dict[str, str | list[str]]


# Function to convert YAML data to CSV
def load_body_parts(yaml_file: Path):

    # Load the YAML file
    with open(yaml_file, "r") as file:
        data_dict: dict[str, list[BodyPart]] = yaml.safe_load(file) or {}

    # Extract body_parts section
    body_parts: list[BodyPart] = data_dict.get("body_parts", [])

    return body_parts


###################################################################################
# Generate Body Part TSV
##################################################################################
def generate_body_parts_tsv(body_parts: list[BodyPart], output_tsv: Path):

    # Create DataFrame
    body_parts_df: pd.DataFrame = pd.json_normalize(body_parts)

    if "activated_abilities" in body_parts_df.columns:
        activated = body_parts_df["activated_abilities"].apply(pd.Series)
        activated = activated.rename(columns=lambda x: f"activated_ability{int(x)+1}")
        body_parts_df = pd.concat(
            [body_parts_df.drop(columns=["activated_abilities"]), activated], axis=1
        )

    if "passive_abilities" in body_parts_df.columns:
        passive = body_parts_df["passive_abilities"].apply(pd.Series)
        passive = passive.rename(columns=lambda x: f"passive_ability{int(x)+1}")
        body_parts_df = pd.concat(
            [body_parts_df.drop(columns=["passive_abilities"]), passive], axis=1
        )

    body_parts_df = body_parts_df.fillna("")

    # Write File
    body_parts_df.to_csv(output_tsv, index=False, sep="\t")
    print(f"Data successfully written to {output_tsv}")


###################################################################################
# Rule Standards Regex
###################################################################################
def compile_dynamic_regex(standards, output_folder):
    glossary = standards["glossary"]
    templates = standards["templates"]
    compiled_rules = OrderedDict()
    raw_rules = {}

    replacements = {k: f"(?:{'|'.join(v)})" for k, v in glossary.items()}
    for rule_name, template in templates.items():
        # Inject the joined strings into the curly braces in the template
        formatted_regex = template.format(**replacements)

        # Collect Raw rules
        raw_rules[rule_name] = formatted_regex
        # Compile for use in your report script
        compiled_rules[rule_name] = re.compile(formatted_regex, re.IGNORECASE)

    with open(f"{output_folder}/regexes.txt", "w") as regex_file:
        json.dump(raw_rules, regex_file, indent=4)

    return compiled_rules


###################################################################################
# Report Generation
###################################################################################
def generate_report(body_parts: list[BodyPart], output_file, rule_patterns):
    # Initialize dictionaries to store system stats and various condition stats
    total_body_parts = len(body_parts)
    ability_count: dict[int, list[str]] = {}
    system_stats: dict[str, list[str]] = {}
    ability_stats = {category: [] for category in rule_patterns.keys()}
    ability_stats["unknown"] = []
    # condition_stats = {"granted": {}, "ignored": {}}
    # injury_stats = {
    #    "additional_injury": [],
    #    "physical_injury": [],
    #    "internal_injury": [],
    #    "severed_injury": [],
    #    "obliterated_injury": [],
    # }

    for body_part in body_parts:
        system = cast(str, body_part.get("system", "Unknown"))
        title = cast(str, body_part.get("title", "Unnamed Body Part"))

        # Add the title to the appropriate system category
        system_stats.setdefault(system, []).append(title)

        active_abilities = cast(list[str], body_part.get("activated_abilities", []))
        passive_abilities = cast(list[str], body_part.get("passive_abilities", []))
        # Gather all abilities from both activated and passive abilities
        abilities = active_abilities + passive_abilities
        num_of_abilities = len(abilities)
        ability_count.setdefault(num_of_abilities, []).append(title)

        for ability in abilities:
            matched_category = None
            for category, pattern in rule_patterns.items():
                if pattern.match(ability.strip()):
                    matched_category = category
                    ability_stats.setdefault(category, []).append((title, ability))
            if not matched_category:
                ability_stats.setdefault("unknown", []).append((title, ability))
        # for ability in abilities:
        #    ability = ability.lower()
        #    # Determine if the ability grants or ignores the condition
        #    grants_condition = "ignore" not in ability
        #    match = re.search(r"(\w+)\s+condition", ability, re.IGNORECASE)
        #    if match:
        #        condition_type = match.group(1)
        #        condition_category = "granted" if grants_condition else "ignored"
        #        condition_stats[condition_category].setdefault(
        #            condition_type, []
        #        ).append(title)
        #
        #    # Check for specific injuries and keywords
        #    if re.search(r"physical injury", ability, re.IGNORECASE) and re.search(
        #        r"deal", ability, re.IGNORECASE
        #    ):
        #        injury_stats["physical_injury"].append(title)
        #    if re.search(r"internal injury", ability, re.IGNORECASE) and re.search(
        #        r"deal", ability, re.IGNORECASE
        #    ):
        #        injury_stats["internal_injury"].append(title)
        #    if re.search(r"injury", ability, re.IGNORECASE) and re.search(
        #        r"severed", ability, re.IGNORECASE
        #    ):
        #        injury_stats["severed_injury"].append(title)
        #    if re.search(r"injury", ability, re.IGNORECASE) and re.search(
        #        r"obliterated", ability, re.IGNORECASE
        #    ):
        #        injury_stats["obliterated_injury"].append(title)
        #    if re.search(r"additional injur", ability, re.IGNORECASE):
        #        injury_stats["additional_injury"].append(title)

    # Create report content
    report_content = []
    report_content.append(f"# Report for Body Parts\n")
    report_content.append("---\n\n")

    # Ability Counts
    report_content.append("## Body Part Statistics\n\n")
    report_content.append(f"Total Number of Body Parts: {total_body_parts}\n\n")
    report_content.append("### Ability Counts\n\n")
    for num, body_parts in ability_count.items():
        report_content.append(
            f"#### Body Parts With {num} Abilities: {len(body_parts)}\n"
        )
        for part in body_parts:
            report_content.append(f"- {part}")
        report_content.append("\n")

    # System statistics report
    report_content.append("### System Statistics\n")
    for system, body_parts in system_stats.items():
        report_content.append(
            f"#### Body Parts With System {system}: {len(body_parts)}"
        )
        for part in body_parts:
            report_content.append(f"- {part}")
        report_content.append("\n")

    report_content.append("## Ability Statistics")
    for category, abilities in ability_stats.items():
        report_content.append(f"### Body Parts With {category}: {len(abilities)}\n")
        for title, ability in abilities:
            report_content.append(f"- {title}")
            if category == "unknown":
                report_content.append(f"\t- {ability}")
        report_content.append("\n")

    # Condition statistics report
    # report_content.append("Condition Statistics:\n")
    # total_granted_condition_parts = sum(
    #    len(parts) for parts in condition_stats["granted"].values()
    # )
    # total_ignored_condition_parts = sum(
    #    len(parts) for parts in condition_stats["ignored"].values()
    # )

    # report_content.append(
    #    f"Total Body Parts Granting a Condition: {total_granted_condition_parts}\n"
    # )
    # for condition_type, body_parts in condition_stats["granted"].items():
    #    report_content.append(f"Condition Type (Granted): {condition_type}")
    #    report_content.append(f"Number of Body Parts: {len(body_parts)}")
    #    for part in body_parts:
    #        report_content.append(f" - {part}")
    #    report_content.append("\n")

    # report_content.append(
    #    f"Total Body Parts Ignoring a Condition: {total_ignored_condition_parts}\n"
    # )
    # for condition_type, body_parts in condition_stats["ignored"].items():
    #    report_content.append(f"Condition Type (Ignored): {condition_type}")
    #    report_content.append(f"Number of Body Parts: {len(body_parts)}")
    #    for part in body_parts:
    #        report_content.append(f" - {part}")
    #    report_content.append("\n")

    # Injury statistics report
    # report_content.append("Injury Statistics:\n")

    # Physical Injury
    # report_content.append(
    #    f"Body Parts that Deal Physical Injury: {len(injury_stats['physical_injury'])}"
    # )
    # for part in injury_stats["physical_injury"]:
    #    report_content.append(f" - {part}")
    # report_content.append("\n")

    # Internal Injury
    # report_content.append(
    #    f"Body Parts that Deal Internal Injury: {len(injury_stats['internal_injury'])}"
    # )
    # for part in injury_stats["internal_injury"]:
    #    report_content.append(f" - {part}")
    # report_content.append("\n")

    # Severed Injury
    # report_content.append(
    #    f"Body Parts that can Sever: {len(injury_stats['severed_injury'])}"
    # )
    # for part in injury_stats["severed_injury"]:
    #    report_content.append(f" - {part}")
    # report_content.append("\n")

    # Obliterated Injury
    # report_content.append(
    #    f"Body Parts that can Obliterate: {len(injury_stats['obliterated_injury'])}"
    # )
    # for part in injury_stats["obliterated_injury"]:
    #    report_content.append(f" - {part}")
    # report_content.append("\n")

    # Additional Injury
    # report_content.append(
    #    f"Body Parts That Deal 1 Additional Injury: {len(injury_stats['additional_injury'])}"
    # )
    # for part in injury_stats["additional_injury"]:
    #    report_content.append(f" - {part}")
    # report_content.append("\n")

    # Create the output report file

    # Write the report to a text file
    try:
        with open(output_file, "w") as report_file:
            report_file.write("\n".join(report_content))
        print(f"Report successfully written to {output_file}")
    except IOError as e:
        print(f"An error occurred while writing the report: {e}")


###################################################################################
# Main script
###################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert YAML file to CSV and generate a system report."
    )
    _ = parser.add_argument("body_parts_yaml", help="Path to the input YAML file")
    _ = parser.add_argument(
        "rule_standards_yaml", help="Path to Rule Standard Yaml File"
    )
    _ = parser.add_argument(
        "output_folder",
        help="Path to the folder where the CSV and report should be saved",
    )

    args = parser.parse_args()

    body_parts_file = cast(Path, args.body_parts_yaml)
    rules_standards_file = cast(Path, args.rule_standards_yaml)
    output_folder = cast(Path, args.output_folder)

    # Ensure output folder exists
    if not os.path.exists(cast(Path, args.output_folder)):
        os.makedirs(cast(Path, args.output_folder))
    body_parts_filename = os.path.basename(body_parts_file)
    output_tsv = f"{output_folder}/{body_parts_filename}.tsv"

    # Run the conversion to CSV and return the entries
    body_parts = load_body_parts(body_parts_file)

    generate_body_parts_tsv(body_parts, output_tsv)

    with open(rules_standards_file, "r") as f:
        data = yaml.safe_load(f)

    rule_patterns = compile_dynamic_regex(data, output_folder)

    # Generate a report based on the processed entries
    output_report = f"{output_folder}/{body_parts_filename}_report.md"
    generate_report(body_parts, output_report, rule_patterns)
