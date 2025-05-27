import fasttext
import xml.etree.ElementTree as ET
import langcodes
import numpy as np
from dataclasses import dataclass
from typing import List
import csv
import sys
import json
import os

@dataclass
class Config:
    resourcePath: str
    outputPath: str
    language: str

@dataclass
class StringTag:
    text: str
    name: str

@dataclass
class TranslationResult:
    text: str
    language: str
    confidence: str

@dataclass
class CSVOutput:
    text: str
    name: str
    language: str
    confidence: str


def get_model_path() -> str:
    filename = "lid.176.ftz"
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running as plain Python script
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "models", filename)

model_path = get_model_path()
model = fasttext.load_model(model_path)

def load_config(path="config.json") -> Config:
    print(f"Loading config file from {path}")
    if not os.path.exists(path):
        print("Config file not found!")
        sys.exit(1)

    try:
        with open(path, "r") as f:
            config = json.loads(f.read())
    except json.JSONDecodeError:
        print("Config file is not valid JSON!")
        sys.exit(1)

    resourcePath = config.get("resourcePath")
    if resourcePath is None:
        print("'resourcePath' is missing in the config file!")
        sys.exit(1)

    if not os.path.exists(resourcePath):
        print(f"{resourcePath} does not exist!")
        sys.exit(1)
    
    outputPath = config.get("outputPath")
    if outputPath is None:
        print("'outputPath' is missing in the config file! Defaulting to the current directory")
        outputPath = "./output.csv"

    language = config.get("language", "English")

    return Config(resourcePath, outputPath, language)

def parse_xml(file_path: str) -> List[StringTag]:
    print(f"Parsing string resource xml from {file_path}")
    def get_all_text(elem) -> str:
        return ''.join(elem.itertext())
    
    tree = ET.parse(file_path)
    root = tree.getroot()

    result: List[StringTag] = []
    for child in root.findall("string"):
        if child.attrib.get("translatable") == False:
            print(f"Skipping elements with 'translatable=false'")
            continue
        if get_all_text(child) is None or get_all_text(child).strip() == "":
            child_name = child.attrib.get("name")
            print(f"Skipping empty text - <string name='{child_name}'>{get_all_text(child)}</string>")
            continue

        processed_text = get_all_text(child).replace("\n", " ").strip()
        result.append(
            StringTag(
                processed_text, 
                child.attrib.get("name")
            )
        )
    return result

def check_translations(text: str) -> TranslationResult:
    label, raw_confidence = model.predict(text)
    confidence: str = f"{np.asarray(raw_confidence)[0] * 100:.2f}%"
    language_code = label[0].replace("__label__", "")
    language_name = langcodes.get(language_code).language_name()

    return TranslationResult(text,language_name,confidence)

def get_csv_output(tags: List[StringTag]) -> List[CSVOutput]:
    print(f"Creating csv format output...")
    csvOutput: List[CSVOutput] = []
    for tag in tags:
        translationResult = check_translations(tag.text)
        csvOutput.append(
            CSVOutput(
                text = tag.text,
                name = tag.name,
                language = translationResult.language,
                confidence = translationResult.confidence
            )
        )
    
    return csvOutput

def write_csv_file(outputPath: str, csv_output: List[CSVOutput]):
    print(f"Writing to csv file -> {outputPath}")
    with open(outputPath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Text", "Language", "Confidence"])
        for word in csv_output:
            writer.writerow([word.name, word.text, word.language, word.confidence])

    print("Output created!")

def main():
    # 1. Load config
    config: Config = load_config()

    # 2. Parse XML
    tags: List[StringTag] = parse_xml(config.resourcePath)

    # 3. Check translations and transform to csv output format
    csvOutput: List[CSVOutput] = get_csv_output(tags)

    # 4. Filter output
    filtered_output: List[CSVOutput] = list(filter(lambda c: c.language.lower() != config.language.lower(), csvOutput))

    # 5. Sort by descending order - Highest confidence first
    sorted_output: List[CSVOutput] = sorted(filtered_output, key=lambda c: c.confidence, reverse=True)

    # 6. Write to csv file
    write_csv_file(config.outputPath, sorted_output)

if __name__ == "__main__":
    main()